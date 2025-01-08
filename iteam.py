from flask import Blueprint, request, jsonify
from models import db, Product, ProductIteam, ProToIteam
import uuid
import base64

# Create the Blueprint for handling product items
iteam_bp = Blueprint('iteam', __name__)

@iteam_bp.route('/add_item', methods=['POST'])
def add_iteam():
    """
    Adds a new product item (ProductIteam) and links it to the provided product.
    """
    try:
        # Parse request data
        data = request.json
        product_id = data.get('product_id')  # Product ID to link the item to
        item_name = data.get('name')  # Item name
        price = data.get('price')  # Item price
        description = data.get('description', '')  # Optional item description
        quantity_in_stock = data.get('qty_in_stock')  # Item stock quantity
        item_img = data.get('display_img', None)  # Optional item image

        if not product_id or not item_name or price is None or quantity_in_stock is None:
            return jsonify({"error": "product_id, item name, price, and stock quantity are required"}), 400

        # Check if the product exists
        product = Product.query.get(product_id)
        if not product:
            return jsonify({"error": "Product not found"}), 404

        # Create a new ProductIteam (item)
        new_item = ProductIteam(
            i_id=str(uuid.uuid4()),  # Use UUID for the item ID
            name=item_name,
            price=price,
            disc=description,
            qty_in_stock=quantity_in_stock,
            img=base64.b64decode(item_img) if item_img is not None else None,
        )
        db.session.add(new_item)
        db.session.commit()

        # Link the new item to the product via ProToIteam
        new_pro_to_iteam = ProToIteam(
            i_id=new_item.i_id,
            p_id=product_id
        )
        db.session.add(new_pro_to_iteam)
        db.session.commit()

        return jsonify({
            "message": "Item added and linked to product successfully",
            "item_id": new_item.i_id,
            "product_id": product_id
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@iteam_bp.route('/remove_item/<string:item_id>', methods=['DELETE'])
def remove_iteam(item_id):
    """
    Removes a product item (ProductIteam) by its ID and unlinks it from the product.
    """
    try:
        # Find the item
        item = ProductIteam.query.get(item_id)
        if not item:
            return jsonify({"error": "Item not found"}), 404

        # Find the ProToIteam link to remove it
        pro_to_iteam = ProToIteam.query.filter_by(i_id=item_id).first()
        if pro_to_iteam:
            db.session.delete(pro_to_iteam)

        # Delete the item
        db.session.delete(item)
        db.session.commit()

        return jsonify({"message": "Item removed successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@iteam_bp.route('/get_items_by_product/<string:product_id>', methods=['GET'])
def get_items_by_product_id(product_id):
    try:
        # Fetch the product by its ID
        product = Product.query.filter_by(p_id=product_id).first()
        if not product:
            return jsonify({"error": "Product not found"}), 404

        # Fetch the related product items via the relationship
        product_items = ProductIteam.query.join(ProToIteam, ProToIteam.i_id == ProductIteam.i_id)\
            .filter(ProToIteam.p_id == product_id).all()

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
    
@iteam_bp.route('/get_item/<string:item_id>', methods=['GET'])
def get_item_by_id(item_id):
    try:
        # Fetch the product item by its ID
        item = ProductIteam.query.filter_by(i_id=item_id).first()
        if not item:
            return jsonify({"error": "Item not found"}), 404

        # Serialize the data
        item_data = {
            "item_id": item.i_id,
            "name": item.name,
            "price": item.price,
            "description": item.disc,
            "qty_in_stock": item.qty_in_stock,
            "display_img": base64.b64encode(item.img).decode('utf-8') if item.img else None  # Decode image if it exists
        }

        return jsonify(item_data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

