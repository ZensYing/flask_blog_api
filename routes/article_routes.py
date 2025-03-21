import os
from flask import Blueprint, request, jsonify
from models import db, Category, Article

article_bp = Blueprint('article', __name__)

# ✅ Get All Categories
@article_bp.route('/categories', methods=['GET'])
def get_categories():
    categories = Category.query.all()
    
    return jsonify([{
        'id': cat.id,
        'title': cat.title
    } for cat in categories])

# ✅ Register this blueprint in your main app (app.py or main.py)
