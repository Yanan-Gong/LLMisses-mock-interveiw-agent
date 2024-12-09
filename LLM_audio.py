import json
from openai import OpenAI
from pydantic import BaseModel
from typing import Optional
import inspect
from dotenv import load_dotenv
import os
import sounddevice as sd
from scipy.io.wavfile import write
import whisper
import tempfile
import warnings
warnings.filterwarnings("ignore", category=FutureWarning, module="whisper")


os.chdir("C:/Users/chloe/Documents/LLM/LLMisses")
print("Current Working Directory:", os.getcwd())
# Load environment variables from .env file

env_path = "C:/Users/chloe/Documents/LLM/LLMisses/.env"
print("Does .env exist?", os.path.exists(env_path))

# Read the file's content directly (for debugging only)
if os.path.exists(env_path):
    with open(env_path, "r") as f:
        print("Contents of .env file:")
        print(f.read())

load_dotenv("C:/Users/chloe/Documents/LLM/LLMisses/.env")

# Fetch sensitive values
api_key = os.getenv('OPENAI_API_KEY')
organization = os.getenv('OPENAI_ORGANIZATION')
# project = os.getenv('OPENAI_PROJECT')

print("API Key:", api_key)
print("Organization:", organization)
# print("Project:", project)

# if not api_key or not organization or not project:
if not api_key or not organization:    
    raise ValueError("Missing one or more required environment variables: OPENAI_API_KEY, OPENAI_ORGANIZATION, OPENAI_PROJECT")

# Initialize OpenAI client
client = OpenAI(
    api_key=api_key,
    organization=organization,
    # project=project
)

# class to define the agent and response, you can change desired models in each agent
class Agent(BaseModel):
    name: str = "Agent"
    model: str = "gpt-4o-mini"
    instructions: str = "You are a helpful Agent"
    tools: list = []

class Response(BaseModel):
    agent: Optional[Agent]
    messages: list




# Load the Whisper model
model = whisper.load_model("base")  # Choose the model size based on your requirements.
# Function to record audio
def record_audio(filename: str, duration: int = 5, sample_rate: int = 44100):
    print(f"Recording for {duration} seconds...")
    audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='int16')
    sd.wait()  # Wait until recording is finished
    write(filename, sample_rate, audio_data)  # Save as a WAV file
    if os.path.exists(filename):
        print(f"Recording saved to {filename}")
    else:
        print(f"Error: File {filename} was not created.")

# Function to transcribe audio from the microphone
def transcribe_audio_from_microphone():
    temp_audio_path = os.path.join(tempfile.gettempdir(), "temp_audio.wav")
    try:
        record_audio(temp_audio_path)  # Record audio
        if not os.path.exists(temp_audio_path):
            print("Error: Temporary audio file not found.")
            return ""

        print(f"Temp audio path exists before transcription: {os.path.exists(temp_audio_path)}")
        if os.stat(temp_audio_path).st_size == 0:
            print("Error: The audio file is empty.")
            return ""

        # Check file content
        with open(temp_audio_path, 'rb') as f:
            print(f"Temporary audio file size: {len(f.read())} bytes")
        
        print(f"Attempting to transcribe file: {temp_audio_path}")
        result = model.transcribe(temp_audio_path)  # Transcribe audio
        return result["text"]
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return ""
    except Exception as e:
        print(f"Error transcribing audio: {e}")
        return ""
    finally:
        if os.path.exists(temp_audio_path):
            print(f"Temporary file {temp_audio_path} exists for cleanup.")
            os.remove(temp_audio_path)  # Cleanup
            print(f"Temporary file {temp_audio_path} deleted.")



# Main Execution
if __name__ == "__main__":
    print("Press Enter to start recording...")
    input()  # Wait for user input to begin recording
    transcription = transcribe_audio_from_microphone()
    if transcription:
        print("Transcription Result:", transcription)
    else:
        print("Failed to transcribe audio. Try again.")

# Helper functions
# This function converts a Python function to a schema that can be used by OpenAI's Chat API.
def function_to_schema(func) -> dict:
    type_map = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
        list: "array",
        dict: "object",
        type(None): "null",
    }

    try:
        signature = inspect.signature(func)
    except ValueError as e:
        raise ValueError(
            f"Failed to get signature for function {func.__name__}: {str(e)}"
        )

    parameters = {}
    for param in signature.parameters.values():
        try:
            param_type = type_map.get(param.annotation, "string")
        except KeyError as e:
            raise KeyError(
                f"Unknown type annotation {param.annotation} for parameter {param.name}: {str(e)}"
            )
        parameters[param.name] = {"type": param_type}

    required = [
        param.name
        for param in signature.parameters.values()
        if param.default == inspect._empty
    ]

    return {
        "type": "function",
        "function": {
            "name": func.__name__,
            "description": (func.__doc__ or "").strip(),
            "parameters": {
                "type": "object",
                "properties": parameters,
                "required": required,
            },
        },
    }

