from flask import Blueprint, request, jsonify
from models import db, Description
import uuid

# Create a Blueprint for handling descriptions
disc_bp = Blueprint('disc', __name__)

@disc_bp.route('/add_disc', methods=['POST'])
def add_disc():
    """
    Add a new description with an optional tag name.
    """
    try:
        data = request.json
        tag_name = data.get('tag_name', None)
        content = data.get('content')

        if not content:
            return jsonify({"error": "Content is required"}), 400

        new_description = Description(
            content=content,
            tag_name=tag_name
        )
        db.session.add(new_description)
        db.session.commit()

        return jsonify({"message": "Description added successfully", "id": new_description.id}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@disc_bp.route('/search', methods=['GET'])
def search_disc():
    """
    Search for descriptions by tag name.
    Query parameters:
      - query: The tag name to search for (required). Use '<all>' to fetch all descriptions.
    """
    try:
        query = request.args.get('query', '').strip()
        print(query)

        if not query:
            return jsonify({"error": "Tag name is required"}), 400

        if query == "<all>":  # If query is '<all>', fetch all descriptions
            descriptions = Description.query.all()
        else:
            descriptions = Description.query.filter(Description.tag_name.ilike(f"%{query}%")).all()

        if not descriptions:
            return jsonify({"message": "No descriptions found"}), 404

        result = [desc.to_dict() for desc in descriptions]
        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@disc_bp.route('/remove_disc/<string:disc_id>', methods=['DELETE'])
def remove_disc(disc_id):
    """
    Remove a description by its ID.
    """
    try:
        description = Description.query.get(disc_id)
        if not description:
            return jsonify({"error": "Description not found"}), 404

        db.session.delete(description)
        db.session.commit()

        return jsonify({"message": "Description removed successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@disc_bp.route('/edit_disc/<string:disc_id>', methods=['PUT'])
def edit_disc(disc_id):
    print("dcsdcs")
    """
    Edit an existing description by its ID.
    """
    try:
        data = request.json
        new_content = data.get('content')
        new_tag_name = data.get('tag_name', None)

        if not new_content:
            return jsonify({"error": "Content is required"}), 400

        description = Description.query.get(disc_id)
        if not description:
            return jsonify({"error": "Description not found"}), 404

        description.content = new_content
        description.tag_name = new_tag_name
        db.session.commit()
        print(description)
        return jsonify({"message": "Description updated successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
