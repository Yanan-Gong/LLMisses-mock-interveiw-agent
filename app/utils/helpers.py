## helper function to handle pdf/ text file uploads
from openai import OpenAI
from dotenv import load_dotenv
import os
from PyPDF2 import PdfReader
load_dotenv()
from pydub.utils import mediainfo
from io import BytesIO

def process_pdf(file):
    """Processes the uploaded PDF file and extracts text."""
    try:
        reader = PdfReader(file)  # Use the PyPDF2 library to read the PDF
        text = ""
        for page in reader.pages:
            text += page.extract_text()  # Extract text from each page
        return text
    except Exception as e:
        raise ValueError(f"Error processing PDF: {str(e)}")

def process_text(text):
    """Processes the uploaded text"""
    # Add your processing logic here (e.g., save text or parse job description)
    return text

def process_audio(file):
    """Processes the uploaded audio file using OpenAI Whisper."""
    try:
        client = OpenAI(
            api_key=os.getenv('OPENAI_API_KEY'),
            organization=os.getenv('OPENAI_ORGANIZATION'),
            project=os.getenv('OPENAI_PROJECT')
        )
        # Call Whisper for transcription
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=file
        )
        return transcript.text
    except Exception as e:
        raise ValueError(f"Error processing audio: {str(e)}")
