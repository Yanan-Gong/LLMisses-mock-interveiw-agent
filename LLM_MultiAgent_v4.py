import json
from openai import OpenAI
from pydantic import BaseModel
from typing import Optional
import inspect
from dotenv import load_dotenv
import os
import whisper




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
            tool_name = getattr(tool_call.function, "name", None)
            tool_args = json.loads(getattr(tool_call.function, "arguments", "{}"))
            tool_call_id = getattr(tool_call, "id", None)

            if not tool_name:
                print("Warning: Tool name not found in tool_call.")
                continue

            if tool_name in tools:
                tool_result = tools[tool_name](**tool_args)

                # Prepare the tool response message
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

                # Append tool response message with the correct tool_call_id
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

# def transfer_to_bq_question_generator():
#     return bq_question_generator_agent

def transfer_to_feedback_agent():
    return feedback_agent

def transfer_to_eval_agent():
    return evaluation_agent

def transfer_to_bq_mock_interview_agent():
    return bq_mock_interview_agent
def transfer_to_summarize_interview_agent():
    return summarize_interview_agent


###  Agent functions and corresponding tools ###
### You can change the input parameters as you like. As long as this input information can be captured in the conversation
### Here I use job_title as the input parameter, you can change to other parameters like experience_years, skills, etc.
def extract_resume_jd(job_title):
    """
    Extracts the experience and job requirements from given resume and job description
    """
    return "success"


def bq_question_generator(job_title):
    """
    based on user's info, generates 6 different behavior questions for the interview
    """
    return "success"


def generate_full_feedback_json(messages, output_file="full_interview_feedback.json"):
    """
    Extracts detailed feedback for all questions and saves it as a JSON file.
    """
    print("Starting to generate feedback JSON...")
    feedback_list = []
    current_feedback = {}
    
    required_sections = ["Question", "User Answer", "Strengths", "Weaknesses", "Suggestions", "Modified Answer"]
    
    for message in messages:
        if not hasattr(message, "role") or not hasattr(message, "content"):
            continue
            
        content = str(message.content)
        if not content:
            continue

        # Check if this message contains feedback (should have all required sections)
        has_all_sections = all(f"**{section}**:" in content or f"{section}:" in content 
                             for section in required_sections)
        
        if has_all_sections:
            feedback_entry = {}
            for section in required_sections:
                feedback_entry[section.lower().replace(" ", "_")] = extract_section(content, section)
            
            if all(feedback_entry.values()):  # Only add if all sections have content
                feedback_list.append(feedback_entry)
                print(f"Found complete feedback entry with {len(feedback_entry)} sections")

    # Create the final structure
    feedback_data = {
        "questions": feedback_list
    }

    if feedback_list:
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(feedback_data, f, indent=4, ensure_ascii=False)
            print(f"Successfully saved {len(feedback_list)} feedback entries to {output_file}")
        except Exception as e:
            print(f"Error saving feedback file: {str(e)}")
    else:
        print("No complete feedback entries found to save")

    return feedback_data

def extract_section(text, marker):
    """
    Extracts a section from the text between the given marker and the next marker or end of text.
    """
    # Remove asterisks from marker for consistency
    clean_marker = marker.replace("*", "")
    
    # List of possible markers (both with and without asterisks)
    markers = [
        "**Question**:", "**User Answer**:", "**Strengths**:", "**Weaknesses**:", 
        "**Suggestions**:", "**Modified Answer**:",
        "Question:", "User Answer:", "Strengths:", "Weaknesses:", 
        "Suggestions:", "Modified Answer:"
    ]
    
    # Try both versions of the marker (with and without asterisks)
    start_idx = -1
    for m in [f"**{clean_marker}**:", clean_marker + ":"]:
        if m in text:
            start_idx = text.find(m) + len(m)
            break
    
    if start_idx == -1:
        return None
    
    # Find the next marker
    end_idx = len(text)
    for next_marker in markers:
        next_idx = text.find(next_marker, start_idx)
        if next_idx != -1 and next_idx < end_idx:
            end_idx = next_idx
    
    extracted_text = text[start_idx:end_idx].strip()
    return extracted_text if extracted_text else None
