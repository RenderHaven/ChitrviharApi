from flask import Blueprint, request, jsonify
from models import db, Category, Variation, VariationOption ,ProductItem ,ProductItemVariation
from sqlalchemy.exc import IntegrityError

variation_bp = Blueprint('variation_bp', __name__)

# Route to add a new variation
@variation_bp.route('/add_variation', methods=['POST'])
def add_variation():
    try:
        # Get data from request body
        data = request.get_json()

        # Debugging: Check the input data
        print("Received data:", data)

        # Validate input
        if not data.get('name') or not data.get('options'):
            return jsonify({"error": "Name and options are required"}), 400


        variation = Variation(
            name=data['name'],
        )
        
        db.session.add(variation)
        db.session.commit()
        
        # Debugging: Check if the variation was added
        print("Variation added:", variation.id)

        # Add options (values) to the variation
        for option_value in data['options']:
            option = VariationOption(value=option_value, variation_id=variation.id)
            db.session.add(option)

        db.session.commit()
        
        # Return success response
        return jsonify({"message": "Variation added successfully", "variation_id": variation.id}), 201

    except IntegrityError as e:
        db.session.rollback()
        print("IntegrityError:", e)
        return jsonify({"error": "Database error. Could not add variation."}), 500
    except Exception as e:
        # Catch all other exceptions and return the error
        print("Error:", e)
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


# Route to get all variations with id and name
@variation_bp.route('/get_variation', methods=['GET'])
def get_all_variations():
    variations = Variation.query.all()
    variation_list = [{"id": variation.id, "name": variation.name} for variation in variations]
    return jsonify(variation_list)




@variation_bp.route('/attach_variation', methods=['POST'])
def attach_variation_to_item():
    """
    Attach a variation option to a product item.
    """
    try:
        data = request.get_json()

        # Validate input
        item_id = data.get('item_id')
        variation_option_id = data.get('variation_option_id')

        if not item_id or not variation_option_id:
            return jsonify({"error": "item_id and variation_option_id are required"}), 400

        # Check if product item exists
        product_item = ProductItem.query.get(item_id)
        if not product_item:
            return jsonify({"error": f"ProductItem with id {item_id} does not exist"}), 404

        # Check if variation option exists
        variation_option = VariationOption.query.get(variation_option_id)
        if not variation_option:
            return jsonify({"error": f"VariationOption with id {variation_option_id} does not exist"}), 404

        # Check if this variation is already attached
        existing_relation = ProductItemVariation.query.filter_by(
            product_item_id=item_id,
            variation_option_id=variation_option_id
        ).first()
        if existing_relation:
            return jsonify({"message": "Variation is already attached to the item"}), 200

        # Create a new relationship
        new_relation = ProductItemVariation(
            product_item_id=item_id,
            variation_option_id=variation_option_id
        )
        db.session.add(new_relation)
        db.session.commit()

        return jsonify({"message": "Variation successfully attached to the item"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@variation_bp.route('/get_variations_by_item/<string:item_id>', methods=['GET'])
def get_variations_by_item(item_id):
    """
    Get variations (names and values) associated with a product item by its item_id.
    """
    try:
        # Query the ProductItemVariation table for the given item_id
        item_variations = ProductItemVariation.query.filter_by(product_item_id=item_id).all()

        if not item_variations:
            return jsonify({"error": "No variations found for the given item_id"}), 404

        # Prepare a list of variation details
        variations = []
        variation_ids = set()  # Track unique variation_id's

        for item_variation in item_variations:
            variation_option = VariationOption.query.get(item_variation.variation_option_id)
            if variation_option:
                variation = Variation.query.get(variation_option.variation_id)
                if variation:
                    # Add to list only if the variation_id is unique
                    if variation.id not in variation_ids:
                        variations.append({
                            "variation_id": variation.id,
                            "variation_name": variation.name,
                            "option_values": [option.value for option in variation.options],
                            "option_ids": [option.id for option in variation.options]
                        })
                        variation_ids.add(variation.id)

        return jsonify(variations), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    

@variation_bp.route('/search', methods=['GET'])
def search_variations():
    """
    Search for variations by name, or return all variations if the query is 'all'.
    """
    try:
        query = request.args.get('query', '').strip()

        # If 'query' is '<all>', return all variations
        if query == '<all>':
            variations = Variation.query.all()
        elif query:
            # If the query is not empty, filter by name
            variations = Variation.query.filter(Variation.name.ilike(f"%{query}%")).all()
        else:
            return jsonify({"error": "Query parameter is required"}), 400

        if not variations:
            return jsonify({"message": "No variations found"}), 404

        result = [variation.to_dict() for variation in variations]
        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@variation_bp.route('/edit_variation/<string:variation_id>', methods=['PUT'])
def edit_variation(variation_id):
    """
    Edit a variation's name or options.
    """
    try:
        data = request.get_json()

        # Validate input
        new_name = data.get('name')
        new_options = data.get('options', [])

        if not new_name:
            return jsonify({"error": "Name is required"}), 400

        # Find the variation
        variation = Variation.query.get(variation_id)
        if not variation:
            return jsonify({"error": "Variation not found"}), 404

        # Update the variation name
        variation.name = new_name
        db.session.commit()

        VariationOption.query.filter_by(variation_id=variation_id).delete()

        # Update variation options
        if new_options:
            for option in new_options:
                option_value = option.get('value')
                option_id = option.get('id')

                if not option_value:
                    return jsonify({"error": "Option value is required"}), 400

                # Check if option_id exists and update the option value
                existing_option = VariationOption.query.get(option_id)
                if existing_option and existing_option.variation_id == variation_id:
                    # Update the existing option
                    existing_option.value = option_value
                else:
                    # Add a new option if no existing option matches the option_id
                    new_option = VariationOption(value=option_value, variation_id=variation_id)
                    db.session.add(new_option)

            db.session.commit()

        return jsonify({"message": "Variation updated successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500




@variation_bp.route('/delete_variation/<string:variation_id>', methods=['DELETE'])
def delete_variation(variation_id):
    """
    Delete a variation and its options.
    """
    try:
        # Find the variation
        variation = Variation.query.get(variation_id)
        if not variation:
            return jsonify({"error": "Variation not found"}), 404

        # Delete all associated options
        VariationOption.query.filter_by(variation_id=variation_id).delete()
        
        # Delete the variation
        db.session.delete(variation)
        db.session.commit()

        return jsonify({"message": "Variation deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


