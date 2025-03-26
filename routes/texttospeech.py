# routes/texttospeech.py
from flask import Blueprint, request, send_file, jsonify
from gtts import gTTS
import os
from io import BytesIO

tts_bp = Blueprint('tts', __name__)

@tts_bp.route('/tts', methods=['POST'])
def text_to_speech():
    data = request.get_json()
    text = data.get('text')
    lang = data.get('lang', 'en')  # default to English

    if not text:
        return jsonify({'error': 'No text provided'}), 400

    try:
        tts = gTTS(text=text, lang=lang)
        audio = BytesIO()
        tts.write_to_fp(audio)
        audio.seek(0)

        return send_file(audio, mimetype='audio/mp3', as_attachment=False, download_name='speech.mp3')
    except Exception as e:
        return jsonify({'error': str(e)}), 500
