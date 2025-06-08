from flask import Flask, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)  # Permitir CORS para todas las rutas

# Datos de divisas (simulados - en producción usarías una API real)
DIVISAS = {
    'USD': {
        'nombre': 'Dólar Estadounidense',
        'valor': 950.0,  # 1 USD = 950 CLP
        'simbolo': '$'
    },
    'EUR': {
        'nombre': 'Euro',
        'valor': 1050.0,  # 1 EUR = 1050 CLP
        'simbolo': '€'
    },
    'ARS': {
        'nombre': 'Peso Argentino',
        'valor': 1.2,  # 1 ARS = 1.2 CLP
        'simbolo': '$'
    }
}

@app.route('/api/divisas/<codigo>', methods=['GET'])
def obtener_divisa(codigo):
    """
    Obtiene el valor de una divisa específica
    """
    codigo = codigo.upper()

    if codigo in DIVISAS:
        divisa = DIVISAS[codigo]
        return jsonify({
            'codigo': codigo,
            'nombre': divisa['nombre'],
            'valor': divisa['valor'],
            'simbolo': divisa['simbolo'],
            'mensaje': f'1 {codigo} = {divisa["valor"]} CLP'
        }), 200
    else:
        return jsonify({
            'error': f'Divisa {codigo} no encontrada',
            'divisas_disponibles': list(DIVISAS.keys())
        }), 404

@app.route('/api/divisas', methods=['GET'])
def listar_divisas():
    """
    Lista todas las divisas disponibles
    """
    return jsonify({
        'divisas': DIVISAS,
        'total': len(DIVISAS)
    }), 200

@app.route('/api/divisas/convertir/<codigo>/<float:monto>', methods=['GET'])
def convertir_divisa(codigo, monto):
    """
    Convierte un monto de CLP a la divisa especificada
    """
    codigo = codigo.upper()

    if codigo in DIVISAS:
        valor_divisa = DIVISAS[codigo]['valor']
        monto_convertido = round(monto / valor_divisa, 2)

        return jsonify({
            'monto_clp': monto,
            'divisa': codigo,
            'monto_convertido': monto_convertido,
            'tasa_cambio': valor_divisa,
            'mensaje': f'{monto} CLP = {monto_convertido} {codigo}'
        }), 200
    else:
        return jsonify({
            'error': f'Divisa {codigo} no encontrada'
        }), 404

@app.route('/health', methods=['GET'])
def health_check():
    """
    Endpoint para verificar que la API está funcionando
    """
    return jsonify({
        'status': 'OK',
        'mensaje': 'API de Divisas funcionando correctamente',
        'puerto': 5001
    }), 200

if __name__ == '__main__':
    print("🚀 Iniciando API de Divisas...")
    print("📊 Divisas disponibles:", list(DIVISAS.keys()))
    print("🌐 Servidor corriendo en http://localhost:5001")
    print("✅ Endpoints disponibles:")
    print("   - GET /api/divisas")
    print("   - GET /api/divisas/<codigo>")
    print("   - GET /api/divisas/convertir/<codigo>/<monto>")
    print("   - GET /health")

    app.run(host='0.0.0.0', port=5001, debug=True)
