from flask import Blueprint, request, jsonify
from sqlalchemy.orm import joinedload
from models import db, Category, Product, ProToItem

# Create a Blueprint
category_bp = Blueprint('category', __name__)

@category_bp.route('/get_all_subcat/<category_id>', methods=['GET'])
def get_all_subcategories(category_id):
    """
    Recursively fetches all subcategory IDs for a list of category IDs.
    """
    subcategories = db.session.query(Category.c_id).filter(Category.pc_id.in_(category_id)).all()
    subcategory_ids = [sub.c_id for sub in subcategories]

    if subcategory_ids:
        subcategory_ids += get_all_subcategories(subcategory_ids)

    return subcategory_ids


@category_bp.route('/get_items_by_category', methods=['POST'])
def get_items_by_category():
    """
    Get all unique ProductItem IDs associated with the given category IDs,
    including subcategories.
    """
    data = request.json
    if not data or 'category_ids' not in data:
        return jsonify({'error': 'category_ids is required'}), 400

    category_ids = data['category_ids']

    # Fetch all subcategories recursively
    all_category_ids = set(category_ids)
    all_category_ids.update(get_all_subcategories(category_ids))

    # Fetch all unique ProductItem IDs
    product_items_query = (
        db.session.query(ProToItem.i_id)
        .join(Product, ProToItem.p_id == Product.p_id)
        .filter(Product.c_id.in_(all_category_ids))
        .distinct()
    )

    item_ids = [item.i_id for item in product_items_query]

    return jsonify({'item_ids': item_ids}), 200