## Helper function to execute tool calls
def execute_tool_call(tool_call, tools, agent_name):
    name = tool_call.function.name
    args = json.loads(tool_call.function.arguments)

    print(f"{agent_name}:", f"{name}({args})")

    return tools[name](**args)  # call corresponding function with provided arguments


def bq_question_answer(agent, messages):
    current_agent = agent
    num_init_messages = len(messages)
    messages = messages.copy()

    while True:
        tool_schemas = [function_to_schema(tool) for tool in current_agent.tools]
        tools = {tool.__name__: tool for tool in current_agent.tools}

        response = client.chat.completions.create(
            model=current_agent.model,
            messages=[{"role": "system", "content": current_agent.instructions}] + messages,
            tools=tool_schemas or None,
        )
        message = response.choices[0].message
        messages.append(message)

        if message.content:
            print(f"{current_agent.name}:", message.content)

        if not message.tool_calls:
            break

        for tool_call in message.tool_calls:
            # Access tool call properties
            tool_name = getattr(tool_call.function, "name", None)
            tool_args = json.loads(getattr(tool_call.function, "arguments", "{}"))
            tool_call_id = getattr(tool_call, "id", None)

            if not tool_name:
                print("Warning: Tool name not found in tool_call.")
                continue
            print(f"Executing tool: {tool_name} with arguments: {tool_args}") 
            if tool_name in tools:
                # Execute the tool
                tool_result = tools[tool_name](**tool_args)

                # Display evaluation details from Evaluation Agent
                # if tool_name == "evaluate_feedback":
                #     print("\n--- Evaluation Agent Output ---")
                #     print(f"Original Feedback: {tool_result['original_feedback']}")
                #     print(f"Refined Feedback: {tool_result['refined_feedback']}")
                #     print(f"Suggestions: {tool_result['suggestions']}")
                #     print("------------------------------\n")

                # Prepare tool response
                tool_response_content = (
                    {
                        "name": tool_result.name,
                        "model": tool_result.model,
                        "instructions": tool_result.instructions,
                        "tools": [tool.__name__ for tool in tool_result.tools],
                    }
                    if isinstance(tool_result, Agent)
                    else tool_result
                )

                # Append tool response message
                tool_response_message = {
                    "role": "tool",
                    "tool_call_id": tool_call_id,
                    "content": json.dumps(tool_response_content),
                }
                messages.append(tool_response_message)
            else:
                print(f"Tool {tool_name} not found for agent {current_agent.name}.")
                continue

            # Handle agent switching
            if isinstance(tool_result, Agent):
                print(f"Switching to {tool_result.name}...")
                current_agent = tool_result
                break  # Restart loop with new agent

    return Response(agent=current_agent, messages=messages[num_init_messages:])





### Transfer functions ###
def transfer_to_user_info_extract_agent():
    return user_info_extract_agent

def transfer_to_bq_question_generator():
    return bq_question_generator_agent

def transfer_to_feedback_agent():
    return feedback_agent

def transfer_to_eval_agent():
    return evaluation_agent

def transfer_to_bq_mock_interview_agent():
    return bq_mock_interview_agent

###  Agent functions and corresponding tools ###
### You can change the input parameters as you like. As long as this input information can be captured in the conversation
### Here I use job_title as the input parameter, you can change to other parameters like experience_years, skills, etc.
def extract_resume_jd(job_title):
    """
    Extracts the experience and job requirments from given resume and job description
    """
    return "success"

# Agent1
user_info_extract_agent = Agent(
    name="User Info Extractor",
    instructions=("You are a helpful assistant who can extract user information from text.\n" "Introduce yourself. Always be very brief. " "1. please summarize the job description." 
"2. please summerize resume focusing on relevant past experience."),
    tools=[extract_resume_jd,transfer_to_bq_question_generator,transfer_to_bq_mock_interview_agent],)

# --------------------------------------------------------#

def bq_question_generator(job_title):
    """
    based on user's info, generates 6 differnect behavior questions for the interview
    """
    return "success"

# Agent2
bq_question_generator_agent = Agent(
    name="Behavior Question Generator",
    instructions=("You are a helpful assistant who can generate 5-10 behavior questions based on the Job Description Summary and Resume Summary from user_info_extract_agent .\n" 
                  "Introduce yourself. Always be very brief. "
                  "Dont not provide answers to the questions."),
    tools=[bq_question_generator,transfer_to_feedback_agent,transfer_to_bq_mock_interview_agent],)

