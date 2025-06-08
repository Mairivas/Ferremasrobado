from flask import Flask, jsonify, request
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import sqlite3

app = Flask(__name__)

# Función para obtener el tipo de cambio del dólar desde el Banco Central
def obtener_tipo_cambio_usd():
    try:
        # URL de la API del Banco Central (serie del dólar observado)
        url = "https://si3.bcentral.cl/SieteRestWS/SieteRestWS.ashx"
        
        # Parámetros para la consulta (serie F073.TCO.PRE.Z.D - Dólar observado)
        params = {
            'user': 'tu_usuario@correo.com',  # Necesitas registrarte en el Banco Central
            'pass': 'tu_password',
            'function': 'GetSeries',
            'timeseries': 'F073.TCO.PRE.Z.D',
            'firstdate': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
            'lastdate': datetime.now().strftime('%Y-%m-%d')
        }
        
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

# Endpoint para convertir monto específico
@app.route('/api/divisas/convertir', methods=['POST'])
def convertir_monto():
    try:
        data = request.get_json()
        monto = data.get('monto')
        moneda_origen = data.get('moneda_origen', 'CLP')
        moneda_destino = data.get('moneda_destino', 'USD')
        
        if not monto:
            return jsonify({"error": "Monto requerido"}), 400
        
        tipo_cambio = obtener_tipo_cambio_usd()
        
        if moneda_origen == 'CLP' and moneda_destino == 'USD':
            monto_convertido = round(monto / tipo_cambio, 2)
        elif moneda_origen == 'USD' and moneda_destino == 'CLP':
            monto_convertido = round(monto * tipo_cambio, 2)
        else:
            return jsonify({"error": "Conversión no soportada"}), 400
        
        return jsonify({
            "monto_original": monto,
            "moneda_origen": moneda_origen,
            "monto_convertido": monto_convertido,
            "moneda_destino": moneda_destino,
            "tipo_cambio": tipo_cambio,
            "fecha_conversion": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)  