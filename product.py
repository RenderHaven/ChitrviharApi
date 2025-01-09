from flask import Blueprint, request, jsonify
from models import db, Product, Category,ProductItem,ProToItem
import uuid
import base64
import cloudinary
import cloudinary.uploader

# Create the Blueprint
product_bp = Blueprint('product', __name__)

# Configure Cloudinary
cloudinary.config(
    cloud_name="dimdoq0ng",
    api_key="324659127373814",
    api_secret="eUTC_Jxfvw95dkaCDN7yHEomugE"
)

@product_bp.route('/add_product', methods=['POST'])
def add_product():
    """
    Adds a new product and creates a corresponding category with the product name.
    """
    try:
        # Parse request data
        data = request.json
        pc_id = data.get('pc_id')  # Parent category ID
        product_name = data.get('name')  # Product name
        description = data.get('description', '')  # Optional product description
        base64_image =data.get('display_img')
        # display_img = data.get('display_img', None)  # Optional product image
        if not pc_id or not product_name:
            print(pc_id)
            return jsonify({"error": "pc_id and name are required"}), 400

        # Check if the parent category exists
        parent_category = Category.query.get(pc_id)
        if not parent_category:
            return jsonify({"error": "Parent category not found"}), 404
        # Create a new category for the product

        # Handle base64 image upload to Cloudinary
        image_url = None
        if base64_image:
            try:
                # Decode base64 image and upload to Cloudinary
                file_to_upload = base64.b64decode(base64_image)
                upload_result = cloudinary.uploader.upload(file_to_upload)
                image_url = upload_result.get('secure_url')
            except Exception as e:
                return jsonify({"error": f"Failed to upload image: {str(e)}"}), 500
            

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
            c_id=new_category.c_id,
            disc=description,
            image_url=image_url,
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
        product_nams=[product.name for product in all_products]
        print(product_ids)
        return jsonify({
            "category_id": category_id,
            "product_ids": product_ids,
            "product_names":product_nams
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
            "p_id": product.p_id,
            "name": product.name,
            "description": product.disc,
            "image_url":product.image_url,
            "c_id": product.c_id 
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@product_bp.route('/get_items_by_product/<string:product_id>', methods=['GET'])
def get_items_by_product_id(product_id):
    try:
        # Fetch the product by its ID
        product = Product.query.filter_by(p_id=product_id).first()
        if not product:
            return jsonify({"error": "Product not found"}), 404

        # Fetch the related product items via the relationship
        product_items = ProductItem.query.join(ProToItem, ProToItem.i_id == ProductItem.i_id)\
            .filter(ProToItem.p_id == product_id).all()

        # Serialize the data
        items_data = [
            item.i_id for item in product_items
        ]

        return jsonify({
            "product_id": product.p_id,
            "product_name": product.name,
            "item_ids": items_data
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@product_bp.route('/search', methods=['GET'])
def search_products():
    query = request.args.get('query', '').strip()
    if len(query) < 3:
        return jsonify({"error": "Search query must be at least 3 characters long"}), 400

    # Search products by name (case-insensitive)
    products = Product.query.filter(Product.name.ilike(f"%{query}%")).all()
    
    result = [{"id": p.p_id, "name": p.name, "description": p.disc} for p in products]
    return jsonify(result), 200

@product_bp.route('/remove_item_from_product/<product_id>', methods=['POST'])
def remove_item_from_product(product_id):
    """
    Remove an item from a specific product.
    """
    try:
        data = request.get_json()
        item_id = data.get('item_id')

        if not item_id:
            return jsonify({'error': 'Item ID is required'}), 400

        # Find the product-item relationship
        product_item = ProToItem.query.filter_by(p_id=product_id, i_id=item_id).first()

        if not product_item:
            return jsonify({'error': 'Item not found in this product'}), 404

        # Remove the relationship
        db.session.delete(product_item)
        db.session.commit()

        return jsonify({'message': 'Item removed from product successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

