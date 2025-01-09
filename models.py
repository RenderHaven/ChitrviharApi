import uuid
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, Column, Integer, String, Float, Boolean
from sqlalchemy.orm import relationship

db = SQLAlchemy()

class Category(db.Model):
    __tablename__ = 'categories'

    c_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    pc_id = db.Column(db.String(36), ForeignKey('categories.c_id'), nullable=True)
    name = db.Column(db.String(200), nullable=False)

    subcategories = relationship("Category", backref="parent", remote_side=[c_id])
    products = relationship("Product", back_populates="category")


class Product(db.Model):
    __tablename__ = 'products'

    p_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(200), nullable=False)
    disc = db.Column(db.String(500))
    image_url = db.Column(db.String(500))  # Store image URL instead of binary data

    c_id = db.Column(db.String(36), ForeignKey('categories.c_id'), nullable=False)
    category = relationship("Category", back_populates="products")

    product_items = relationship('ProductItem', secondary='product_to_items', back_populates="products")


class ProductItem(db.Model):
    __tablename__ = 'product_items'

    i_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(200), nullable=False)
    image_url = db.Column(db.String(500))  # Store image URL instead of binary data
    price = db.Column(db.Float, nullable=False, default=0.0)
    disc = db.Column(db.String(500))
    stock_quantity = db.Column(db.Integer, nullable=False, default=0)

    products = relationship('Product', secondary='product_to_items', back_populates="product_items")


class ProToItem(db.Model):
    __tablename__ = 'product_to_items'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    p_id = db.Column(db.String(36), ForeignKey('products.p_id'), nullable=False)
    i_id = db.Column(db.String(36), ForeignKey('product_items.i_id'), nullable=False)


class Variation(db.Model):
    __tablename__ = 'variations'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    c_id = db.Column(db.String(36), ForeignKey('categories.c_id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)

    category = relationship("Category")
    options = relationship("VariationOption", back_populates="variation", cascade="all, delete-orphan")


class VariationOption(db.Model):
    __tablename__ = 'variation_options'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    variation_id = db.Column(db.Integer, ForeignKey('variations.id'), nullable=False)
    value = db.Column(db.String(200), nullable=False)

    variation = relationship("Variation", back_populates="options")
