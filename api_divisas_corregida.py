from flask import Flask, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)  # Permitir CORS para todas las rutas

# Función para obtener tasa de cambio real
def obtener_tasa_usd_clp():
    try:
        # API gratuita para obtener tasas de cambio
        response = requests.get('https://api.exchangerate-api.com/v4/latest/USD', timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data['rates'].get('CLP', 800)  # Fallback a 800 si no encuentra
        else:
            return 800  # Tasa de respaldo
    except:
        return 800  # Tasa de respaldo en caso de error

@app.route('/api/divisas/test', methods=['GET'])
def test_api():
    """Endpoint de prueba"""
    return jsonify({
        "message": "API de divisas funcionando correctamente",
        "status": "success",
        "endpoints": [
            "/api/divisas/USD",
            "/api/divisas/convertir/USD/<monto>",
            "/api/divisas/test"
        ]
    })

@app.route('/api/divisas/USD', methods=['GET'])
def obtener_usd():
    """Obtener tasa de cambio USD a CLP"""
    try:
        tasa = obtener_tasa_usd_clp()
        return jsonify({
            "moneda": "USD",
            "tasa_cambio": tasa,
            "fecha": "2024-06-08",
            "status": "success"
        })
    except Exception as e:
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500

@app.route('/api/divisas/convertir/USD/<int:monto>', methods=['GET'])
def convertir_clp_a_usd(monto):
    """Convertir CLP a USD"""
    try:
        tasa_usd_clp = obtener_tasa_usd_clp()
        monto_usd = round(monto / tasa_usd_clp, 2)

        return jsonify({
            "monto_original": monto,
            "moneda_original": "CLP",
            "monto_convertido": monto_usd,
            "moneda_convertida": "USD",
            "tasa_cambio": tasa_usd_clp,
            "status": "success"
        })
    except Exception as e:
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500

@app.route('/api/divisas/convertir/USD/<float:monto>', methods=['GET'])
def convertir_clp_a_usd_float(monto):
    """Convertir CLP a USD (acepta decimales)"""
    try:
        tasa_usd_clp = obtener_tasa_usd_clp()
        monto_usd = round(monto / tasa_usd_clp, 2)

        return jsonify({
            "monto_original": monto,
            "moneda_original": "CLP",
            "monto_convertido": monto_usd,
            "moneda_convertida": "USD",
            "tasa_cambio": tasa_usd_clp,
            "status": "success"
        })
    except Exception as e:
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500

if __name__ == '__main__':
    print("🚀 API de Divisas iniciando en puerto 5001...")
    print("📊 Endpoints disponibles:")
    print("   - GET /api/divisas/test")
    print("   - GET /api/divisas/USD")
    print("   - GET /api/divisas/convertir/USD/<monto>")
    app.run(host='0.0.0.0', port=5001, debug=True)