# --------------------------------------------------------#
def evaluate_answers(job_title):
    """
    Evaluate the answers provided by the user. 
    """
    return "success"

# Agent3
feedback_agent = Agent(
    name="Feedback Agent",
    instructions=( "You are a mock interview agent designed to assist users in improving their responses to interview questions. "
        "Your primary responsibilities are: \n\n"
        "1. Introducing yourself as a professional mock interview tutor. \n"
        "2. Collecting behavioral interview questions (BQ) from the `bq_question_generator_agent` and presenting them to the user one at a time. \n"
        "3. After receiving the user's answers, evaluate their responses systematically. Ensure the evaluation process follows these steps: \n"
        "   - Analyze the question, extract keywords, and ensure a clear understanding of its intent. \n"
        "   - Assess the user's answer to determine alignment with the keywords, relevance to the question, and suitability based on the user's experience level and the role they are applying for. \n"
        "   - Use the following considerations when tailoring feedback: \n"
        "      a. For entry-level roles: Focus on potential, transferable skills, and foundational knowledge. \n"
        "      b. For mid-level roles: Emphasize demonstrated experience, results achieved, and team contributions. \n"
        "      c. For senior roles: Highlight leadership, strategic thinking, and high-impact achievements. \n"
        "      d. Align feedback with the specific skills, responsibilities, and expectations of the target role. \n"
        "   - Apply the STAR (Situation, Task, Action, Result) framework to evaluate the structure and depth of the response. \n"
        "4. Generate detailed feedback for each answer, including: \n"
        "   - Strengths: Highlight well-structured and relevant parts of the response. \n"
        "   - Weaknesses: Identify areas that need improvement, especially as they relate to the user's experience level and role expectations. \n"
        "   - Suggestions: Provide actionable advice for refining the answer, considering the skills and competencies expected at the user's experience level and the role they are applying for. \n"
        "   - Modified Answer: Present an improved version of the user’s response based on the feedback and the context of their experience level and target role. \n\n"
        "5. Collaborate with the `Evaluation Agent` to further refine your feedback. Incorporate their insights to enhance your analysis and suggestions for current and future responses. \n"
        "6. Present the final refined feedback to the user using the following structure: \n"
        "   - **Question**: [The question provided to the user] \n"
        "   - **User Answer**: [The original response from the user] \n"
        "   - **Strengths**: [Highlight positive aspects] \n"
        "   - **Weaknesses**: [Identify areas of improvement] \n"
        "   - **Suggestions**: [Provide actionable suggestions] \n"
        "   - **Modified Answer**: [Present the refined answer] \n\n"
        "7. Once the process is complete, transfer control back to the `bq_mock_interview_agent`. \n\n"
        "Guidelines: \n"
        "- Always consider the user's experience level and the role they are applying for when generating feedback. \n"
        "- Maintain professionalism throughout the interaction. \n"
        "- Do not provide hints or direct answers unless evaluating or refining the user’s response. \n"
        "- Adapt to feedback from the `Evaluation Agent` to continuously improve the quality of your assessments."

  ),
    tools=[evaluate_answers,transfer_to_eval_agent],
)
# --------------------------------------------------------#
def evaluate_feedback(feedback: str) -> dict:
    """
    Evaluate the feedback provided by the feedback_agent.

    Args:
        feedback (str): The feedback provided by the feedback_agent.

    Returns:
        dict: A dictionary containing the refined feedback and suggestions for improvement.
    """
    print(f"Input Feedback to Evaluation Agent: {feedback}")  # Debug input
    # Example evaluation logic
    refined_feedback = f"Refined feedback: {feedback.strip()}. Make it clearer, more relevant to the question asked, more professional, and more actionable."
    suggestions = "Focus on being concise and providing examples to justify the evaluation."
    
    result = {
        "original_feedback": feedback,
        "refined_feedback": refined_feedback,
        "suggestions": suggestions
    }
    print(f"Evaluation Agent Output: {result}")  # Debug output
    return result
    

