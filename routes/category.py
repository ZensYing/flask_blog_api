import os
from flask import Blueprint, request, jsonify, url_for
from flask_jwt_extended import jwt_required
from models import db, Category
from werkzeug.utils import secure_filename

category_bp = Blueprint('category', __name__)

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@category_bp.route('/categories', methods=['POST'])
@jwt_required()
def create_category():
    title = request.form.get('title')
    slug = request.form.get('slug')
    file = request.files.get('thumbnail')

    if not title or not slug:
        return jsonify({'message': 'Title and slug are required'}), 400

    thumbnail_path = None
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        thumbnail_path = url_for('static', filename=f'uploads/{filename}', _external=True)

    category = Category(title=title, slug=slug, thumbnail=thumbnail_path)
    db.session.add(category)
    db.session.commit()

    return jsonify({'message': 'Category created', 'thumbnail': thumbnail_path}), 201

@category_bp.route('/categories', methods=['GET'])
def get_categories():
    categories = Category.query.all()
    return jsonify([{'id': c.id, 'title': c.title, 'slug': c.slug, 'thumbnail': c.thumbnail} for c in categories])

@category_bp.route('/categories/<int:id>', methods=['PUT'])
@jwt_required()
def update_category(id):
    category = Category.query.get(id)
    if not category:
        return jsonify({'message': 'Category not found'}), 404

    title = request.form.get('title')
    slug = request.form.get('slug')
    file = request.files.get('thumbnail')

    if title:
        category.title = title
    if slug:
        category.slug = slug

    # Update thumbnail if a new file is provided
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        category.thumbnail = url_for('static', filename=f'uploads/{filename}', _external=True)

    db.session.commit()
    return jsonify({'message': 'Category updated successfully', 'thumbnail': category.thumbnail}), 200


@category_bp.route('/categories/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_category(id):
    category = Category.query.get(id)
    if not category:
        return jsonify({'message': 'Category not found'}), 404

    # Delete the associated thumbnail if exists
    if category.thumbnail:
        thumbnail_path = os.path.join(UPLOAD_FOLDER, os.path.basename(category.thumbnail))
        if os.path.exists(thumbnail_path):
            os.remove(thumbnail_path)

    db.session.delete(category)
    db.session.commit()
    return jsonify({'message': 'Category deleted successfully'}), 200
