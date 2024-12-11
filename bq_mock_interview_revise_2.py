import json
from openai import OpenAI
from pydantic import BaseModel
from typing import Optional, List, Dict
import inspect
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Fetch sensitive values
api_key = os.getenv("OPENAI_API_KEY")
organization = os.getenv("OPENAI_ORGANIZATION")
project = os.getenv("OPENAI_PROJECT")

if not api_key or not organization or not project:
    raise ValueError("Missing one or more required environment variables: OPENAI_API_KEY, OPENAI_ORGANIZATION, OPENAI_PROJECT")

# Initialize OpenAI client
client = OpenAI(
    api_key=api_key,
    organization=organization,
    project=project,
)

class Agent(BaseModel):
    name: str
    model: str
    instructions: str
    tools: List[callable]

class Response(BaseModel):
    agent: Optional[Agent]
    messages: List[Dict]

# Tools for agents
def extract_resume_jd():
    """
    Extracts relevant information from the resume and job description.
    """
    return "Extracted key details from the resume and job description."

def bq_question_generator():
    """
    Generates behavioral questions based on the extracted information.
    """
    return [
        "Describe a time you solved a challenging problem using data.",
        "Explain how you handle competing priorities in a project.",
    ]

def evaluate_answers(user_input: str):
    """
    Evaluates answers considering user background.
    """
    if "data" in user_input.lower():
        return "Great job! Your response demonstrates clear problem-solving skills using data."
    else:
        return "Your response could use more specific examples about data usage."

# Agents
user_info_extract_agent = Agent(
    name="User Info Extractor",
    model="gpt-4",
    instructions="Extract key details from the resume and job description.",
    tools=[extract_resume_jd],
)

bq_question_generator_agent = Agent(
    name="Behavioral Question Generator",
    model="gpt-4",
    instructions="Generate behavioral interview questions based on the extracted information.",
    tools=[bq_question_generator],
)

feedback_agent = Agent(
    name="Feedback Agent",
    model="gpt-4",
    instructions="Evaluate the user's responses and provide constructive feedback.",
    tools=[evaluate_answers],
)

bq_mock_interview_agent = Agent(
    name="Mock Interview Manager",
    model="gpt-4",
    instructions=(
        "Guide the user through a mock interview. Start by summarizing the resume and job description. "
        "If extraction fails, proceed with default behavioral questions. Provide feedback after each answer."
    ),
    tools=[extract_resume_jd, bq_question_generator, evaluate_answers],
)

# Core logic for handling agent responses
def execute_tool(tool_name, tools, args=None):
    """
    Executes the specified tool from the tools dictionary.
    """
    if tool_name in tools:
        return tools[tool_name](**args) if args else tools[tool_name]()
    return None

def bq_question_answer(agent, messages):
    """
    Handles the interaction and tool execution for the given agent.
    """
    tools = {tool.__name__: tool for tool in agent.tools}
    response_messages = []

    for message in messages:
        if message["role"] == "user":
            if "extract_resume_jd" in tools:
                result = execute_tool("extract_resume_jd", tools)
                response_messages.append({"role": "assistant", "content": result})
            elif "bq_question_generator" in tools:
                result = execute_tool("bq_question_generator", tools)
                response_messages.append({"role": "assistant", "content": "\n".join(result)})
            elif "evaluate_answers" in tools:
                result = execute_tool("evaluate_answers", tools, {"user_input": message["content"]})
                response_messages.append({"role": "assistant", "content": result})

    return response_messages

# Main script
if __name__ == "__main__":
    agent = bq_mock_interview_agent
    messages = []

    file_path = input("Enter the path to your .txt file with the resume and job description: ").strip()
    try:
        with open(file_path, "r") as file:
            resume_jd = file.read()
        messages.append({"role": "user", "content": resume_jd})
        print("Resume and Job Description loaded successfully.\n")

        # Process the first step
        print("Starting the mock interview process...\n")
        responses = bq_question_answer(agent, messages)
        for response in responses:
            print(f"{agent.name}: {response['content']}")

        while True:
            user_input = input("\nYour response (type 'quit' to exit): ").strip()
            if user_input.lower() == "quit":
                print("Exiting the interview process. Goodbye!")
                break

            messages.append({"role": "user", "content": user_input})
            responses = bq_question_answer(agent, messages)
            for response in responses:
                print(f"{agent.name}: {response['content']}")

    except Exception as e:
        print(f"Error: {e}")
