from flask import Flask, jsonify, request, session, redirect
from flask_cors import CORS
import sqlite3
from datetime import datetime
import json
import requests

app = Flask(__name__)
CORS(app)  
app.secret_key = 'ferremas_secret'  # Asegúrate de tener esto

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

# Endpoint para iniciar la transacción with Transbank
@app.route('/api/pago/iniciar', methods=['POST'])
def iniciar_pago():
    datos = request.json
    monto = datos.get('monto')
    buy_order = datos.get('buy_order', 'orden123')
    session_id = datos.get('session_id', 'sesion123')
    return_url = datos.get('return_url', 'http://localhost:8000/pago_exitoso')

    # Usa las credenciales y endpoint de integración oficiales de Transbank
    url = "https://webpay3gint.transbank.cl/rswebpaytransaction/api/webpay/v1.0/transactions"
    headers = {
        "Tbk-Api-Key-Id": "597055555532",
        "Tbk-Api-Key-Secret": "XW6bU9l5nTQ8QwGH5pWQ5n7g7m9a6v5t",
        "Content-Type": "application/json"
    }
    body = {
        "buy_order": buy_order,
        "session_id": session_id,
        "amount": monto,
        "return_url": return_url
    }
    try:
        resp = requests.post(url, json=body, headers=headers, timeout=10)
        print("Transbank status:", resp.status_code)
        print("Transbank response:", resp.text)
        if resp.status_code == 200:
            data = resp.json()
            return jsonify({"url": data["url"], "token": data["token"]})
        else:
            # Devuelve el código de error real para mejor diagnóstico
            return jsonify({"error": "No se pudo iniciar la transacción", "detalle": resp.text, "status_code": resp.status_code}), resp.status_code
    except Exception as e:
        print("Error al conectar con Transbank:", str(e))
        return jsonify({"error": "Error de conexión con Transbank", "detalle": str(e)}), 500

# Endpoint para recibir el resultado del pago (return_url)
@app.route('/pago_exitoso', methods=['POST'])
def pago_exitoso():
    token = request.form.get('token_ws')
    # Consultar el estado de la transacción
    url = f"https://webpay3gint.transbank.cl/rswebpaytransaction/api/webpay/v1.0/transactions/{token}"
    headers = {
        "Tbk-Api-Key-Id": "597055555532",
        "Tbk-Api-Key-Secret": "XW6bU9l5nTQ8QwGH5pWQ5n7g7m9a6v5t"
    }
    resp = requests.put(url, headers=headers)
    if resp.status_code == 200:
        data = resp.json()
        # Limpia el carrito de la sesión si lo usas en backend
        session.pop('carrito', None)
        # Página de éxito amigable
        return """
        <html>
        <head>
            <meta charset="utf-8">
            <title>Pago Exitoso - FERREMAS</title>
            <style>
                body { font-family: Arial, sans-serif; background: #f3f3f3; text-align: center; padding-top: 80px; }
                .msg { background: #fff; display: inline-block; padding: 40px 60px; border-radius: 12px; box-shadow: 0 2px 16px rgba(0,0,0,0.07);}
                .msg h2 { color: #28a745; margin-bottom: 18px;}
                .msg a { display: inline-block; margin-top: 18px; background: #ff7300; color: #fff; padding: 12px 28px; border-radius: 6px; text-decoration: none; font-weight: bold;}
                .msg a:hover { background: #ff9800; }
            </style>
        </head>
        <body>
            <div class="msg">
                <h2>¡Pago realizado con éxito!</h2>
                <p>Tu compra fue procesada correctamente.<br>Gracias por confiar en FERREMAS.</p>
                <a href="/catalog">Volver al Catálogo</a>
            </div>
            <script>
                // Limpia el carrito del frontend
                localStorage.removeItem('carrito');
            </script>
        </body>
        </html>
        """
    else:
        return """
        <html>
        <head><meta charset="utf-8"><title>Error de Pago</title></head>
        <body style="text-align:center;padding-top:80px;">
            <h2 style="color:#dc3545;">Error al confirmar el pago</h2>
            <a href="/cart" style="color:#007bff;">Volver al carrito</a>
        </body>
        </html>
        """, 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)