def end_interview(messages):
    """
    Function to handle the end of interview process and generate feedback JSON
    """
    print("Generating interview feedback file...")
    feedback_data = generate_full_feedback_json(messages)
    if feedback_data and feedback_data["questions"]:
        print(f"Successfully generated feedback for {len(feedback_data['questions'])} questions")
    else:
        print("No feedback was generated. Please check the message format.")
    return feedback_data

    
# Agent1
user_info_extract_agent = Agent(
    name="User Info Extractor",
    instructions=("You are a helpful assistant who can extract user information from text and generate high quality interview behavior questions based on the information you obtain.\n" "Introduce yourself. Always be very brief. " "1. please summarize the job description." 
"2. please summerize resume focusing on relevant past experience. 3. generate 5-10 behavior questions based on the Job Description Summary and Resume Summary 4.Do not provide answers to the questions. 5. Once the process is complete, transfer control back to the `bq_mock_interview_agent`, do not present questions"),
    tools=[extract_resume_jd,bq_question_generator,transfer_to_bq_mock_interview_agent],)


# --------------------------------------------------------#


# --------------------------------------------------------#
def evaluate_answers(job_title):
    """
    Evaluate the answers provided by the user. 
    Feedback MUST follow the format below : \n"
        "   - **Question**: [The question provided to the user] \n"
        "   - **User Answer**: [The original response from the user] \n"
        "   - **Strengths**: [Highlight positive aspects] \n"
        "   - **Weaknesses**: [Identify areas of improvement] \n"
        "   - **Suggestions**: [Provide actionable suggestions] \n"
        "   - **Modified Answer**: [Present the refined answer] \n\n"
    """
    return "success"
def evaluate_feedback(feedback: str) -> dict:
    """
    Evaluate the feedback provided by the feedback_agent.

    Args:
        feedback (str): The feedback provided by the feedback_agent.

    Returns:
        dict: A dictionary containing the refined feedback and suggestions for improvement.
    """
    # print(f"Input Feedback to Evaluation Agent: {feedback}")  # Debug input
    # Example evaluation logic
    refined_feedback = f"Refined feedback: {feedback.strip()}. Make it clearer, more relevant to the question asked, more professional, and more actionable."
    suggestions = "Focus on being concise and providing examples to justify the evaluation."
    
    result = {
        "original_feedback": feedback,
        "refined_feedback": refined_feedback,
        "suggestions": suggestions
    }
    # print(f"Evaluation Agent Output: {result}")  # Debug output
    return result
    


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
        "6. You MUST present the final refined feedback to the user using the following structure: \n"
        "   - **Question**: [The question provided to the user] \n"
        "   - **User Answer**: [The original response from the user] \n"
        "   - **Strengths**: [Highlight positive aspects] \n"
        "   - **Weaknesses**: [Identify areas of improvement] \n"
        "   - **Suggestions**: [Provide actionable suggestions] \n"
        "   - **Modified Answer**: [Present the refined answer] \n\n"
        "7. You MUST include ALL of the following sections in your feedback:\n"
        "- **Question**: [question text]\n"
        "- **User Answer**: [answer text]\n"
        "- **Strengths**: [strengths text]\n"
        "- **Weaknesses**: [weaknesses text]\n"
        "- **Suggestions**: [suggestions text]\n"
        "- **Modified Answer**: [modified answer text]\n"
        "8. Once the process is complete, transfer control back to the `bq_mock_interview_agent`. \n\n"
        "9. For each question-answer pair, provide structured feedback using EXACTLY this format:\n\n"
        "**Question**: [exact question text]\n"
        "**User Answer**: [exact user answer text]\n"
        "**Strengths**: [list specific strengths]\n"
        "**Weaknesses**: [list specific areas for improvement]\n"
        "**Suggestions**: [provide actionable advice]\n"
        "**Modified Answer**: [provide an improved version of the answer]\n\n"
        "10. Ensure EVERY feedback entry includes ALL six sections above.\n"
        "11. Do not skip any sections or leave any empty.\n"
        "12. When processing the final feedback request, compile ALL previous question-answer pairs and provide feedback for each one.\n"
        "13. Maintain consistent formatting with the exact section headers shown above.\n\n"
        "Remember: Each feedback MUST contain all six sections with the exact headers shown above."
        "Guidelines: \n"
        "- Always consider the user's experience level and the role they are applying for when generating feedback. \n"
        "- Maintain professionalism throughout the interaction. \n"
        "- Do not provide hints or direct answers unless evaluating or refining the user’s response. \n"
        "- Adapt to feedback from the `Evaluation Agent` to continuously improve the quality of your assessments.\n"
        "- NEVER show your feedback to user, only send it to 'BQ Mock Interview Agent'. \n\n"

  ),
    tools=[evaluate_answers,  transfer_to_eval_agent,transfer_to_bq_mock_interview_agent],
)
# --------------------------------------------------------#

    
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
        "- Collaborate effectively with the Feedback Agent to foster continuous improvement in evaluating user responses. \n"
        "- NEVER show your response to user, ONLY send it to 'Feedback Agent' \n\n."
        "You MUST include ALL of the following sections in your feedback:\n"
        "- **Question**: [question text]\n"
        "- **User Answer**: [answer text]\n"
        "- **Strengths**: [strengths text]\n"
        "- **Weaknesses**: [weaknesses text]\n"
        "- **Suggestions**: [suggestions text]\n"
        "- **Modified Answer**: [modified answer text]\n"
        "Note: You are not responsible for directly evaluating the user’s answer but for ensuring the feedback provided by the Feedback Agent is robust, actionable, and aligned with the question’s intent, the user’s experience, and the role they are targeting."
    ),
    tools=[evaluate_feedback, transfer_to_feedback_agent, transfer_to_bq_mock_interview_agent]
)

