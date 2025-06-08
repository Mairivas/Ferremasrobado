#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para diagnosticar por qué solo aparece 1 producto
Archivo: diagnostico_productos.py
"""

import sqlite3
import os

def diagnosticar_productos():
    """Diagnostica el problema de productos faltantes"""

    db_name = 'ferremas.db'

    print("🔍 DIAGNÓSTICO COMPLETO DE PRODUCTOS")
    print("=" * 50)

    if not os.path.exists(db_name):
        print(f"❌ Base de datos '{db_name}' no existe")
        return False

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # 1. Verificar estructura de la tabla
    print("📋 ESTRUCTURA DE LA TABLA PRODUCTOS:")
    cursor.execute("PRAGMA table_info(productos)")
    columnas = cursor.fetchall()
    for col in columnas:
        print(f"   - {col[1]} ({col[2]})")

    # 2. Contar productos totales
    cursor.execute("SELECT COUNT(*) FROM productos")
    total = cursor.fetchone()[0]
    print(f"\n📊 TOTAL DE PRODUCTOS EN BD: {total}")

    # 3. Mostrar todos los productos
    print("\n📦 TODOS LOS PRODUCTOS:")
    cursor.execute("SELECT id, codigo, nombre, valor, stock FROM productos ORDER BY id")
    productos = cursor.fetchall()

    for i, producto in enumerate(productos, 1):
        print(f"   {i}. ID:{producto[0]} | {producto[1]} | {producto[2]} | ${producto[3]:,} | Stock:{producto[4]}")

    # 4. Verificar si hay productos con problemas
    print("\n🔍 VERIFICANDO POSIBLES PROBLEMAS:")

    # Productos con nombres vacíos
    cursor.execute("SELECT COUNT(*) FROM productos WHERE nombre IS NULL OR nombre = ''")
    nombres_vacios = cursor.fetchone()[0]
    if nombres_vacios > 0:
        print(f"   ⚠️  {nombres_vacios} productos con nombres vacíos")

    # Productos con precios 0
    cursor.execute("SELECT COUNT(*) FROM productos WHERE valor <= 0")
    precios_cero = cursor.fetchone()[0]
    if precios_cero > 0:
        print(f"   ⚠️  {precios_cero} productos con precio 0 o negativo")

    # Productos con stock negativo
    cursor.execute("SELECT COUNT(*) FROM productos WHERE stock < 0")
    stock_negativo = cursor.fetchone()[0]
    if stock_negativo > 0:
        print(f"   ⚠️  {stock_negativo} productos con stock negativo")

    if nombres_vacios == 0 and precios_cero == 0 and stock_negativo == 0:
        print("   ✅ No se encontraron problemas en los datos")

    # 5. Simular la consulta que debería hacer el servidor
    print("\n🌐 SIMULANDO CONSULTA DEL SERVIDOR:")
    cursor.execute("SELECT * FROM productos")
    productos_servidor = cursor.fetchall()

    print(f"   📊 Productos que debería mostrar el servidor: {len(productos_servidor)}")

    if len(productos_servidor) != total:
        print(f"   ❌ PROBLEMA: El servidor obtiene {len(productos_servidor)} pero hay {total} en la BD")
    else:
        print("   ✅ El servidor debería obtener todos los productos correctamente")

    conn.close()

    # 6. Generar recomendaciones
    print("\n💡 RECOMENDACIONES:")
    if total == 1:
        print("   🔧 Solo hay 1 producto en la BD. Ejecuta: python fix_productos.py")
    elif total == 10:
        print("   🔧 Hay 10 productos en la BD. El problema está en el código del servidor.")
        print("   🔧 Necesitamos revisar el archivo server.py en la ruta /catalog")
    else:
        print(f"   🔧 Hay {total} productos. Verifica si es el número correcto.")

    return True

def generar_solucion_server():
    """Genera código corregido para el servidor"""

    print("\n🔧 CÓDIGO SUGERIDO PARA server.py (ruta /catalog):")
    print("-" * 50)

    codigo_catalog = """
# En server.py, busca la ruta @app.route('/catalog') y reemplázala con esto:

@app.route('/catalog')
def catalog():
    if 'user_id' not in session:
        return redirect('/login')

    try:
        # Conectar a la base de datos
        conn = sqlite3.connect('ferremas.db')
        cursor = conn.cursor()

        # Obtener TODOS los productos
        cursor.execute("SELECT * FROM productos ORDER BY id")
        productos = cursor.fetchall()

        conn.close()

        # Debug: imprimir cuántos productos se obtuvieron
        print(f"DEBUG: Se obtuvieron {len(productos)} productos de la BD")

        # Renderizar template con todos los productos
        return render_template('catalog.html', productos=productos)

    except Exception as e:
        print(f"ERROR en /catalog: {e}")
        return f"Error al cargar catálogo: {e}"
    """

    print(codigo_catalog)

if __name__ == "__main__":
    diagnosticar_productos()
    generar_solucion_server()
