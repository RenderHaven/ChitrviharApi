from flask import Blueprint, request, jsonify
from models import db, Product, ProductItem, ProToItem
import uuid
import base64

# Create the Blueprint for handling product items
item_bp = Blueprint('item', __name__)

@item_bp.route('/add_item', methods=['POST'])
def add_item():
    """
    Adds a new product item (Productitem) and links it to the provided product.
    """
    try:
        # Parse request data
        data = request.json
        product_id = data.get('product_id')  # Product ID to link the item to
        item_name = data.get('name')  # Item name
        price = data.get('price')  # Item price
        description = data.get('description', '')  # Optional item description
        quantity_in_stock = data.get('stock_quantity')  # Item stock quantity
        item_img = data.get('display_img', None)  # Optional item image
        if(item_img!=None):
            item_img="https://images.pexels.com/photos/90946/pexels-photo-90946.jpeg?auto=compress&cs=tinysrgb&w=600"
        if not product_id or not item_name or price is None or quantity_in_stock is None:
            return jsonify({"error": "product_id, item name, price, and stock quantity are required"}), 400

        # Check if the product exists
        product = Product.query.get(product_id)
        if not product:
            return jsonify({"error": "Product not found"}), 404

        # Create a new Productitem (item)
        new_item = ProductItem(
            i_id=str(uuid.uuid4()),  # Use UUID for the item ID
            name=item_name,
            price=price,
            disc=description,
            stock_quantity=quantity_in_stock,
            image_url=item_img,
        )
        db.session.add(new_item)
        db.session.commit()

        # Link the new item to the product via ProToItem
        new_pro_to_item = ProToItem(
            i_id=new_item.i_id,
            p_id=product_id
        )
        db.session.add(new_pro_to_item)
        db.session.commit()

        return jsonify({
            "message": "Item added and linked to product successfully",
            "item_id": new_item.i_id,
            "product_id": product_id
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@item_bp.route('/remove_item/<string:item_id>', methods=['DELETE'])
def remove_item(item_id):
    """
    Removes a product item (Productitem) by its ID and unlinks it from the product.
    """
    try:
        # Find the item
        item = ProductItem.query.get(item_id)
        if not item:
            return jsonify({"error": "Item not found"}), 404

        # Find the ProToItem link to remove it
        pro_to_item = ProToItem.query.filter_by(i_id=item_id).first()
        if pro_to_item:
            db.session.delete(pro_to_item)

        # Delete the item
        db.session.delete(item)
        db.session.commit()

        return jsonify({"message": "Item removed successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@item_bp.route('/get_products_by_item/<string:item_id>', methods=['GET'])
def get_items_by_product_id(item_id):
    try:
        # Fetch the product by its ID
        item = ProductItem.query.filter_by(i_id=item_id).first()
        if not item:
            return jsonify({"error": "Product not found"}), 404

        # Fetch the related product items via the relationship
        products = Product.query.join(ProToItem, ProToItem.p_id == Product.p_id)\
            .filter(ProToItem.i_id == item_id).all()

        # Serialize the data
        products_data = [
            {'p_id':product.p_id ,'name':product.name} for product in products
        ]

        return jsonify({
            "item_id": item.i_id,
            "product_name": item.name,
            "products": products_data,
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@item_bp.route('/get_item/<string:item_id>', methods=['GET'])
def get_item_by_id(item_id):
    try:
        # Fetch the product item by its ID
        item = ProductItem.query.filter_by(i_id=item_id).first()
        if not item:
            return jsonify({"error": "Item not found"}), 404

        # Serialize the data
        item_data = {
            "item_id": item.i_id,
            "name": item.name,
            "price": item.price,
            "description": item.disc,
            "stock_quantity": item.stock_quantity,
            "image_url": item.image_url  # Decode image if it exists
        }

        return jsonify(item_data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@item_bp.route('/search', methods=['GET'])
def search_items():
    """
    Search for items by name or description.
    Query parameters:
      - query: The search keyword (required).
    """
    try:
        query = request.args.get('query', '').strip()
        if not query:
            return jsonify({"error": "Query parameter is required"}), 400

        # Search for items with matching name or description
        items = ProductItem.query.filter(
            (ProductItem.name.ilike(f"%{query}%")) | 
            (ProductItem.disc.ilike(f"%{query}%"))
        ).all()

        # Serialize the search results
        search_results = [
            {
                "i_id": item.i_id,
                "name": item.name,
                "price": item.price,
                "description": item.disc,
                # "stock_quantity": item.stock_quantity,
                # "display_img": base64.b64encode(item.img).decode('utf-8') if item.img else None
            }
            for item in items
        ]

        return jsonify(search_results), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@item_bp.route('/add_items_to_product/<string:product_id>', methods=['POST'])
def add_items_to_product(product_id):
    item_ids = request.json.get('item_ids', [])
    product = Product.query.get_or_404(product_id)
    
    # Add each item to the product
    for item_id in item_ids:
        product_item = ProductItem.query.get(item_id)
        if product_item and product_item not in product.product_items:
            product.product_items.append(product_item)

    db.session.commit()
    return jsonify({'message': 'Items added to product successfully'}), 200