#Agent4: Agent to evaluate the feedback from feedback agent
evaluation_agent = Agent(
    name="Evaluation Agent",
    instructions=(
        "You are an independent Evaluation Agent tasked with assessing the feedback provided by the Feedback Agent. "
        "Your primary objective is to ensure that the feedback thoroughly addresses the user's improvement needs and provides actionable suggestions. "
        "Additionally, ensure that the feedback properly considers the user's work experience and the role they are applying for. "
        "Your responsibilities include: \n\n"
        "1. **Understanding the Question**: Analyze the question to clarify what kind of response an interviewer would expect. \n"
        "2. **Reviewing the User’s Answer**: Consider the user's answer to evaluate its relevance and alignment with the question. \n"
        "3. **Assessing Feedback from the Feedback Agent**: \n"
        "   - Focus on evaluating the feedback provided by the Feedback Agent, not the user’s answer itself. \n"
        "   - Verify whether the feedback explicitly checks the relevance of the user’s answer to the question by analyzing the keywords and intent of the question. \n"
        "   - Ensure that the feedback checks whether the user's response is appropriate for their experience level and the position they are applying for. For example, ask: \n"
        "     - **Is this answer strong enough for someone with the user’s previous work experience?** \n"
        "     - **Does this answer meet the expectations for the position the user is applying for?** \n"
        "     - **Does the feedback align with the job description or role expectations?** \n"
        "   - If the user’s answer is irrelevant but the feedback fails to address this, emphasize it in your evaluation to ensure such omissions are avoided in the future. \n"
        "   - Confirm that the feedback effectively utilizes the STAR (Situation, Task, Action, Result) method, addressing each component clearly. \n"
        "4. **Enhancing Feedback**: Refine and improve the feedback provided by the Feedback Agent, ensuring it is: \n"
        "   - **Comprehensive**: Covers all aspects of the user’s answer in relation to the question. \n"
        "   - **Actionable**: Provides specific, clear, and practical suggestions for improvement based on the user’s experience and role. \n"
        "   - **Relevant**: Ensures the feedback is tailored to the user’s experience level (entry-level, mid-level, senior) and the role they are applying for. \n"
        "5. **Providing Detailed Feedback to the Feedback Agent**: \n"
        "   - Highlight strengths in the Feedback Agent’s analysis. \n"
        "   - Identify weaknesses or omissions in the feedback, especially regarding the user’s experience level or role expectations. \n"
        "   - Suggest specific ways to enhance future evaluations, including ensuring greater alignment with the user’s background and job position. \n\n"
        "6. **Delivering Your Evaluation**: Structure your output as follows: \n"
        "   - **Refined Feedback**: Provide an improved version of the feedback based on the user’s answer and the original feedback from the Feedback Agent. \n"
        "   - **Strengths**: Highlight the best aspects of the feedback provided. \n"
        "   - **Weaknesses**: Identify areas where the feedback fell short or missed key points, particularly in relation to the user's experience and target position. \n"
        "   - **Suggestions**: Offer actionable advice to help the Feedback Agent improve its future evaluations. \n\n"
        "Guidelines: \n"
        "- Always ensure clarity and professionalism in your evaluation. \n"
        "- Focus on helping the Feedback Agent refine its approach while providing actionable suggestions. \n"
        "- Collaborate effectively with the Feedback Agent to foster continuous improvement in evaluating user responses. \n\n"
        "Note: You are not responsible for directly evaluating the user’s answer but for ensuring the feedback provided by the Feedback Agent is robust, actionable, and aligned with the question’s intent, the user’s experience, and the role they are targeting."
    ),
    tools=[evaluate_feedback, transfer_to_feedback_agent, transfer_to_bq_mock_interview_agent]
)

# Agent5: Manager Agent to control the whole process
bq_mock_interview_agent = Agent(
    name="BQ Mock Interview Agent",
    instructions=("You are a helpful assistant who can guide the user through a mock interview process."
                  "Introduce yourself. Always be very brief. "
                  "Gather information from users and lead them into the next step."
                  "1. Extract user information from text."
                  "2. Generate behavior questions based on the job description and resume."
                  "3. Provide feedback on the user's answers."
                  "4. Evaluate the feedback and further refine both user's answer and your previous feedback, try to learn to improve the performance"
                  "5. Wrap up the mock interview based on the feedback from feedback_agent. providing suggestions."),
    tools=[transfer_to_user_info_extract_agent,transfer_to_bq_question_generator,transfer_to_feedback_agent,transfer_to_eval_agent],
)



# ----------------- Main -----------------#
agent = bq_mock_interview_agent
messages = []

print("Welcome to the mock interview process! Please input your resume and job description.")
while True:
    user_input_mode = input("How would you like to provide input? (1: Text, 2: Audio, 'quit' to exit): ").strip().lower()
    
    if user_input_mode == 'quit':
        print("Exiting the interview process. Goodbye!")
        break
    
    if user_input_mode == '1':  # Text input mode
        user = input("User: ").strip()

    elif user_input_mode == '2':  # Audio input mode
        user = transcribe_audio_from_microphone()
        if user:
            print(f"You said: {user}")
        else:
            print("Failed to transcribe audio. Try again.")
            continue

    # Append user input to the conversation
    messages.append({"role": "user", "content": user})
    
    # Generate and display the AI's response
    response = bq_question_answer(agent, messages)
    agent = response.agent
    messages.extend(response.messages)
    print("Agent:", response.messages[-1]["content"]) 