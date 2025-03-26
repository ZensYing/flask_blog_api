import pytesseract
from flask import Blueprint, request, jsonify, send_file
from PIL import Image, ImageFilter
from googletrans import Translator
from fpdf import FPDF
import tempfile
import os

ocr_bp = Blueprint('ocr', __name__)
translator = Translator()

# 🔍 ENHANCED OCR
@ocr_bp.route('/ocr', methods=['POST'])
def image_to_text():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400

    image_file = request.files['image']
    lang = request.form.get('lang', 'eng+khm')  # Default to both

    try:
        image = Image.open(image_file.stream).convert("L")
        image = image.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))  # Auto-enhance

        custom_config = r'--oem 3 --psm 6'
        text = pytesseract.image_to_string(image, lang=lang, config=custom_config)

        # 🌐 Translate result
        translate_to = request.form.get('translate_to', 'en')  # Optional
        translated_text = ''
        if translate_to:
            translated = translator.translate(text, dest=translate_to)
            translated_text = translated.text

        return jsonify({
            'text': text.strip(),
            'translated': translated_text.strip()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# 📄 EXPORT OCR RESULT
@ocr_bp.route('/ocr/export', methods=['POST'])
def export_text():
    data = request.get_json()
    text = data.get('text')
    export_type = data.get('type', 'txt')

    if not text:
        return jsonify({'error': 'No text provided'}), 400

    try:
        if export_type == 'txt':
            path = tempfile.mktemp(suffix='.txt')
            with open(path, 'w', encoding='utf-8') as f:
                f.write(text)
        elif export_type == 'pdf':
            path = tempfile.mktemp(suffix='.pdf')
            pdf = FPDF()
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.set_font("Arial", size=12)
            for line in text.splitlines():
                pdf.multi_cell(0, 10, line)
            pdf.output(path)
        else:
            return jsonify({'error': 'Invalid export type'}), 400

        return send_file(path, as_attachment=True)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# 📂 BULK OCR SUPPORT
@ocr_bp.route('/ocr/bulk', methods=['POST'])
def bulk_ocr():
    if 'images' not in request.files:
        return jsonify({'error': 'No images uploaded'}), 400

    image_files = request.files.getlist('images')
    lang = request.form.get('lang', 'eng+khm')
    results = []

    try:
        for image_file in image_files:
            image = Image.open(image_file.stream).convert("L")
            image = image.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))

            custom_config = r'--oem 3 --psm 6'
            text = pytesseract.image_to_string(image, lang=lang, config=custom_config)

            results.append({
                'filename': image_file.filename,
                'text': text.strip()
            })

        return jsonify({'results': results})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
