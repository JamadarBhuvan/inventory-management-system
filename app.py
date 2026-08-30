import os
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError  # NEW: to catch duplicate SKU errors
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt
from flasgger import Swagger

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY")
jwt = JWTManager(app)

from flask_migrate import Migrate

migrate = Migrate(app, db)

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "StockFlow API",
        "description": "Inventory Management System API",
        "version": "0.0.1"
    },
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT Authorization header using the Bearer scheme. Example: \"Bearer {token}\""
        }
    }
}

swagger = Swagger(app, template=swagger_template)

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



class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='staff')  # 'admin' or 'staff'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)  
    
from flask import request, jsonify

@app.route('/login', methods=['POST'])
def login():
    """
    Log in and get a JWT access token
    ---
    tags:
      - Auth
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - username
            - password
          properties:
            username:
              type: string
              example: "admin"
            password:
              type: string
              example: "yourpassword"
    responses:
      200:
        description: Login successful, returns JWT
        schema:
          type: object
          properties:
            access_token:
              type: string
              example: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
      400:
        description: Missing username or password
      401:
        description: Invalid username or password
    """
    data = request.get_json()

    if not data or not data.get('username') or not data.get('password'):
        return jsonify({"error": "username and password required"}), 400

    user = User.query.filter_by(username=data['username']).first()

    if not user or not user.check_password(data['password']):
        return jsonify({"error": "invalid username or password"}), 401

    access_token = create_access_token(
        identity=user.username,
        additional_claims={"role": user.role}
    )

    return jsonify({"access_token": access_token}), 200

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check
    ---
    tags:
      - System
    responses:
      200:
        description: Service is up and running
        schema:
          type: object
          properties:
            status:
              type: string
              example: "ok"
    """
    return jsonify({"status": "ok"}), 200


@app.route('/products', methods=['POST'])
@jwt_required()
def create_product():
    """
    Create a new product (admin only)
    ---
    tags:
      - Products

    security:
    - Bearer: []

    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - name
            - sku
            - quantity
            - price
          properties:
            name:
              type: string
              example: "Wireless Mouse"
            sku:
              type: string
              example: "WM-1001"
            quantity:
              type: integer
              example: 50
            price:
              type: number
              example: 499.99
    responses:
      201:
        description: Product created successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Product created"
            id:
              type: integer
              example: 12
      400:
        description: Missing or invalid fields
      409:
        description: Product with this SKU already exists
    """
    data = request.get_json(silent=True)
    ...
    # NEW: bouncer check 1 - is it even JSON?
    if data is None:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    # NEW: bouncer check 2 - required fields present?
    required_fields = ['name', 'sku', 'quantity', 'price']
    missing = [f for f in required_fields if f not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    name = data.get('name')
    sku = data.get('sku')
    quantity = data.get('quantity')
    price = data.get('price')

    # NEW: bouncer check 3 - are values sane?
    if not isinstance(name, str) or not name.strip():
        return jsonify({"error": "Name must be a non-empty string"}), 400

    if not isinstance(sku, str) or not sku.strip():
        return jsonify({"error": "SKU must be a non-empty string"}), 400

    if not isinstance(quantity, int) or quantity < 0:
        return jsonify({"error": "Quantity must be a non-negative integer"}), 400

    if not isinstance(price, (int, float)) or price < 0:
        return jsonify({"error": "Price must be a non-negative number"}), 400

    new_product = Product(
        name=name.strip(),
        sku=sku.strip(),
        quantity=quantity,
        price=price
    )

    db.session.add(new_product)

    # NEW: catch duplicate SKU instead of crashing
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": f"Product with SKU '{sku}' already exists"}), 409

    return jsonify({"message": "Product created", "id": new_product.id}), 201


@app.route('/products', methods=['GET'])
def get_products():
    """
    Get all products
    ---
    tags:
      - Products
    responses:
      200:
        description: A list of all products
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
                example: 1
              name:
                type: string
                example: "Wireless Mouse"
              sku:
                type: string
                example: "WM-1001"
              quantity:
                type: integer
                example: 50
              price:
                type: string
                example: "499.99"
    """
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
    """
    Get a single product by ID
    ---
    tags:
      - Products
    parameters:
      - name: product_id
        in: path
        type: integer
        required: true
        description: ID of the product to fetch
    responses:
      200:
        description: The product with the given ID
        schema:
          type: object
          properties:
            id:
              type: integer
              example: 1
            name:
              type: string
              example: "Wireless Mouse"
            quantity:
              type: integer
              example: 50
            price:
              type: number
              example: 499.99
      404:
        description: Product not found
    """
    # ...your existing code stays exactly as is
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
@jwt_required()
def update_product(product_id):
    """
    Update a product (admin only, partial update supported)
    ---
    tags:
      - Products
    security:
      - Bearer: []
    parameters:
      - in: path
        name: product_id
        type: integer
        required: true
        example: 1
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
              example: "Wireless Mouse V2"
            sku:
              type: string
              example: "WM-1002"
            quantity:
              type: integer
              example: 30
            price:
              type: number
              example: 549.99
    responses:
      200:
        description: Product updated successfully
      400:
        description: Invalid JSON or invalid field values
      404:
        description: Product not found
      409:
        description: Product with this SKU already exists
    """
    product = Product.query.get(product_id)
    ...
    if not product:
        return jsonify({"error": "Product not found"}), 404

    data = request.get_json(silent=True)  # NEW
    if data is None:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    # NEW: validate only the fields actually sent (partial update)
    if 'name' in data:
        if not isinstance(data['name'], str) or not data['name'].strip():
            return jsonify({"error": "Name must be a non-empty string"}), 400
        product.name = data['name'].strip()

    if 'sku' in data:
        if not isinstance(data['sku'], str) or not data['sku'].strip():
            return jsonify({"error": "SKU must be a non-empty string"}), 400
        product.sku = data['sku'].strip()

    if 'quantity' in data:
        if not isinstance(data['quantity'], int) or data['quantity'] < 0:
            return jsonify({"error": "Quantity must be a non-negative integer"}), 400
        product.quantity = data['quantity']

    if 'price' in data:
        if not isinstance(data['price'], (int, float)) or data['price'] < 0:
            return jsonify({"error": "Price must be a non-negative number"}), 400
        product.price = data['price']

    # NEW: catch duplicate SKU on update too
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": f"Product with SKU '{data.get('sku')}' already exists"}), 409

    return jsonify({"message": "Product updated"}), 200

@app.route('/products/<int:product_id>', methods=['DELETE'])
@jwt_required()
def delete_product(product_id):
    """
    Delete a product (admin only)
    ---
    tags:
      - Products

    security:
      - Bearer: []

    parameters:
      - in: path
        name: product_id
        type: integer
        required: true
        example: 1
    responses:
      200:
        description: Product deleted successfully
      404:
        description: Product not found
    """
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    db.session.delete(product)
    db.session.commit()

    return jsonify({"message": "Product deleted"}), 200


# NEW: safety net for anything that slips through
@app.errorhandler(500)
def server_error(e):
    db.session.rollback()
    return jsonify({"error": "Internal server error"}), 500

@app.route('/register', methods=['POST'])
def register():
    """
    Register a new user
    ---
    tags:
      - Auth
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - username
            - password
          properties:
            username:
              type: string
              example: "john_doe"
            password:
              type: string
              example: "strongpassword123"
    responses:
      201:
        description: User registered successfully
      400:
        description: Invalid input (missing or empty username/password)
      409:
        description: Username already taken
    """
    data = request.get_json(silent=True)
    # ...rest of your existing code stays exactly as is
    if data is None:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    username = data.get('username')
    password = data.get('password')

    if not isinstance(username, str) or not username.strip():
        return jsonify({"error": "Username must be a non-empty string"}), 400

    if not isinstance(password, str) or not password.strip():
        return jsonify({"error": "Password must be a non-empty string"}), 400

    # check if username already exists
    existing_user = User.query.filter_by(username=username.strip()).first()
    if existing_user:
        return jsonify({"error": f"Username '{username}' already taken"}), 409

    new_user = User(username=username.strip(), role='staff')  # always staff, no exceptions
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully", "username": new_user.username}), 201


if __name__ == '__main__':
    app.run(debug=True)