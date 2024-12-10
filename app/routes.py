from flask import request, jsonify,Blueprint, render_template
from app.models.bq_mock_interview_v0 import bq_mock_interview_agent, bq_question_answer
from app.utils.helpers import process_pdf, process_text
import base64

bp = Blueprint('main', __name__)

@bp.route('/')
def home():
   return render_template('home.html')

@bp.route('/upload')
def upload():
    return render_template('upload.html')

@bp.route('/chat')
def chat_():
    return render_template('chat.html')

@bp.route('/feedback')
def feedback():
    return render_template('feedback.html')

agent = bq_mock_interview_agent  # Initialize the agent globally
messages = []  # Initialize the conversation messages globally
# Global variables to store inputs
uploaded_pdf_text = ""
uploaded_text = ""
combined_message_sent = False  # Flag to ensure combined message is sent only once

@bp.route('/api/upload-pdf', methods=['POST'])
def upload_pdf():
    """Handles PDF upload from frontend"""
    global uploaded_pdf_text
    # file = request.files.get('file')
    fileBase64 = request.json['fileContent']
    if not fileBase64:
        return jsonify({"error": "No file provided"}), 400
    # Process the PDF file and store the result
    file = base64.b64decode(fileBase64)
    uploaded_pdf_text = process_pdf(file)
    return jsonify({"message": "PDF uploaded and processed successfully"})

@bp.route('/api/upload-text', methods=['POST'])
def upload_text():
    """Handles job description text upload"""
    global uploaded_text
    data = request.json
    if not data or 'text' not in data:
        return jsonify({"error": "No text provided"}), 400
    # Store the provided text
    uploaded_text = process_text(data['text'])
    return jsonify({"message": "Text uploaded and processed successfully"})


@bp.route('/api/chat', methods=['POST'])
def chat():
    """Handles chatbot interactions"""
    global agent, uploaded_pdf_text, uploaded_text, messages,combined_message_sent
    
    data = request.json
    user_input = data.get('input')
    
    #if not data or 'message' not in data:
     #   return jsonify({"error": "No message provided"}), 400
    if not combined_message_sent:
        combined_message = f"{uploaded_pdf_text}\n\n{uploaded_text}"
        messages.append({"role": "user", "content": combined_message})
        combined_message_sent = True
        
    # Handle the current user input
    messages.append({"role": "user", "content": user_input})
    
    # Call the chatbot logic
    response = bq_question_answer(agent, messages)
    agent = response.agent  # Update the agent if changed
    messages.extend(response.messages)  # Append new messages to the conversation
    
    # Return the latest chatbot response to the frontend
    return jsonify({"response": response.messages[-1].content})
