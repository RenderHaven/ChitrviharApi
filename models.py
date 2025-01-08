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

    cat_id = db.Column(db.String(36), ForeignKey('categories.c_id'), nullable=True)
    category = relationship("Category", back_populates="products")

    disc = db.Column(db.String(500))
    display_img = db.Column(db.LargeBinary)

    pro_to_iteams = relationship('ProToIteam', back_populates="product")


class ProductIteam(db.Model):
    __tablename__ = 'product_items'

    i_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(200), nullable=False)
    img = db.Column(db.LargeBinary)
    price = db.Column(db.Integer, nullable=False, default=0)
    disc = db.Column(db.String(500))
    qty_in_stock = db.Column(db.Integer, nullable=False, default=0)

    pro_to_iteams = relationship('ProToIteam', back_populates="product_iteam")


class ProToIteam(db.Model):
    __tablename__ = 'product_to_items'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    i_id = db.Column(db.String(36), ForeignKey('product_items.i_id'))
    p_id = db.Column(db.String(36), ForeignKey('products.p_id'))

    product = relationship("Product", back_populates="pro_to_iteams")
    product_iteam = relationship("ProductIteam", back_populates="pro_to_iteams")


class Variation(db.Model):
    __tablename__ = 'variations'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    c_id = db.Column(db.String(36), ForeignKey('categories.c_id'))
    name = db.Column(db.String(200), nullable=False)

    category = relationship("Category")


class VariationOption(db.Model):
    __tablename__ = 'variation_options'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    var_id = db.Column(db.Integer, ForeignKey('variations.id'))
    value = db.Column(db.String(200), nullable=False)

    variation = relationship("Variation")
