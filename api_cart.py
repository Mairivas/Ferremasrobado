from flask import Flask, request, jsonify, session
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = 'ferremas_secret'
CORS(app)

@app.route('/api/cart', methods=['POST'])
def add_to_cart():
    producto = request.json
    carrito = session.get('carrito', [])
    # Buscar si ya existe el producto
    for item in carrito:
        if item['codigo'] == producto['codigo']:
            item['cantidad'] += 1
            break
    else:
        carrito.append(producto)
    session['carrito'] = carrito
    return jsonify({'ok': True, 'carrito': carrito})

@app.route('/api/cart', methods=['GET'])
def get_cart():
    carrito = session.get('carrito', [])
    return jsonify({'carrito': carrito})

if __name__ == '__main__':
    app.run(port=5000, debug=True)
