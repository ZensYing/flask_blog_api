from flask import Blueprint
from routes.category import category_bp
from routes.subcategory import subcategory_bp
from routes.article import article_bp

# Create a master Blueprint to register all routes
routes_bp = Blueprint('routes', __name__)

# Register each blueprint
routes_bp.register_blueprint(category_bp)
routes_bp.register_blueprint(subcategory_bp)
routes_bp.register_blueprint(article_bp)
