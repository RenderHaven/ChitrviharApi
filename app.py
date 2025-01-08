from flask import Flask, render_template
from flask_cors import CORS
from models import db
from product import product_bp  # Import the Blueprint
from iteam import iteam_bp  # Import the Blueprint
import os

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}})

# Configure the database connection string from environment variables, fallback to SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Register Blueprints
app.register_blueprint(product_bp, url_prefix='/product')  # Prefixing all product routes with /product
app.register_blueprint(iteam_bp, url_prefix='/item')  # Prefixing all item routes with /item

# Ensure database tables are created
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0')
