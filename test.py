from models import db, Product, Category
from app import app

# Sample product data
product_data = {
    "Pro1": {
        "PId": 'Pro1',
        "name": "Home",
        "CId": 'Cat1',  # Link this product to the "Home" category
    },
}

# Sample category data
category_data = {
    "Cat1": {
        "CId": 'Cat1',
        "PId": None,  # Parent ID is None for top-level categories
        "name": "Home",
    },
    "Cat2": {
        "CId": 'Cat2',
        "PId": 'Cat1',  # Parent ID is 'Cat1'
        "name": "Gender",
    },
    "Cat3": {
        "CId": 'Cat3',
        "PId": 'Cat1',  # Parent ID is 'Cat1'
        "name": "Size",
    },
    "Cat4": {
        "CId": 'Cat4',
        "PId": 'Cat1',  # Parent ID is 'Cat1'
        "name": "Colour",
    },
}

def insert_data():
    # Ensure the database schema exists
    db.create_all()

    # Insert categories
    for id, info in category_data.items():
        new_category = Category(
            c_id=info['CId'],
            pc_id=info['PId'],  # Parent category ID
            name=info['name'],
        )
        db.session.add(new_category)

    # Insert products
    for id, info in product_data.items():
        new_product = Product(
            p_id=info['PId'],
            name=info['name'],
            c_id=info['CId'],  # Assign the category ID
        )
        db.session.add(new_product)

    # Commit all changes to the database
    db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        db.drop_all()  # Drops all tables to start fresh
        db.create_all()  # Re-creates the tables
        insert_data()  # Inserts the sample data
    print("Data inserted successfully")
