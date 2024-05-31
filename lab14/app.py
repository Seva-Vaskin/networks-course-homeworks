import os
import random
import string
from functools import wraps
from flask import Flask, jsonify, request
from werkzeug.exceptions import NotFound, Unauthorized

app = Flask(__name__)

products = dict()
users = dict()
tokens = dict()
next_product_id = 1


def generate_token():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=32))


@app.route('/user/sign-up', methods=['POST'])
def sign_up():
    user_data = request.json
    email = user_data.get("email")
    password = user_data.get("password")
    if email in users:
        return jsonify({"message": "User already exists"}), 400
    users[email] = {"email": email, "password": password}
    return jsonify({"message": "User registered successfully"}), 201


@app.route('/user/sign-in', methods=['POST'])
def sign_in():
    user_data = request.json
    email = user_data.get("email")
    password = user_data.get("password")
    user = users.get(email)
    if not user or user["password"] != password:
        return jsonify({"message": "Invalid credentials"}), 401
    token = generate_token()
    tokens[token] = email
    return jsonify({"token": token}), 200


def get_token():
    auth_header = request.headers.get('Authorization')
    if auth_header:
        try:
            proto, token = auth_header.split(maxsplit=1)
            if proto != 'Bearer':
                raise Unauthorized(description=f"Expected Bearer auth type, got {proto}")
            return token
        except ValueError:
            raise Unauthorized(description="Invalid Authorization header format")
    return None


def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = get_token()
        if not token or token not in tokens:
            raise Unauthorized(description="Token is missing or invalid")
        return f(*args, **kwargs)
    return decorator


def get_user_from_token(token):
    return tokens.get(token)


@app.route('/product', methods=['POST'])
def add_product():
    global next_product_id
    product_data = request.json
    token = get_token()
    email = get_user_from_token(token) if token else None

    # Определяем значение public по умолчанию
    if token:
        product_public = product_data.get("public", False)
    else:
        product_public = product_data.get("public", True)

    # Проверяем, чтобы продукт без токена не мог быть приватным
    if not token and not product_public:
        return jsonify({"message": "Public product must be true if no token is provided"}), 400

    product = {
        "id": next_product_id,
        "name": product_data["name"],
        "description": product_data["description"],
        "public": product_public,
        "owner": email
    }

    products[next_product_id] = product
    next_product_id += 1
    return jsonify(product), 201


@app.route('/product/<int:product_id>', methods=['GET'])
def get_product(product_id):
    token = get_token()
    email = get_user_from_token(token) if token else None

    product = products.get(product_id, None)
    if product is None or (not product['public'] and product['owner'] != email):
        raise NotFound(description="Product not found")
    return jsonify(product)


@app.route('/product/<int:product_id>', methods=['PUT'])
@token_required
def update_product(product_id):
    token = get_token()
    email = get_user_from_token(token)

    product = products.get(product_id, None)
    if product is None or (product['owner'] != email):
        raise NotFound(description="Product not found or not authorized")

    product_data = request.json
    product['name'] = product_data.get('name', product['name'])
    product['description'] = product_data.get('description', product['description'])
    product['public'] = product_data.get('public', product['public'])
    return jsonify(product)


@app.route('/product/<int:product_id>', methods=['DELETE'])
@token_required
def delete_product(product_id):
    global products
    token = get_token()
    email = get_user_from_token(token)

    product = products.get(product_id, None)
    if product is None or (product['owner'] != email):
        raise NotFound(description="Product not found or not authorized")

    products.pop(product_id)
    return jsonify(product)


@app.route('/products', methods=['GET'])
def list_products():
    token = get_token()
    email = get_user_from_token(token) if token else None

    if email:
        filtered_products = [product for product in products.values() if product['public'] or product['owner'] == email]
    else:
        filtered_products = [product for product in products.values() if product['public']]

    return jsonify(filtered_products)


@app.errorhandler(NotFound)
def handle_not_found(error):
    response = jsonify({"message": error.description})
    response.status_code = 404
    return response


@app.errorhandler(Unauthorized)
def handle_unauthorized(error):
    response = jsonify({"message": error.description})
    response.status_code = 401
    return response


if __name__ == '__main__':
    app.run(debug=True)
