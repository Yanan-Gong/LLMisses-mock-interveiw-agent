from flask import request, jsonify,Blueprint, render_template
from app.models.bq_mock_interview_v1_audio import bq_mock_interview_agent, bq_question_answer, summarize_interview_agent, end_interview
from app.utils.helpers import process_pdf, process_text, process_audio,validate_audio_format
import base64
from io import BytesIO

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
upload_audio_text = ""
combined_message_sent = False  # Flag to ensure combined message is sent only once

@bp.route('/api/upload-pdf', methods=['POST'])
def upload_pdf():
    """Handles PDF upload from frontend."""
    global uploaded_pdf_text
    file_base64 = request.json.get('fileContent')
    if not file_base64:
        return jsonify({"error": "No file provided"}), 400

    try:
        # Decode the Base64 content and process the PDF
        file_data = base64.b64decode(file_base64)
        pdf_file = BytesIO(file_data)  # Convert to file-like object
        uploaded_pdf_text = process_pdf(pdf_file)

        return jsonify({"message": "PDF uploaded and processed successfully", "text": uploaded_pdf_text}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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


@bp.route('/api/upload-audio', methods=['POST'])
def upload_audio():
    """Handles audio upload from the frontend."""
    global upload_audio_text

    # Retrieve the base64-encoded file content and filename from the request
    file_base64 = request.json.get('fileContent')

    if not file_base64:
        return jsonify({"error": "No file provided"}), 400

    try:
        # Decode the Base64 content into binary audio data
        audio_data = base64.b64decode(file_base64)
        
        # Wrap the binary data in a BytesIO object
        audio_file = BytesIO(audio_data)
        
        # Optional: Check if the audio data is valid before processing
        #if not validate_audio_format(audio_file):
         #   return jsonify({"error": "Invalid or unsupported audio format."}), 400

        # Process the audio file and get the transcription using Whisper
        #audio_file.seek(0)  # Reset file pointer after validation
        upload_audio_text = process_audio(audio_file)

        return jsonify({
            "message": "Audio uploaded and processed successfully",
            "transcription": upload_audio_text
        }), 200

    except Exception as e:
        return jsonify({"error": f"Failed to process audio: {str(e)}"}), 500


@bp.route('/api/chat', methods=['POST'])
def chat():
    """Handles chatbot interactions for both audio and text inputs."""
    global agent, uploaded_pdf_text, uploaded_text, messages, combined_message_sent

    data = request.json
    input_type = data.get('type')  # 'audio' or 'message'
    user_input = data.get('input')

    if not input_type or not user_input:
        return jsonify({"error": "No valid input provided"}), 400

    # Combined PDF and uploaded text logic (run once)
    if not combined_message_sent:
        combined_message = f"{uploaded_pdf_text}\n\n{uploaded_text}"
        messages.append({"role": "user", "content": combined_message})
        combined_message_sent = True

    try:
        # Handle audio input
        if input_type == 'audio':
            # Decode the base64-encoded audio data
            audio_data = base64.b64decode(user_input)
            audio_file = BytesIO(audio_data)
            if not validate_audio_format(audio_file):
                return jsonify({"error": "Invalid audio format"}), 400

            audio_file.seek(0)
            transcription = process_audio(audio_file)  # Convert audio to text
            print("Audio transcription:", transcription)

            # Append transcription as user input
            messages.append({"role": "user", "content": transcription})
        else:
            # Handle text input
            messages.append({"role": "user", "content": user_input})

        # End condition
        if user_input.lower() == 'end':
            print("\nGenerating behavioral interview summary...\n")
            response = bq_question_answer(summarize_interview_agent, messages)
            messages.extend(response.messages)
            final_feedback = end_interview(messages)
            return jsonify({"response": final_feedback})

        # Chatbot logic
        response = bq_question_answer(agent, messages)
        agent = response.agent  # Update the agent if changed
        messages.extend(response.messages)  # Append new messages to the conversation

        # Return chatbot's response
        return jsonify({"response": response.messages[-1].content})

    except Exception as e:
        return jsonify({"error": f"Failed to process input: {str(e)}"}), 500



'''
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

    if user_input.lower() == 'end':
        print("\nGenerating behavioral interview summary...\n")
        messages.append({"role": "user", "content": user_input})
        response = bq_question_answer(summarize_interview_agent, messages)
        messages.extend(response.messages)
        final_feedback = end_interview(messages)
        print("\nExiting the interview process. Goodbye!")

    # Handle the current user input
    messages.append({"role": "user", "content": user_input})
    
    # Call the chatbot logic
    response = bq_question_answer(agent, messages)
    agent = response.agent  # Update the agent if changed
    messages.extend(response.messages)  # Append new messages to the conversation
    
    # Return the latest chatbot response to the frontend
    return jsonify({"response": response.messages[-1].content})'''