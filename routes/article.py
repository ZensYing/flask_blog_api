import os
from flask import Blueprint, request, jsonify, url_for
from flask_jwt_extended import jwt_required
from models import db, Article, Category
from werkzeug.utils import secure_filename

article_bp = Blueprint('article', __name__)

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ✅ Create Article
@article_bp.route('/articles', methods=['POST'])
@jwt_required()
def create_article():
    title = request.form.get('title')
    slug = request.form.get('slug')
    body = request.form.get('body')
    category_id = request.form.get('category_id')
    file = request.files.get('thumbnail')

    if not title or not slug or not body or not category_id:
        return jsonify({'message': 'Title, slug, body, and category are required'}), 400

    category = Category.query.get(category_id)
    if not category:
        return jsonify({'message': 'Category not found'}), 404

    thumbnail_path = None
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        thumbnail_path = url_for('static', filename=f'uploads/{filename}', _external=True)

    article = Article(
        title=title, slug=slug, body=body, 
        thumbnail=thumbnail_path, category_id=category_id
    )
    db.session.add(article)
    db.session.commit()

    return jsonify({'message': 'Article created successfully', 'thumbnail': thumbnail_path}), 201

# ✅ Get Paginated Articles
@article_bp.route('/articles', methods=['GET'])
def get_articles():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search_query = request.args.get('search', '')

    query = Article.query
    if search_query:
        query = query.filter(Article.title.ilike(f"%{search_query}%"))

    paginated_articles = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'articles': [{
            'id': a.id,
            'title': a.title,
            'slug': a.slug,
            'body': a.body,
            'thumbnail': a.thumbnail,
            'category_id': a.category_id,
            'category_title': a.category.title if a.category else None
        } for a in paginated_articles.items],
        'total_pages': paginated_articles.pages,
        'current_page': paginated_articles.page
    })
# ✅ Get Article by Slug
@article_bp.route('/articles/<slug>', methods=['GET'])
def get_article_by_slug(slug):
    article = Article.query.filter_by(slug=slug).first()
    if not article:
        return jsonify({'message': 'Article not found'}), 404

    return jsonify({
        'id': article.id,
        'title': article.title,
        'slug': article.slug,
        'body': article.body,
        'thumbnail': article.thumbnail,
        'category_id': article.category_id,
        'category_title': article.category.title if article.category else None
    })
# ✅ Get Last 3 Articles for Hero Section
@article_bp.route('/articles/latest', methods=['GET'])
def get_latest_articles():
    latest_articles = Article.query.order_by(Article.id.desc()).limit(3).all()

    return jsonify({
        'articles': [{
            'id': a.id,
            'title': a.title,
            'slug': a.slug,
            'body': a.body[:200] + '...',  # Limit preview text
            'thumbnail': a.thumbnail,
            'category_id': a.category_id,
            'category_title': a.category.title if a.category else None
        } for a in latest_articles]
    })

# ✅ Update Article (Fixed)
@article_bp.route('/articles/<int:id>', methods=['PUT'])
@jwt_required()
def update_article(id):
    article = Article.query.get(id)
    if not article:
        return jsonify({'message': 'Article not found'}), 404

    # Support JSON payloads
    if request.is_json:
        data = request.get_json()
        title = data.get('title', article.title)
        slug = data.get('slug', article.slug)
        body = data.get('body', article.body)
        category_id = data.get('category_id', article.category_id)
    else:
        title = request.form.get('title', article.title)
        slug = request.form.get('slug', article.slug)
        body = request.form.get('body', article.body)
        category_id = request.form.get('category_id', article.category_id)

    # Validate category
    if category_id and category_id != article.category_id:
        category = Category.query.get(category_id)
        if not category:
            return jsonify({'message': 'Category not found'}), 404
        article.category_id = category_id

    # Update fields
    article.title = title
    article.slug = slug
    article.body = body

    # Update thumbnail if a new file is provided
    file = request.files.get('thumbnail')
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        article.thumbnail = url_for('static', filename=f'uploads/{filename}', _external=True)

    db.session.commit()
    
    return jsonify({'message': 'Article updated successfully', 'thumbnail': article.thumbnail}), 200

# ✅ Delete Article
@article_bp.route('/articles/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_article(id):
    article = Article.query.get(id)
    if not article:
        return jsonify({'message': 'Article not found'}), 404

    # Delete the associated thumbnail if exists
    if article.thumbnail:
        thumbnail_path = os.path.join(UPLOAD_FOLDER, os.path.basename(article.thumbnail))
        if os.path.exists(thumbnail_path):
            os.remove(thumbnail_path)

    db.session.delete(article)
    db.session.commit()
    return jsonify({'message': 'Article deleted successfully'}), 200
