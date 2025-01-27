from flask import Blueprint, request, jsonify
from sqlalchemy.exc import DatabaseError
from models import Order,db

orders_bp = Blueprint('orders', __name__)

# Initialize SQLAlchemy

# {
#     "id": self.id,
#     "user_id": self.user_id,
#     "item_id": self.item_id,
#     "address_id": self.address_id,  # Include the address_id
#     "item_name": self.item.name if self.item else None,
#     "quantity": self.quantity,
#     "status": self.status,
#     "datetime": self.datetime.isoformat() if self.datetime else None,
#     "user": self.user.to_dict() if self.user else None,  # Include user information
#     "address": self.address.to_dict() if self.address else None,  # Include address information
# }

@orders_bp.route('/get_all', methods=['GET'])
def get_orders():
    orders = Order.query.all()
    return jsonify([order.to_dict() for order in orders])

@orders_bp.route('/get/<string:order_id>', methods=['GET'])
def get_order(order_id):
    order = Order.query.get(order_id)
    if order:
        return jsonify(order.to_dict())
    else:
        return jsonify({"error": "Order not found"}), 404

@orders_bp.route('/add', methods=['POST'])
def create_order():
    data = request.json
    try:
        order = Order(**data)
        db.session.add(order)
        db.session.commit()
        return jsonify(order.to_dict()), 201
    except DatabaseError as err:
        db.session.rollback()
        print(err)
        return jsonify({"error": str(err)}), 400

@orders_bp.route('/edit/<string:order_id>', methods=['PUT'])
def update_order(order_id):
    order = Order.query.get(order_id)
    if order:
        data = request.json
        for key, value in data.items():
            setattr(order, key, value)
        db.session.commit()
        return jsonify(order.to_dict()), 200
    else:
        return jsonify({"error": "Order not found"}), 404

@orders_bp.route('/delete/<string:order_id>', methods=['DELETE'])
def delete_order(order_id):
    order = Order.query.get(order_id)
    if order:
        db.session.delete(order)
        db.session.commit()
        return jsonify({"message": "Order deleted successfully"}), 200
    else:
        return jsonify({"error": "Order not found"}), 404
    
@orders_bp.route('/get_card_item/<string:user_id>', methods=['GET'])
def get_card_item(user_id):
    """
    Fetch all orders for a given user_id in card format.
    """
    try:
        # Query all orders for the given user_id
        orders = Order.query.filter_by(user_id=user_id).all()
        
        if orders:
            return jsonify([order.to_card_dict() for order in orders]), 200
        else:
            return jsonify({"message": "No orders found for the given user_id"}), 404
    except Exception as err:
        print(err)
        return jsonify({"error": "An error occurred while fetching the orders"}), 500