# Agent5: Manager Agent to control the whole process
bq_mock_interview_agent = Agent(
    name="BQ Mock Interview Agent",
    instructions=(
        "You are a professional mock interview assistant responsible for guiding users through a structured and effective mock interview process. "
        "Your role ensures that users receive valuable feedback to refine their interview performance.\n\n"
        
        "### Primary Responsibilities:\n\n"
        
        "1. **Introduce Yourself**: Begin with a concise and professional introduction to set expectations for the mock interview process.\n\n"
        
        "2. **Extract User Information**: Gather essential details such as the user's job description, resume, and any other relevant information. Use this data to understand their background and customize the interview process.\n\n"
        
        "3. **Generate Behavioral Questions**: Create behavioral questions that align with the user's job description and resume. Ensure the questions are relevant, challenging, and appropriate to the user's experience level and target role.\n\n"
        
        "4. **Sequential Question Delivery**: Show one question at a time to the user. Allow them to fully answer each question before proceeding to the next. NEVER display multiple questions simultaneously. \n\n"
        
        "5. **Monitor Progress**: Keep track of the user's progress throughout the mock interview. If the user chooses to quit the session early, provide a summary that includes:\n"
        "   - The total number of questions answered.\n"
        "   - Common weaknesses identified.\n"
        "   - Actionable suggestions for improving future performance.\n\n"
        
        "6. **Silent Feedback Collection**: DO NOT provide feedback immediately after each question. After each user response, evaluate the answer and store feedback internally. DO NOT share any feedback with the user during the interview process. Collect feedback for all questions answered and present it only in the following scenarios:\n"
        "   - At the end of the mock interview.\n"
        "   - If the user chooses to quit or terminate the interview early.\n\n"
        
        "7. **Provide Feedback**: At the appropriate time (end of the interview or early termination), evaluate the user’s responses systematically. Identify:\n"
        "   - Strengths: Highlight the positive aspects of their answers.\n"
        "   - Weaknesses: Identify areas that need improvement.\n"
        "   - Suggestions: Offer actionable advice to enhance their responses.\n"
        "Collaborate with the Feedback Agent to refine the feedback for accuracy and clarity.\n\n"
        
        "8. **Refine and Learn**: Continuously improve the feedback by incorporating insights from the Evaluation Agent. Use these insights to enhance future evaluations and adapt to new user responses effectively.\n\n"
        "9. You MUST present the final feedback on each question to the user using the following structure: \n"
        "   - **Question**: [The question provided to the user] \n"
        "   - **User Answer**: [The original response from the user] \n"
        "   - **Strengths**: [Highlight positive aspects] \n"
        "   - **Weaknesses**: [Identify areas of improvement] \n"
        "   - **Suggestions**: [Provide actionable suggestions] \n"
        "   - **Modified Answer**: [Present the refined answer] \n\n"
        
        "10. **Wrap-Up**: At the conclusion of the mock interview or upon early termination, provide comprehensive feedback on all answered questions. Incorporate suggestions from the Feedback Agent and include:\n"
        "   - Specific improvements for each answer.\n"
        "   - Overall suggestions for future preparation.\n"
        "   - Tailored guidance for succeeding in real interviews.\n\n"
        "11. Once the process is complete, transfer control to the `summarize_interview_agent`. \n\n"
        "12. **Example Feedback Format**:\n"
        "   Question: Tell me about a time you handled a difficult situation.\n"
        "   User Answer: I stayed calm and solved the problem.\n"
        "   Strengths: Demonstrated composure under pressure\n"
        "   Weaknesses: Lack of specific details and STAR format\n"
        "   Suggestions: Include context, actions taken, and results achieved\n"
        "   Modified Answer: In my previous role, when faced with [specific situation]...\n\n"
        
        "### Guidelines:\n"
        "- Always ensure each feedback section is properly labeled and contains meaningful content. Never skip or leave any section empty.\n"
        "- DO NOT provide immediate feedback after each question - collect and store internally until the interview ends.\n"
        "- Always maintain a professional tone.\n"
        "- Tailor the process to the user's experience level and target role.\n"
        "- Ensure feedback is actionable, clear, and constructive."
        "- ONLY PRESENT FEEDBACK ON EACH QUESTION AT THE END OF INTERVIEW/ WHEN USER CHOOSE TO QUIT INTERVIEW!!!!!"
    ),
    tools=[transfer_to_user_info_extract_agent, transfer_to_feedback_agent, transfer_to_eval_agent, transfer_to_summarize_interview_agent],
)
summarize_interview_agent = Agent(
    name="Summarize Interview Agent",
    instructions=(
        "You are a professional assistant responsible for summarizing the interview process. "
        "Your role ensures that users receive a comprehensive, valuable feedback to refine their interview performance at the end of the interview.\n\n"
        "**Provide Feedback**: At the appropriate time (end of the interview or early termination), evaluate the user’s responses systematically. Identify:\n"
        "   - Strengths: Highlight the positive aspects of their answers.\n"
        "   - Weaknesses: Identify areas that need improvement.\n"
        "   - Suggestions: Offer actionable advice to enhance their responses.\n"
    ),
    tools=[transfer_to_bq_mock_interview_agent,transfer_to_feedback_agent,transfer_to_summarize_interview_agent],
)

# ----------------- Main -----------------#
agent = bq_mock_interview_agent
messages = []

print("Welcome to the mock interview process! Please input your resume and job description.")
while True:
    user = input("User (type 'quit' to exit): ").strip()
    # if user.lower() == 'quit':
    #     print("Exiting the interview Process. Goodbye!")
    #     break
    if user.lower() == 'quit':
        print("\nGenerating behavioral interview summary...\n")
        messages.append({"role": "user", "content": user})
        response = bq_question_answer(summarize_interview_agent, messages)
        messages.extend(response.messages)
        final_feedback = end_interview(messages)
        print("\nExiting the interview process. Goodbye!")
        break
    messages.append({"role": "user", "content": user})

    response = bq_question_answer(agent, messages)
    agent = response.agent
    messages.extend(response.messages)
    