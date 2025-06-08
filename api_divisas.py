from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import json

app = Flask(__name__)
CORS(app, origins="*")  # Permitir CORS para todas las rutas

# API key gratuita para obtener tasas de cambio reales
# Puedes registrarte en https://fixer.io/ o usar otra API
API_KEY = "tu_api_key_aqui"  # Reemplaza con tu API key real

# Datos de divisas de respaldo (por si falla la API externa)
DIVISAS_BACKUP = {
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

def obtener_tasa_cambio_real(codigo_divisa):
    """
    Obtiene la tasa de cambio real desde una API externa
    """
    try:
        # Usando API gratuita de exchangerate-api.com (no requiere key para uso básico)
        url = f"https://api.exchangerate-api.com/v4/latest/CLP"
        response = requests.get(url, timeout=5)

        if response.status_code == 200:
            data = response.json()
            if codigo_divisa in data['rates']:
                # La API devuelve cuánto vale 1 CLP en la divisa objetivo
                # Necesitamos el inverso para saber cuánto vale 1 divisa en CLP
                tasa_clp_a_divisa = data['rates'][codigo_divisa]
                tasa_divisa_a_clp = 1 / tasa_clp_a_divisa
                return tasa_divisa_a_clp
    except Exception as e:
        print(f"Error al obtener tasa de cambio real: {e}")

    # Si falla, usar datos de respaldo
    if codigo_divisa in DIVISAS_BACKUP:
        return DIVISAS_BACKUP[codigo_divisa]['valor']

    return None

@app.route('/api/divisas/<codigo>', methods=['GET'])
def obtener_divisa(codigo):
    """
    Obtiene el valor de una divisa específica
    """
    codigo = codigo.upper()

    # Intentar obtener tasa real
    valor_real = obtener_tasa_cambio_real(codigo)

    if valor_real:
        nombre_divisa = DIVISAS_BACKUP.get(codigo, {}).get('nombre', f'Divisa {codigo}')
        simbolo = DIVISAS_BACKUP.get(codigo, {}).get('simbolo', codigo)

        return jsonify({
            'codigo': codigo,
            'nombre': nombre_divisa,
            'valor': round(valor_real, 2),
            'simbolo': simbolo,
            'mensaje': f'1 {codigo} = {round(valor_real, 2)} CLP'
        }), 200
    else:
        return jsonify({
            'error': f'Divisa {codigo} no encontrada',
            'divisas_disponibles': list(DIVISAS_BACKUP.keys())
        }), 404

@app.route('/api/divisas', methods=['GET'])
def listar_divisas():
    """
    Lista todas las divisas disponibles
    """
    divisas_actualizadas = {}

    for codigo in DIVISAS_BACKUP.keys():
        valor_real = obtener_tasa_cambio_real(codigo)
        if valor_real:
            divisas_actualizadas[codigo] = {
                'nombre': DIVISAS_BACKUP[codigo]['nombre'],
                'valor': round(valor_real, 2),
                'simbolo': DIVISAS_BACKUP[codigo]['simbolo']
            }

    return jsonify({
        'divisas': divisas_actualizadas,
        'total': len(divisas_actualizadas)
    }), 200

@app.route('/api/divisas/convertir/<codigo>/<float:monto>', methods=['GET'])
def convertir_divisa(codigo, monto):
    """
    Convierte un monto de CLP a la divisa especificada
    """
    codigo = codigo.upper()

    # Obtener tasa de cambio actual
    valor_divisa = obtener_tasa_cambio_real(codigo)

    if valor_divisa:
        monto_convertido = round(monto / valor_divisa, 2)

        return jsonify({
            'monto_clp': monto,
            'divisa': codigo,
            'monto_convertido': monto_convertido,
            'tasa_cambio': round(valor_divisa, 2),
            'mensaje': f'{monto} CLP = {monto_convertido} {codigo}'
        }), 200
    else:
        return jsonify({
            'error': f'Divisa {codigo} no encontrada'
        }), 404

@app.route('/api/divisas/convertir', methods=['POST'])
def convertir_divisa_post():
    """
    Convierte divisas usando POST (más flexible)
    """
    try:
        data = request.get_json()
        codigo = data.get('codigo', '').upper()
        monto = float(data.get('monto', 0))

        if not codigo or monto <= 0:
            return jsonify({'error': 'Código de divisa y monto son requeridos'}), 400

        valor_divisa = obtener_tasa_cambio_real(codigo)

        if valor_divisa:
            monto_convertido = round(monto / valor_divisa, 2)

            return jsonify({
                'monto_clp': monto,
                'divisa': codigo,
                'monto_convertido': monto_convertido,
                'tasa_cambio': round(valor_divisa, 2),
                'mensaje': f'{monto} CLP = {monto_convertido} {codigo}'
            }), 200
        else:
            return jsonify({
                'error': f'Divisa {codigo} no encontrada'
            }), 404

    except Exception as e:
        return jsonify({'error': f'Error en la conversión: {str(e)}'}), 500

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
    print("📊 Divisas disponibles:", list(DIVISAS_BACKUP.keys()))
    print("🌐 Servidor corriendo en http://localhost:5001")
    print("✅ Endpoints disponibles:")
    print("   - GET /api/divisas")
    print("   - GET /api/divisas/<codigo>")
    print("   - GET /api/divisas/convertir/<codigo>/<monto>")
    print("   - POST /api/divisas/convertir")
    print("   - GET /health")

    app.run(host='0.0.0.0', port=5001, debug=True)
