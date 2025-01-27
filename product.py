from flask import Blueprint, request, jsonify
from models import db, Product, Category, ProductItem, ProToItem, Description
import uuid
import base64
import cloudinary
import cloudinary.uploader
import category as Cat
from sqlalchemy import or_

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
        description_content = data.get('description', '')  # Optional product description
        tag_name = data.get('tag_name', ' ')  # Tagname
        base64_image = data.get('display_img')
        offer = data.get('discount')
        typ = data.get('type')
        disc_id = data.get('disc_id')  # Description ID

        if not pc_id or not product_name:
            return jsonify({"error": "pc_id and name are required"}), 400

        # Check if the parent category exists
        parent_category = Category.query.get(pc_id)
        if not parent_category:
            return jsonify({"error": "Parent category not found"}), 404

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
            name=product_name,
            c_id=new_category.c_id,
            disc_id=disc_id,  # Use the provided description ID if available
            image_url=image_url,
            discount=offer,
            Type=typ
        )
        db.session.add(new_product)
        db.session.commit()

        # Check if a disc_id was provided
        if disc_id:
            # Validate the provided description ID
            existing_description = Description.query.get(disc_id)
            if not existing_description:
                return jsonify({"error": "Description not found for the provided disc_id"}), 404
        else:
            # Add a new description if content and tag_name are provided
            if description_content and tag_name:
                new_description = Description(
                    content=description_content,
                    tag_name=tag_name
                )
                db.session.add(new_description)
                db.session.commit()

        return jsonify({
            "message": "Product added successfully",
            "product_id": new_product.p_id,
            "category_id": new_category.c_id
        }), 201

    except Exception as e:
        db.session.rollback()
        print(e)
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
        return jsonify(product.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        print(e)
        return jsonify({"error": str(e)}), 500


@product_bp.route('/update_product_description/<string:product_id>', methods=['PUT'])
def update_product_description(product_id):
    """
    Updates the description of a specific product.
    """
    try:
        # Parse request data
        data = request.json
        new_description = data.get('description')

        if not new_description:
            return jsonify({"error": "Description content is required"}), 400

        # Check if the product exists
        product = Product.query.get(product_id)
        if not product:
            return jsonify({"error": "Product not found"}), 404

        # Update or create the description in the `Description` table
        description = Description.query.filter_by(table_name='products', record_id=product_id).first()
        if description:
            description.content = new_description
        else:
            description = Description(
                table_name='products',
                record_id=product_id,
                content=new_description
            )
            db.session.add(description)

        db.session.commit()

        return jsonify({"message": "Product description updated successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500



@product_bp.route('/get_products_by_category/<string:category_id>', methods=['GET'])
def get_products_by_category(category_id):
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
        product_names = [product.name for product in all_products]
        
        return jsonify({
            "category_id": category_id,
            "product_ids": product_ids,
            "product_names": product_names
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
    if query == '<all>':
        products = Product.query.all()
    else:
        products = Product.query.filter(Product.name.ilike(f"%{query}%")).all()

    result = [{"id": p.p_id, "name": p.name, "description": p.description.content if p.description else None} for p in products]
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
    



@product_bp.route('/get_products_of_gender/', methods=['GET'])
def get_products_by_gender():
    """
    Retrieves a list of products filtered by gender type (Man, Woman, UniSex).
    """
    try:
        # Query subcategories based on the Type field
        all_products = Product.query.filter(
            or_(
                Product.Type == 'Man',
                Product.Type == 'Women',
                Product.Type == 'UniSex',
                Product.Type == 'Other'
            )
        ).all()

        if not all_products:
            return jsonify({"message": "No products found for the specified types"}), 200

        # Prepare product data
        data = [
            {
                "product_id": product.p_id,
                "name": product.name,
                "image_url": product.image_url,
                "type": product.Type
            }
            for product in all_products
        ]

        return jsonify(data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

from flask import Flask, jsonify, request


@product_bp.route('/get_items_by_productlist/<product_id>', methods=['POST'])
def item_from_product(product_id):
    """
    Retrieve items for a specific product and its related categories.
    """
    try:
        # Log request headers and body
        print("Request Headers:", request.headers)
        print(f"Request Body: {request.get_data(as_text=True)}")  # Raw body data

        # Parse the request body
        if not request.is_json:
            return jsonify({'error': 'Invalid content type. Expected application/json'}), 415

        data = request.get_json() 
        product_ids = data.get('product_ids', [])
        
        print(f"Received product IDs: {product_ids}")

        if not product_ids:
            return jsonify({'error': 'No product IDs provided'}), 400

        # Fetch all products matching the given IDs
        products = Product.query.filter(Product.p_id.in_(product_ids)).all()
        if not products:
            return jsonify({'error': 'No products found for the given IDs'}), 404

        # Collect all unique categories for the products
        categories = {product.category for product in products if product.category}
        print(f"Unique categories: {[cat.name for cat in categories]}")
        
        category_ids = [cat.c_id for cat in categories]

        new_category_ids=Cat.get_all_subcategories(category_ids)
        category_ids+=new_category_ids

        print(f"All categories (including subcategories): {category_ids}")

        # Get IDs of all categories

        # Fetch all products in these categories
        products_in_categories = Product.query.filter(Product.c_id.in_(category_ids)).all()
        print(f"Products in categories: {[prod.name for prod in products_in_categories]}")

        # Collect all product items for the products in these categories
        all_product_items = []
        for prod in products_in_categories:
            all_product_items.extend(prod.product_items)

        # Prepare the response
        items_data = [
            item.to_dict()
            for item in all_product_items
        ]
        item_ids=[item.i_id for item in all_product_items]
        return jsonify({
            "item_ids": item_ids,
            "item_data" : items_data
        }), 200

    except Exception as e:
        db.session.rollback()
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500
    

@product_bp.route('/remove_product/<product_id>', methods=['DELETE'])
def remove_product(product_id):
    try:
        # Find the product by its ID
        product = Product.query.get(product_id)
        if not product:
            return jsonify({"error": "Product not found"}), 404

        # Get the category ID of the product
        category_id = product.c_id

        # Fetch all subcategories recursively
        def get_subcategories(category_id):
            subcategories = Category.query.filter_by(pc_id=category_id).all()
            subcategory_ids = [sub.c_id for sub in subcategories]
            for sub in subcategories:
                subcategory_ids.extend(get_subcategories(sub.c_id))
            return subcategory_ids

        subcategory_ids = get_subcategories(category_id)
        all_category_ids = [category_id] + subcategory_ids

        # Fetch all products in the category and its subcategories
        products_to_remove = Product.query.filter(Product.c_id.in_(all_category_ids)).all()

        # Collect all product IDs to delete associated product_to_items entries
        product_ids = [prod.p_id for prod in products_to_remove]

        # Delete all product_to_items entries associated with the products
        ProToItem.query.filter(ProToItem.p_id.in_(product_ids)).delete(synchronize_session=False)

        # Delete the products themselves
        for prod in products_to_remove:
            db.session.delete(prod)

        categorys_to_remove = Category.query.filter(Category.c_id.in_(all_category_ids)).all()
        for cat in categorys_to_remove:
            db.session.delete(cat)

        # Commit the changes
        db.session.commit()

        return jsonify({"message": "Products and related entries removed successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Database error occurred", "details": str(e)}), 500