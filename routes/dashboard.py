from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from models import db, Category, SubCategory, Article

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard-stats', methods=['GET'])
@jwt_required()
def get_dashboard_stats():
    categories = Category.query.count()
    subcategories = SubCategory.query.count()
    articles = Article.query.count()

    return jsonify({
        'categories': categories,
        'subcategories': subcategories,
        'articles': articles
    })
