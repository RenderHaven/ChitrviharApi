from models import db,Product,Category
from app import app

product_data = {
    "Pro1": {
        "PId": 'Home',
        "name": "Home",
    },
}

category_data={
    "Cat1": {
        "CId": 'Cat1',
        "PId": 'Null',
        "name": "Home",
        "values":"S,M,L,XL,XXL"
    },
    "Cat2": {
        "CId": 'Cat2',
        "PId": 'Cat1',
        "name": "Gender",
        "values":"RED,BLACK,WHITE"
    },
    "Cat3": {
        "CId": 'Cat3',
        "PId": 'Cat1',
        "name": "Size",
        "values":"S,M,L,XL,XXL"
    },
    "Cat4": {
        "CId": 'Cat4',
        "PId": 'Cat1',
        "name": "Colour",
        "values":"RED,BLACK,WHITE"
    },
}

iteam_data={
    
}

def insert_data():
    db.create_all()
    #catagory
    for id, info in category_data.items():
        new_row = Category(
            c_id=id,
            pc_id=info['PId'],
            name=info['name'],
        )
        db.session.add(new_row)
    # Insert events
    for evt_id, evt_info in product_data.items():
        new_product = Product(
            p_id=evt_info['PId'],
            name=evt_info['name'],
        )
        db.session.add(new_product)
    db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        db.drop_all()
        db.create_all()
        insert_data()
    print("Data inserted successfully")
