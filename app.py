from flask import Flask, render_template
from flask_cors import CORS
from models import db,Category,Product
from product import product_bp  # Import the Blueprint
from iteam import item_bp  # Import the Blueprint
import os

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}})

# Configure the database connection string from environment variables, fallback to SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', "sqlite:///local_database.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Register Blueprints
app.register_blueprint(product_bp, url_prefix='/product')  # Prefixing all product routes with /product
app.register_blueprint(item_bp, url_prefix='/item')  # Prefixing all item routes with /item

# Ensure database tables are created
@app.route('/restart')
def restart():
    with app.app_context():
        db.drop_all()
        db.create_all()
        new_category = Category(
                c_id='Cat1',
                pc_id=None,  # Parent category ID
                name='Home',
        )
        db.session.add(new_category)
        new_product = Product(
                p_id='Home',
                name='Home',
                c_id='Cat1',  # Assign the category ID
        )
        db.session.add(new_product)
        db.session.commit()
    return 'done'

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0')
