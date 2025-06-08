from flask import Flask, jsonify, request
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import sqlite3

app = Flask(__name__)

# Función para obtener el tipo de cambio del dólar desde el Banco Central
def obtener_tipo_cambio_usd():
    try:
        # Por ahora usaremos un valor fijo para pruebas (valor aproximado del dólar)
        # En producción deberías usar la API real del Banco Central
        return 950.0  # Valor aproximado del dólar en pesos chilenos

    except Exception as e:
        print(f"Error obteniendo tipo de cambio: {e}")
        return 950.0  # Valor por defecto

# Endpoint para obtener tipo de cambio actual
@app.route('/api/divisas/usd-clp', methods=['GET'])
def tipo_cambio_usd():
    try:
        tipo_cambio = obtener_tipo_cambio_usd()
        return jsonify({
            "moneda_origen": "USD",
            "moneda_destino": "CLP",
            "tipo_cambio": tipo_cambio,
            "fecha": datetime.now().isoformat(),
            "fuente": "Banco Central de Chile"
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint para convertir precio de producto a USD
@app.route('/api/divisas/convertir/<codigo_producto>', methods=['GET'])
def convertir_producto_usd(codigo_producto):
    try:
        # Obtener precio del producto desde la base de datos
        conn = sqlite3.connect('ferremas.db')
        cursor = conn.cursor()
        cursor.execute("SELECT nombre, valor FROM productos WHERE codigo = ?", (codigo_producto,))
        producto = cursor.fetchone()
        conn.close()

        if not producto:
            return jsonify({"error": "Producto no encontrado"}), 404

        nombre, precio_clp = producto
        tipo_cambio = obtener_tipo_cambio_usd()
        precio_usd = round(precio_clp / tipo_cambio, 2)

        return jsonify({
            "codigo_producto": codigo_producto,
            "nombre": nombre,
            "precio_clp": precio_clp,
            "precio_usd": precio_usd,
            "tipo_cambio": tipo_cambio,
            "fecha_conversion": datetime.now().isoformat()
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint simplificado para obtener solo el valor USD (compatibilidad)
@app.route('/api/divisas/USD', methods=['GET'])
def obtener_valor_usd():
    """Endpoint de compatibilidad para obtener valor del USD"""
    try:
        tipo_cambio = obtener_tipo_cambio_usd()
        return jsonify({
            "moneda": "USD",
            "valor": tipo_cambio,
            "fecha": datetime.now().isoformat(),
            "fuente": "Banco Central de Chile (simulado)"
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("🚀 Iniciando API Divisas en puerto 5001...")
    app.run(debug=True, port=5001, host='0.0.0.0')
