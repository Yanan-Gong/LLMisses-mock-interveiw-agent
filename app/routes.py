from flask import request, jsonify,Blueprint, render_template
from app.models.bq_mock_interview_v1_audio import bq_mock_interview_agent, bq_question_answer, summarize_interview_agent, end_interview
from app.utils.helpers import process_pdf, process_text, process_audio
import base64
from io import BytesIO
import os
import tempfile

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
        if input_type == 'audio':
            # Decode Base64 audio data and save it as a temporary file
            # This is important! We must save into a temporary file (cannot handle simply use helper
            #  function)
            decoded_audio = base64.b64decode(user_input)
            with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as tmp_audio_file:
                tmp_audio_file.write(decoded_audio)
                tmp_audio_file_path = tmp_audio_file.name
                print(f"Audio file saved to: {tmp_audio_file_path}")

            # Process audio using the helper function
            with open(tmp_audio_file_path, "rb") as audio_file:
                transcription_text = process_audio(audio_file)
                print("Audio transcription:", transcription_text)

            # Clean up temporary file
            os.remove(tmp_audio_file_path)

            # Append transcription to chat as user input
            messages.append({"role": "user", "content": transcription_text})
        else:
            # Handle text input
            messages.append({"role": "user", "content": user_input})

        # Handle 'end' input
        if user_input.lower() == 'end':
            print("\nGenerating behavioral interview summary...\n")
            response = bq_question_answer(summarize_interview_agent, messages)
            messages.extend(response.messages)
            final_feedback = end_interview(messages)
            return jsonify({"response": final_feedback})

        # Process chatbot logic
        response = bq_question_answer(agent, messages)
        agent = response.agent  # Update agent state if necessary
        messages.extend(response.messages)  # Append new messages

        # Return the latest chatbot response
        return jsonify({"response": response.messages[-1].content})

    except Exception as e:
        return jsonify({"error": f"Failed to process input: {str(e)}"}), 500
