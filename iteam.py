from flask import Blueprint, request, jsonify
from models import db, Product, ProductItem, ProToItem, ProductItemVariation, Variation, VariationOption,Description
import uuid
import base64
import cloudinary
import cloudinary.uploader

# Create the Blueprint for handling product items
item_bp = Blueprint('item', __name__)

# Configure Cloudinary
cloudinary.config(
    cloud_name="dimdoq0ng",
    api_key="324659127373814",
    api_secret="eUTC_Jxfvw95dkaCDN7yHEomugE"
)

@item_bp.route('/add_item', methods=['POST'])
def add_item():
    try:
        data = request.json
        product_id = data.get('product_id')
        item_name = data.get('name')
        price = data.get('price')
        description_content = data.get('description', '')
        quantity_in_stock = data.get('stock_quantity')
        base64_image = data.get('display_img', None)
        variation_value_ids = data.get('variation_value_ids', [])
        disc_id = data.get('disc_id')
        tag_name = data.get('tag_name', ' ')  # Tagname
        if  not item_name or price is None or quantity_in_stock is None:
            return jsonify({"error": "product_id, item name, price, and stock quantity are required"}), 400


        image_url = None
        if base64_image:
            try:
                file_to_upload = base64.b64decode(base64_image)
                upload_result = cloudinary.uploader.upload(file_to_upload)
                image_url = upload_result.get('secure_url')
            except Exception as e:
                return jsonify({"error": f"Failed to upload image: {str(e)}"}), 500

        new_item = ProductItem(
            name=item_name,
            price=price,
            stock_quantity=quantity_in_stock,
            image_url=image_url
        )
        db.session.add(new_item)
        db.session.commit()
        
        if(product_id):
            product = Product.query.get(product_id)
            if not product:
                return jsonify({"error": "Product not found"}), 404
            new_pro_to_item = ProToItem(
                i_id=new_item.i_id,
                p_id=product_id
            )
            db.session.add(new_pro_to_item)
            db.session.commit()

        for variation_id in variation_value_ids:
            new_relation = ProductItemVariation(product_item_id=new_item.i_id, variation_option_id=variation_id)
            db.session.add(new_relation)
        db.session.commit()

        # Check if a disc_id was provided
        if disc_id:
            # Use the existing description
            existing_description = Description.query.get(disc_id)
            if existing_description:
                new_item.disc_id = disc_id  # Assign the existing description to the product
                db.session.commit()
            else:
                return jsonify({"error": "Description not found for the provided disc_id"}), 404
        else:
            # Add a new description with tagline and content
            if description_content and tag_name:
                new_description = Description(
                    content=description_content,
                    tag_name=tag_name
                )
                db.session.commit()
                new_item.disc_id=new_description.id
                db.session.commit()

        return jsonify({
            "message": "Item added and linked to product successfully",
            "item_id": new_item.i_id,
            "product_id": product_id
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    

@item_bp.route('/edit_item', methods=['PUT'])
def edit_item():
    try:
        data = request.json
        item_id = data.get('item_id')
        item_name = data.get('name')
        price = data.get('price')
        quantity_in_stock = data.get('stock_quantity')
        base64_image = data.get('display_img', None)
        is_img_changed = data.get('isImgChanged', False)
        description_content = data.get('description', '')
        variation_value_ids = data.get('variation_value_ids', [])
        disc_id = data.get('disc_id')
        tag_name = data.get('tag_name', ' ')
        print(data)
        if not item_id:
            return jsonify({"error": "item_id is required"}), 400

        existing_item = ProductItem.query.get(item_id)
        if not existing_item:
            return jsonify({"error": "Item not found"}), 404

        if not item_name or price is None or quantity_in_stock is None:
            return jsonify({"error": "item name, price, and stock quantity are required"}), 400

        # Update item details
        existing_item.name = item_name
        existing_item.price = price
        existing_item.stock_quantity = quantity_in_stock

        # Update or retain image URL
        if is_img_changed:
            if base64_image:
                try:
                    file_to_upload = base64.b64decode(base64_image)
                    upload_result = cloudinary.uploader.upload(file_to_upload)
                    existing_item.image_url = upload_result.get('secure_url')
                except Exception as e:
                    return jsonify({"error": f"Failed to upload image: {str(e)}"}), 500
            else:
                existing_item.image_url = None  # Clear image if no new image is provided

        # Update description
        if disc_id:
            existing_description = Description.query.get(disc_id)
            if existing_description:
                existing_item.disc_id = disc_id
            else:
                return jsonify({"error": "Description not found for the provided disc_id"}), 404
        elif description_content and tag_name:
            new_description = Description(
                content=description_content,
                tag_name=tag_name
            )
            db.session.add(new_description)
            db.session.commit()
            existing_item.disc_id = new_description.id
        # Remove existing variation relationships
        ProductItemVariation.query.filter_by(product_item_id=item_id).delete()
        # Add new variation relationships
        for variation_id in variation_value_ids:
            new_relation = ProductItemVariation(product_item_id=item_id, variation_option_id=variation_id)
            db.session.add(new_relation)

        db.session.commit()

        return jsonify({
            "message": "Item updated successfully",
            "item_id": item_id
        }), 200

    except Exception as e:
        db.session.rollback()
        print(e)
        return jsonify({"error": str(e)}), 500


@item_bp.route('/remove_item/<string:item_id>', methods=['DELETE'])
def remove_item(item_id):
    try:
        item = ProductItem.query.get(item_id)
        if not item:
            return jsonify({"error": "Item not found"}), 404

        ProToItem.query.filter_by(i_id=item_id).delete()
        db.session.delete(item)
        db.session.commit()

        return jsonify({"message": "Item removed successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@item_bp.route('/get_products_by_item/<string:item_id>', methods=['GET'])
def get_products_by_item_id(item_id):
    try:
        item = ProductItem.query.filter_by(i_id=item_id).first()
        if not item:
            return jsonify({"error": "Product not found"}), 404

        products = Product.query.join(ProToItem, ProToItem.p_id == Product.p_id)\
            .filter(ProToItem.i_id == item_id).all()

        products_data = [{'p_id': product.p_id, 'name': product.name} for product in products]

        return jsonify({
            "item_id": item.i_id,
            "product_name": item.name,
            "products": products_data
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@item_bp.route('/get_item/<string:item_id>/<string:all>', methods=['GET'])
def get_item_by_id(item_id, all='false'):
    try:
        item = ProductItem.query.filter_by(i_id=item_id).first()
        if not item:
            return jsonify({"error": "Item not found"}), 404

        variations = []
        # if all.lower() == 'true':
        #     for variation_config in item.variations:
        #         var_option = VariationOption.query.filter_by(id=variation_config.variation_option_id).first()
        #         if(var_option==None):continue
        #         var = Variation.query.filter_by(id=var_option.variation_id).first()
        #         variations.append({
        #             'name': var.name,
        #             'value': var_option.value,
        #             'option_id': var_option.id
        #         })

        item_data=item.to_dict()

        return jsonify(item_data), 200

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

@item_bp.route('/search', methods=['GET'])
def search_items():
    try:
        query = request.args.get('query', '').strip()
        if not query:
            return jsonify({"error": "Query parameter is required"}), 400

        if query == '<all>':
            items = ProductItem.query.all()
        else:
            items = ProductItem.query.filter(
                (ProductItem.name.ilike(f"%{query}%"))
            ).all()

        search_results = [{
            "i_id": item.i_id,
            "name": item.name,
            "price": item.price,
        } for item in items]

        return jsonify(search_results), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@item_bp.route('/add_items_to_product/<string:product_id>', methods=['POST'])
def add_items_to_product(product_id):
    try:
        item_ids = request.json.get('item_ids', [])
        product = Product.query.get_or_404(product_id)

        for item_id in item_ids:
            product_item = ProductItem.query.get(item_id)
            if product_item and product_item not in product.product_items:
                product.product_items.append(product_item)

        db.session.commit()
        return jsonify({'message': 'Items added to product successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@item_bp.route('/get_items_by_filter', methods=['GET'])
def get_items():
    try:
        product_ids = request.args.getlist('ProductIds')

        query = db.session.query(ProductItem)

        if product_ids and 'all' not in product_ids:
            query = query.join(ProductItem.products).filter(Product.p_id.in_(product_ids))

        items = query.all()

        result = []
        for item in items:
            result.append(item.to_small_dict())

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
