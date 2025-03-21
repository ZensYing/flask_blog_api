import os
from flask import Blueprint, request, jsonify, url_for
from flask_jwt_extended import jwt_required
from models import db, SubCategory, Category
from werkzeug.utils import secure_filename

subcategory_bp = Blueprint('subcategory', __name__)

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ✅ Create Subcategory
@subcategory_bp.route('/subcategories', methods=['POST'])
@jwt_required()
def create_subcategory():
    title = request.form.get('title')
    slug = request.form.get('slug')
    category_id = request.form.get('category_id')
    file = request.files.get('thumbnail')

    if not title or not slug or not category_id:
        return jsonify({'message': 'Title, slug, and category_id are required'}), 400

    # Check if category exists
    category = Category.query.get(category_id)
    if not category:
        return jsonify({'message': 'Category not found'}), 404

    thumbnail_path = None
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        thumbnail_path = url_for('static', filename=f'uploads/{filename}', _external=True)

    subcategory = SubCategory(title=title, slug=slug, thumbnail=thumbnail_path, category_id=category_id)
    db.session.add(subcategory)
    db.session.commit()

    return jsonify({'message': 'Subcategory created', 'thumbnail': thumbnail_path}), 201


# ✅ Get All Subcategories (Optional Search by Title)
@subcategory_bp.route('/subcategories', methods=['GET'])
def get_subcategories():
    search_query = request.args.get('search', '')
    
    if search_query:
        subcategories = SubCategory.query.filter(SubCategory.title.ilike(f"%{search_query}%")).all()
    else:
        subcategories = SubCategory.query.all()

    return jsonify([
        {
            'id': s.id,
            'title': s.title,
            'slug': s.slug,
            'thumbnail': s.thumbnail,
            'category_id': s.category_id,
            'category_title': s.category.title if s.category else None
        }
        for s in subcategories
    ])


# ✅ Update Subcategory
@subcategory_bp.route('/subcategories/<int:id>', methods=['PUT'])
@jwt_required()
def update_subcategory(id):
    subcategory = SubCategory.query.get(id)
    if not subcategory:
        return jsonify({'message': 'Subcategory not found'}), 404

    title = request.form.get('title')
    slug = request.form.get('slug')
    category_id = request.form.get('category_id')
    file = request.files.get('thumbnail')

    if title:
        subcategory.title = title
    if slug:
        subcategory.slug = slug
    if category_id:
        category = Category.query.get(category_id)
        if not category:
            return jsonify({'message': 'Category not found'}), 404
        subcategory.category_id = category_id

    # Update thumbnail if a new file is provided
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        subcategory.thumbnail = url_for('static', filename=f'uploads/{filename}', _external=True)

    db.session.commit()
    return jsonify({'message': 'Subcategory updated successfully', 'thumbnail': subcategory.thumbnail}), 200


# ✅ Delete Subcategory
@subcategory_bp.route('/subcategories/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_subcategory(id):
    subcategory = SubCategory.query.get(id)
    if not subcategory:
        return jsonify({'message': 'Subcategory not found'}), 404

    # Delete the associated thumbnail if exists
    if subcategory.thumbnail:
        thumbnail_path = os.path.join(UPLOAD_FOLDER, os.path.basename(subcategory.thumbnail))
        if os.path.exists(thumbnail_path):
            os.remove(thumbnail_path)

    db.session.delete(subcategory)
    db.session.commit()
    return jsonify({'message': 'Subcategory deleted successfully'}), 200
