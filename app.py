from flask import Flask, render_template
from flask_cors import CORS
from models import db
from product import product_bp  # Import the Blueprint
from iteam import iteam_bp  # Import the Blueprint

app = Flask(__name__)

CORS(app)
# Configure SQLite connection string
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Register the Blueprint
app.register_blueprint(product_bp, url_prefix='/product')  # Prefixing all product routes with /product
app.register_blueprint(iteam_bp, url_prefix='/item')  # Prefixing all product routes with /product

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
