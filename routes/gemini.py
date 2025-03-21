import os
import requests
from flask import Blueprint, request, jsonify

gemini_bp = Blueprint('gemini', __name__)

# Load API Key from environment variable
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("Missing GEMINI_API_KEY environment variable")


@gemini_bp.route('/gemini', methods=['POST'])
def generate_gemini_response():
    try:
        print("📢 Received request to /gemini")  # Debug Log

        # Read JSON body
        data = request.get_json(force=True)  # ✅ Force parsing JSON request

        print(f"📢 Received Data: {data}")  # Debug Log

        if not data:
            return jsonify({'error': 'No JSON payload received'}), 400

        prompt = data.get('prompt')
        if not prompt or not isinstance(prompt, str):
            return jsonify({'error': 'Invalid prompt provided'}), 400

        print(f"📢 Sending prompt to Gemini API: {prompt}")  # Debug Log

        # Gemini API Endpoint
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
        
        # Request Payload
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        # Debug Log for payload
        #
        print(f"📢 Sending payload: {payload}")  # Debug Log

        # Send request to  API
        response = requests.post(url, json=payload, headers={'Content-Type': 'application/json'})
        data = response.json()

        print(f"📢  API Response: {data}")  # Debug Log

        if response.status_code != 200:
            return jsonify({'error': data.get('error', {}).get('message', 'Error calling  API')}), response.status_code

        # Extract response text
        response_text = data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', 'No response generated')

        print(f"📢 Extracted response text: {response_text}")  # Debug Log

        return jsonify({'responseText': response_text})
    # 
    except Exception as e:
        print(f"🔥 Server error processing Gemini request: {str(e)}")  # Debug Log
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500
