import uuid
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, Column, Integer, String, Float
from sqlalchemy.orm import relationship

db = SQLAlchemy()


class Description(db.Model):
    __tablename__ = 'descriptions'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    content = db.Column(db.String(1000), nullable=False)  # The description content
    tag_name = db.Column(db.String(50), nullable=False)  # Optional tag name for the description

    def to_dict(self):
        return {
            "id": self.id,
            "content": self.content,
            "tag_name": self.tag_name,  # Include the tag name in the serialized data
        }
    


class Category(db.Model):
    __tablename__ = 'categories'

    c_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    pc_id = db.Column(db.String(36), ForeignKey('categories.c_id'), nullable=True)
    name = db.Column(db.String(200), nullable=False)

    subcategories = relationship("Category", backref="parent", remote_side=[c_id])
    products = relationship("Product", back_populates="category")

    def to_dict(self):
        return {
            "c_id": self.c_id,
            "pc_id": self.pc_id,
            "name": self.name,
            "products_names": [product.name for product in self.products],
        }


class Product(db.Model):
    __tablename__ = 'products'

    p_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(200), nullable=False)
    disc_id = db.Column(db.String(36), ForeignKey('descriptions.id'), nullable=True)  # Reference to Description
    image_url = db.Column(db.String(500))
    c_id = db.Column(db.String(36), ForeignKey('categories.c_id'), nullable=False)

    category = relationship("Category", back_populates="products")
    description = relationship("Description", backref="products")  # Relationship with Description table
    Type = db.Column(db.String(200), nullable=False, default="Other")
    discount = db.Column(db.Float, nullable=False, default=0.0)
    product_items = relationship('ProductItem', secondary='product_to_items', back_populates="products")

    def to_dict(self):
        return {
            "p_id": self.p_id,
            "c_id" :self.c_id,
            "name": self.name,
            "description": self.description.content if self.description else None,  # Use the Description relation
            "tag_name": self.description.tag_name if self.description else None,
            'disc_id': self.description.id if self.description else None,
            "image_url": self.image_url,
            "Type": self.Type,
            "discount": self.discount,
            # "category": self.category.to_dict() if self.category else None,
            "items_id": [item.i_id for item in self.product_items],
        }


class ProductItem(db.Model):
    __tablename__ = 'product_items'

    i_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(200), nullable=False)
    image_url = db.Column(db.String(500))
    price = db.Column(db.Float, nullable=False, default=0.0)
    disc_id = db.Column(db.String(36), ForeignKey('descriptions.id'), nullable=True)  # Reference to Description
    stock_quantity = db.Column(db.Integer, nullable=False, default=0)
    
    
    description = relationship("Description", backref="product_items")  # Relationship with Description table
    products = relationship('Product', secondary='product_to_items', back_populates="product_items")
    variations = relationship("ProductItemVariation", back_populates="product_item", cascade="all, delete-orphan")


    def to_dict(self):
        return {
            "i_id": self.i_id,
            "name": self.name,
            "image_url": self.image_url,
            "price": self.price,
            "description": self.description.content if self.description else None,  # Use the Description relation
            "tag_name": self.description.tag_name if self.description else None,
            'disc_id': self.description.id if self.description else None,
            "stock_quantity": self.stock_quantity,
            "products_id": [product.p_id for product in self.products],
            "variations": [variation.variation_option.to_dict() for variation in self.variations if variation.variation_option],
        }
    def to_small_dict(self):
        return {
            "i_id": self.i_id,
            "name": self.name,
            "image_url": self.image_url,
            "price": self.price,
            "variations": [variation.variation_option.to_dict() for variation in self.variations if variation.variation_option],
        }




class ProToItem(db.Model):
    __tablename__ = 'product_to_items'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    p_id = db.Column(db.String(36), ForeignKey('products.p_id'), nullable=False)
    i_id = db.Column(db.String(36), ForeignKey('product_items.i_id'), nullable=False)


class Variation(db.Model):
    __tablename__ = 'variations'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(200), nullable=False)

    options = relationship("VariationOption", back_populates="variation", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "options": [option.to_dict() for option in self.options],
        }


class VariationOption(db.Model):
    __tablename__ = 'variation_options'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    variation_id = db.Column(db.String(36), ForeignKey('variations.id'), nullable=False)
    value = db.Column(db.String(200), nullable=False)

    variation = relationship("Variation", back_populates="options")
    product_items = relationship("ProductItemVariation", back_populates="variation_option" ,cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "variation_id": self.variation_id,
            "value": self.value,
            "variation_name": self.variation.name if self.variation else None,
        }


class ProductItemVariation(db.Model):
    __tablename__ = 'product_item_variations'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_item_id = db.Column(db.String(36), ForeignKey('product_items.i_id'), nullable=False)
    variation_option_id = db.Column(db.String(36), ForeignKey('variation_options.id'), nullable=False)

    product_item = relationship("ProductItem", back_populates="variations")
    variation_option = relationship("VariationOption", back_populates="product_items")

    def to_dict(self):
        return {
            "id": self.id,
            "product_item_id": self.product_item_id,
            "variation_option_id": self.variation_option_id,
            "product_item": self.product_item.to_dict() if self.product_item else None,
            "variation_option": self.variation_option.to_dict() if self.variation_option else None,
        }


class User(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(200), nullable=True)
    email = db.Column(db.String(200), nullable=True)
    number = db.Column(db.String(15), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False,default='123456')
    addresses = db.relationship('Address', backref='user', lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "number": self.number,
            "addresses": [address.to_dict() for address in self.addresses],
        }


class Address(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    street = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    zip_code = db.Column(db.String(20), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "street": self.street,
            "city": self.city,
            "state": self.state,
            "zip_code": self.zip_code,
        }


class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)  # Reference to User
    i_id = db.Column(db.String(36), db.ForeignKey('product_items.i_id'), nullable=False)  # Reference to ProductItem
    address_id = db.Column(db.String(36), db.ForeignKey('address.id'), nullable=True)  # Reference to Address
    quantity = db.Column(db.Integer, nullable=False, default=1)
    status = db.Column(db.String(50), nullable=False, default='IN_CART')  # Status of the order
    datetime = db.Column(db.DateTime, nullable=False, default=db.func.now())  # Timestamp for the order

    user = relationship('User', backref='orders')  # Relationship with User
    item = relationship('ProductItem', backref='orders')  # Relationship with ProductItem
    address = relationship('Address', backref='orders')  # Relationship with Address

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "i_id": self.i_id,
            "address_id": self.address_id,  # Include the address_id
            "item_name": self.item.name if self.item else None,
            "quantity": self.quantity,
            "status": self.status,
            "datetime": self.datetime.isoformat() if self.datetime else None,
            "user": self.user.to_dict() if self.user else None,  # Include user information
            "address": self.address.to_dict() if self.address else None,  # Include address information
        }

    def to_card_dict(self):
        return {
            "name": self.item.name if self.item else "Unknown Item",
            "description": self.item.description.content if self.item and self.item.description else "No description",
            "price": self.item.price if self.item else 0,
            "originalPrice": self.item.price + 200,  # Example of calculating original price
            "saved": 200,  # Example of static discount
            "image": self.item.image_url if self.item else None,
            "quantity": self.quantity,
            "size": "M",  # If size is part of `variations`, update dynamically
            "left": self.item.stock_quantity if self.item else 0,
        }


