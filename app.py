from flask import Flask, render_template
from flask_cors import CORS
from models import db, Category, Product
from user.routes import user_bp
from product import product_bp  # Import the Blueprint
from iteam import item_bp  # Import the Blueprint
from category import category_bp
from variation import variation_bp
from orders import orders_bp
from disc import disc_bp
import os
from flask_migrate import Migrate
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)


# Enable CORS for all origins (ensure this is intentional for security reasons)
CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"], "allow_headers": ["Content-Type"]}})



# Configure the database connection string from environment variables, fallback to SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', "postgresql://postgres:vikramisdevloper@database-1.cv4mksa0gyui.eu-north-1.rds.amazonaws.com:5432/postgres")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the app with SQLAlchemy
db.init_app(app)
migrate = Migrate(app, db)


# Register Blueprints with proper url_prefix
app.register_blueprint(product_bp, url_prefix='/product')
app.register_blueprint(item_bp, url_prefix='/item')
app.register_blueprint(user_bp, url_prefix='/user')
app.register_blueprint(category_bp, url_prefix='/category')
app.register_blueprint(variation_bp, url_prefix='/variation')
app.register_blueprint(disc_bp, url_prefix='/description')
app.register_blueprint(orders_bp, url_prefix='/order')

# Ensure database tables are created (development only)
# @app.route('/restart')
# def restart():
#     # Ensure to comment or protect this in production
#     if app.config['ENV'] == 'development':
#         with app.app_context():
#             db.drop_all()  # Be cautious, this will delete all data
#             db.create_all()  # Recreate tables
#             # Example: adding initial categories and products
#             new_category = Category(c_id='Cat1', pc_id=None, name='Home')
#             db.session.add(new_category)
#             new_product = Product(p_id='Home', name='Home', c_id='Cat1')
#             db.session.add(new_product)
#             db.session.commit()
#             logging.info('Database reset and initial data added.')
#     return 'done'

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    with app.app_context():  # This establishes an application context
        db.create_all() 
        migrate.init_app(app, db)
    # Running the app with debug mode
    app.run(host='0.0.0.0', debug=True)
