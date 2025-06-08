from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
from datetime import datetime
import json

app = Flask(__name__)
CORS(app)  

def get_db_connection():
    conn = sqlite3.connect('ferremas.db')
    conn.row_factory = sqlite3.Row
    return conn

# Endpoint 1: Listar todos los productos
@app.route('/api/productos', methods=['GET'])
def listar_productos():
    try:
        conn = get_db_connection()
        productos = conn.execute('SELECT * FROM productos').fetchall()
        conn.close()
        
        productos_json = []
        for producto in productos:
            productos_json.append({
                "codigo_producto": producto['codigo'],
                "marca": "FERREMAS",  # Puedes cambiar esto
                "codigo": producto['codigo'],
                "nombre": producto['nombre'],
                "descripcion": producto['descripcion'],
                "stock": producto['stock'],
                "precio": [{
                    "fecha": datetime.now().isoformat(),
                    "valor": producto['valor']
                }],
                "imagen": producto['imagen']
            })
        
        return jsonify(productos_json), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint 2: Obtener producto específico
@app.route('/api/productos/<codigo>', methods=['GET'])
def obtener_producto(codigo):
    try:
        conn = get_db_connection()
        producto = conn.execute('SELECT * FROM productos WHERE codigo = ?', (codigo,)).fetchone()
        conn.close()
        
        if producto:
            producto_json = {
                "codigo_producto": producto['codigo'],
                "marca": "FERREMAS",
                "codigo": producto['codigo'],
                "nombre": producto['nombre'],
                "descripcion": producto['descripcion'],
                "stock": producto['stock'],
                "precio": [{
                    "fecha": datetime.now().isoformat(),
                    "valor": producto['valor']
                }],
                "imagen": producto['imagen']
            }
            return jsonify(producto_json), 200
        else:
            return jsonify({"error": "Producto no encontrado"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint 3: Consultar solo el stock
@app.route('/api/productos/<codigo>/stock', methods=['GET'])
def consultar_stock(codigo):
    try:
        conn = get_db_connection()
        producto = conn.execute('SELECT stock FROM productos WHERE codigo = ?', (codigo,)).fetchone()
        conn.close()
        
        if producto:
            return jsonify({
                "codigo": codigo,
                "stock": producto['stock']
            }), 200
        else:
            return jsonify({"error": "Producto no encontrado"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint 4: Actualizar stock
@app.route('/api/productos/<codigo>/stock', methods=['PUT'])
def actualizar_stock(codigo):
    try:
        data = request.get_json()
        nuevo_stock = data.get('stock')
        
        if nuevo_stock is None:
            return jsonify({"error": "Stock requerido"}), 400
        
        conn = get_db_connection()
        conn.execute('UPDATE productos SET stock = ? WHERE codigo = ?', (nuevo_stock, codigo))
        conn.commit()
        conn.close()
        
        return jsonify({
            "mensaje": "Stock actualizado correctamente",
            "codigo": codigo,
            "nuevo_stock": nuevo_stock
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint 5: Crear nuevo producto
@app.route('/api/productos', methods=['POST'])
def crear_producto():
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        if not all(key in data for key in ['codigo', 'nombre', 'valor', 'stock', 'imagen']):
            return jsonify({"error": "Faltan campos requeridos"}), 400
        
        # Verificar que el producto no exista
        conn = get_db_connection()
        producto_existente = conn.execute('SELECT codigo FROM productos WHERE codigo = ?', (data['codigo'],)).fetchone()
        
        if producto_existente:
            conn.close()
            return jsonify({"error": "El producto ya existe"}), 400
        
        # Insertar nuevo producto
        conn.execute("""
            INSERT INTO productos (codigo, nombre, valor, stock, imagen, descripcion)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            data['codigo'],
            data['nombre'],
            data['valor'],
            data['stock'],
            data['imagen'],
            data.get('descripcion', '')
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            "mensaje": "Producto creado exitosamente",
            "codigo": data['codigo'],
            "nombre": data['nombre'],
            "valor": data['valor'],
            "stock": data['stock']
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)