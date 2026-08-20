import os
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    sku = db.Column(db.String(50), unique=True, nullable=False)
    quantity = db.Column(db.Integer, default=0, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def __repr__(self):
        return f'<Product {self.sku}>'

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"}), 200

@app.route('/products', methods=['POST'])
def create_product():
    data = request.get_json()

    new_product = Product(
        name=data['name'],
        sku=data['sku'],
        quantity=data['quantity'],
        price=data['price']
    )

    db.session.add(new_product)
    db.session.commit()

    return {"message": "Product created", "id": new_product.id}, 201

@app.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()

    result = []
    for p in products:
        result.append({
            "id": p.id,
            "name": p.name,
            "sku": p.sku,
            "quantity": p.quantity,
            "price": str(p.price)
        })

    return jsonify(result), 200

@app.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get(product_id)

    if not product:
        return jsonify({"error": "Product not found"}), 404

    return jsonify({
        "id": product.id,
        "name": product.name,
        "sku": product.sku,
        "quantity": product.quantity,
        "price": str(product.price)
    }), 200

@app.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    product = Product.query.get(product_id)

    if not product:
        return jsonify({"error": "Product not found"}), 404

    data = request.get_json()

    product.name = data.get('name', product.name)
    product.sku = data.get('sku', product.sku)
    product.quantity = data.get('quantity', product.quantity)
    product.price = data.get('price', product.price)

    db.session.commit()

    return jsonify({"message": "Product updated"}), 200

@app.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    product = Product.query.get(product_id)

    if not product:
        return jsonify({"error": "Product not found"}), 404

    db.session.delete(product)
    db.session.commit()

    return jsonify({"message": "Product deleted"}), 200

if __name__ == '__main__':
    app.run(debug=True)