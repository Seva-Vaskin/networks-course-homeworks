from flask import Flask, jsonify, request
from werkzeug.exceptions import NotFound

app = Flask(__name__)

products = dict()
next_id = 1


@app.route('/product', methods=['POST'])
def add_product():
    global next_id
    product_data = request.json
    product = {"id": next_id, "name": product_data["name"], "description": product_data["description"]}
    products[next_id] = product
    next_id += 1
    return jsonify(product), 201


@app.route('/product/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = products.get(product_id, None)
    if product is None:
        raise NotFound(description="Product not found")
    return jsonify(product)


@app.route('/product/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    product = products.get(product_id, None)
    if product is None:
        raise NotFound(description="Product not found")
    product_data = request.json
    product['name'] = product_data.get('name', product['name'])
    product['description'] = product_data.get('description', product['description'])
    return jsonify(product)


@app.route('/product/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    global products
    product = products.get(product_id, None)
    if product is None:
        raise NotFound(description="Product not found")
    products.pop(product_id)
    return jsonify(product)


@app.route('/products', methods=['GET'])
def list_products():
    return jsonify(list(products.values()))


@app.errorhandler(NotFound)
def handle_not_found(error):
    response = jsonify({"message": error.description})
    response.status_code = 404
    return response


if __name__ == '__main__':
    app.run(debug=True)
