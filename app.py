from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from dotenv import load_dotenv  # Import dotenv
import os

# ✅ Load environment variables before anything else
load_dotenv()

from config import Config
from db import db
from auth import auth_bp
from routes import routes_bp
from routes.dashboard import dashboard_bp
from routes.gemini import gemini_bp 
from routes.image_ocr import ocr_bp
from routes.texttospeech import tts_bp

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
jwt = JWTManager(app)

# ✅ Allow CORS for all origins (Global Access)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(routes_bp, url_prefix='/api')
app.register_blueprint(dashboard_bp, url_prefix='/api')
app.register_blueprint(gemini_bp, url_prefix='/api')
app.register_blueprint(ocr_bp, url_prefix='/api')
app.register_blueprint(tts_bp, url_prefix='/api')

# print("\n✅ Registered Routes:")
# for rule in app.url_map.iter_rules():
#     print(rule)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
