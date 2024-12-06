import json
from openai import OpenAI
from pydantic import BaseModel
from typing import Optional
import inspect
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Fetch sensitive values
api_key = os.getenv('OPENAI_API_KEY')
organization = os.getenv('OPENAI_ORGANIZATION')
project = os.getenv('OPENAI_PROJECT')

if not api_key or not organization or not project:
    raise ValueError("Missing one or more required environment variables: OPENAI_API_KEY, OPENAI_ORGANIZATION, OPENAI_PROJECT")

# Initialize OpenAI client
client = OpenAI(
    api_key=api_key,
    organization=organization,
    project=project
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


###Main function to handle the conversation
def bq_question_answer(agent, messages):

    current_agent = agent
    num_init_messages = len(messages)
    messages = messages.copy()

    while True:

        # turn python functions into tools and save a reverse map
        tool_schemas = [function_to_schema(tool) for tool in current_agent.tools]
        tools = {tool.__name__: tool for tool in current_agent.tools}

        # === 1. get openai completion ===
        response = client.chat.completions.create(
            model=agent.model,
            messages=[{"role": "system", "content": current_agent.instructions}]
            + messages,
            tools=tool_schemas or None,
        )
        message = response.choices[0].message
        messages.append(message)

        if message.content:  # print agent response
            print(f"{current_agent.name}:", message.content)

        if not message.tool_calls:  # if finished handling tool calls, break
            break

        # === 2. handle tool calls ===

        for tool_call in message.tool_calls:
            result = execute_tool_call(tool_call, tools, current_agent.name)

            if type(result) is Agent:  # if agent transfer, update current agent
                current_agent = result
                result = (
                    f"Transfered to {current_agent.name}. Adopt persona immediately."
                )

            result_message = {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result,
            }
            messages.append(result_message)

    # ==== 3. return last agent used and new messages =====
    return Response(agent=current_agent, messages=messages[num_init_messages:])


### Transfer functions ###
def transfer_to_user_info_extract_agent():
    return user_info_extract_agent

def transfer_to_bq_question_generator():
    return bq_question_generator_agent

def transfer_to_feedback_agent():
    return feedback_agent

def trnasfer_to_bq_mock_interview_agent():
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
    instructions=("You are a helpful assistant who can extract user information from text.\n" 
                  "Introduce yourself. Always be very brief. "
                  "1. please summarize the job description." 
                  "2. please summerize resume focusing on relevant past experience."),
    tools=[extract_resume_jd,transfer_to_bq_question_generator,trnasfer_to_bq_mock_interview_agent],)

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
    tools=[bq_question_generator,transfer_to_feedback_agent,trnasfer_to_bq_mock_interview_agent],)

# --------------------------------------------------------#
def evaluate_answers(job_title):
    """
    Evaluate the answers provided by the user. 
    """
    return "success"

# Agent3
feedback_agent = Agent(
    name="Feedback Agent",
    instructions=("You are a interview agent, introduce yourself,you collect bq questions from bq_question_generator_agent. "
                  "You are responsible for mocking the interview process." 
                  " DO NOT provide hint, keep it professional.  "
                  "1. Provide questions one by one to user; after user answer all the questions, go to next step"
                  "2. Collecting all question - answer pairs."
                  "3. Evaluate the answers by STAR methods provided by the user."
                  "4. Provide feedback to the user. Using structure like:"
                  " Question, User Answer, Modified Answer"
                  "5. Transfer to bq_mock_interview_agent"),
    tools=[evaluate_answers,trnasfer_to_bq_mock_interview_agent],
)
# --------------------------------------------------------#


# Agent4: Manager Agent to control the whole process
bq_mock_interview_agent = Agent(
    name="BQ Mock Interview Agent",
    instructions=("You are a helpful assistant who can guide the user through a mock interview process."
                  "Introduce yourself. Always be very brief. "
                  "Gather information from users and lead them into the next step."
                  "1. Extract user information from text."
                  "2. Generate behavior questions based on the job description and resume."
                  "3. Provide feedback on the user's answers."
                  "4. Wrap up the mock interview based on the feedback from feedback_agent. providing suggestions."),
    tools=[transfer_to_user_info_extract_agent,transfer_to_bq_question_generator,transfer_to_feedback_agent],
)



# ----------------- Main -----------------#
'''agent = bq_mock_interview_agent
messages = []

print("Welcome to the mock interview process! Please input your resume and job description.")
while True:
    user = input("User (type 'quit' to exit): ").strip()
    if user.lower() == 'quit':
        print("Exiting the interview Process. Goodbye!")
        break
    messages.append({"role": "user", "content": user})

    response = bq_question_answer(agent, messages)
    agent = response.agent
    messages.extend(response.messages)'''