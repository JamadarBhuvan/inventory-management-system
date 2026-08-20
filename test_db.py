from app import app, db, Product

with app.app_context():
    p = Product(name="Test Widget", sku="TW-001", quantity=10, price=99.99)
    db.session.add(p)
    db.session.commit()

    products = Product.query.all()
    for prod in products:
        print(prod.id, prod.name, prod.quantity, prod.price)
