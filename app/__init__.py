from flask import Flask
from dotenv import load_dotenv
import os

def create_app():
    load_dotenv()  # Load environment variables
    app = Flask(__name__)

    # Load configurations
    app.config['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')
    app.config['OPENAI_ORGANIZATION'] = os.getenv('OPENAI_ORGANIZATION')
    app.config['OPENAI_PROJECT'] = os.getenv('OPENAI_PROJECT')
    app.config['UPLOAD_FOLDER'] = 'uploads'  # Upload folder for file handling

    # Ensure the upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Register routes
    from .routes import bp as main_bp
    app.register_blueprint(main_bp)

    return app
