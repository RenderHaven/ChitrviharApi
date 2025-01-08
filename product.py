from flask import Blueprint, request, jsonify
from models import db, Product, Category
import uuid
import base64

# Create the Blueprint
product_bp = Blueprint('product', __name__)

@product_bp.route('/add_product', methods=['POST'])
def add_product():
    """
    Adds a new product and creates a corresponding category with the product name.
    """
    try:
        # Parse request data
        data = request.json
        print(data.get('pcategory_id'))
        pc_id = data.get('pcategory_id')  # Parent category ID
        product_name = data.get('name')  # Product name
        description = data.get('description', '')  # Optional product description
        display_img = data.get('display_img', None)  # Optional product image
        if not pc_id or not product_name:
            return jsonify({"error": "pc_id and product name are required"}), 400

        # Check if the parent category exists
        parent_category = Category.query.get(pc_id)
        if not parent_category:
            return jsonify({"error": "Parent category not found"}), 404
        # Create a new category for the product
        new_category = Category(
            c_id=str(uuid.uuid4()),
            pc_id=pc_id,
            name=product_name
        )
        db.session.add(new_category)
        db.session.commit()

        # Create a new product under the newly created category
        new_product = Product(
            p_id=str(uuid.uuid4()),
            name=product_name,
            cat_id=new_category.c_id,
            disc=description,
            display_img=base64.b64decode(display_img) if display_img is not None else None,
        )
        print(new_product)
        db.session.add(new_product)
        db.session.commit()
        
        return jsonify({
            "message": "Product added successfully",
            "product_id": new_product.p_id,
            "category_id": new_category.c_id
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@product_bp.route('/remove_product/<string:product_id>', methods=['DELETE'])
def remove_product(product_id):
    """
    Removes a product by its ID. Does not delete its category.
    """
    try:
        # Find the product
        product = Product.query.get(product_id)
        if not product:
            return jsonify({"error": "Product not found"}), 404

        # Delete the product
        db.session.delete(product)
        db.session.commit()

        return jsonify({"message": "Product removed successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@product_bp.route('/get_products_by_category/<string:category_id>', methods=['GET'])
def get_products_by_category(category_id):
    print(category_id)
    """
    Retrieves a list of product IDs for a given parent category ID (pc_id),
    including products of all subcategories.
    """
    try:
        # Find the subcategories under the given category_id
        subcategories = Category.query.filter_by(pc_id=category_id).all()
        if not subcategories:
            return jsonify({"message": "No subcategories found for this category"}), 200

        # Collect all products using the back-populated relationship
        all_products = []
        for subcategory in subcategories:
            all_products.extend(subcategory.products)  # Access related products directly

        if not all_products:
            return jsonify({"message": "No products found for this category"}), 200

        # Extract product details
        product_ids = [product.p_id for product in all_products]
        print(product_ids)
        return jsonify({
            "category_id": category_id,
            "product_ids": product_ids
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500



@product_bp.route('/get_product/<string:product_id>', methods=['GET'])
def get_product_by_id(product_id):
    """
    Retrieves a specific product by its ID.
    """
    try:
        # Find the product by ID
        product = Product.query.get(product_id)
        if not product:
            return jsonify({"error": "Product not found"}), 404

        # Return product details
        print(product)
        return jsonify({
            "product_id": product.p_id,
            "name": product.name,
            "description": product.disc,
            "display_img":base64.b64encode(product.display_img).decode('utf-8') if product.display_img is not None else None,
            "category_id": product.cat_id 
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
