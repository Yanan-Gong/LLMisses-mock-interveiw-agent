from flask import Blueprint, request, jsonify
from app.models.bq_mock_interview import bq_question_answer, user_info_extract_agent
import PyPDF2
import os
import whisper

bp = Blueprint('main', __name__)

# Initialize the agent and messages
agent = user_info_extract_agent
messages = []

@bp.route('/api/chat', methods=['POST'])
def chat():
    global agent, messages

    data = request.get_json()
    user_input = data.get('input')

    if not user_input:
        return jsonify({'error': 'Input is required'}), 400

    messages.append({"role": "user", "content": user_input})
    response = bq_question_answer(agent, messages)
    agent = response.agent
    messages.extend(response.messages)

    return jsonify({"response": response.messages[-1]["content"]})

# File Upload Endpoint (Text/PDF)
@bp.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400

    # Configure upload folder
    upload_folder = os.getenv('UPLOAD_FOLDER', 'uploads')
    filepath = os.path.join(upload_folder, file.filename)
    file.save(filepath)

    # Handle PDF files
    if file.filename.endswith('.pdf'):
        with open(filepath, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            pdf_text = ''.join([page.extract_text() for page in reader.pages])
        return jsonify({'content': pdf_text})
    
    # Handle text files
    elif file.filename.endswith('.txt'):
        content = file.read().decode('utf-8')
        return jsonify({'content': content})

    return jsonify({'error': 'Unsupported file type'}), 400

# Audio Upload Endpoint
@bp.route('/api/audio', methods=['POST'])
def upload_audio():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400

    audio_file = request.files['audio']
    if audio_file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400

    # Configure upload folder
    upload_folder = os.getenv('UPLOAD_FOLDER', 'uploads')
    filepath = os.path.join(upload_folder, audio_file.filename)
    audio_file.save(filepath)

    # Process audio using Whisper
    model = whisper.load_model('base')
    transcription = model.transcribe(filepath)

    return jsonify({'transcription': transcription['text']})