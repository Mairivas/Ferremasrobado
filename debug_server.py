#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para debuggear cómo server.py obtiene los productos
Archivo: debug_server.py
"""

import sqlite3
import os

def debug_productos_server():
    """Simula cómo server.py obtiene los productos"""

    db_name = 'ferremas.db'

    if not os.path.exists(db_name):
        print(f"❌ Base de datos '{db_name}' no existe")
        return False

    print("🐛 DEBUG: CÓMO SERVER.PY OBTIENE PRODUCTOS")
    print("=" * 50)

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Simular la consulta que hace server.py
    cursor.execute("SELECT * FROM productos")
    productos = cursor.fetchall()

    print(f"📦 Productos encontrados: {len(productos)}")
    print("\nDetalles de cada producto:")
    print("-" * 30)

    for i, producto in enumerate(productos, 1):
        print(f"{i}. ID: {producto[0]}")
        print(f"   Código: {producto[1]}")
        print(f"   Nombre: {producto[2]}")
        print(f"   Valor: ${producto[3]:,}")
        print(f"   Stock: {producto[4]}")
        print(f"   Imagen: {producto[5]}")
        print(f"   Descripción: {producto[6]}")
        print()

    # Simular HTML que se genera
    print("🌐 HTML QUE SE GENERARÍA:")
    print("-" * 30)

    html_productos = ""
    for producto in productos:
        html_producto = f"""
        <div class="producto">
            <img src="{producto[5]}" alt="{producto[2]}" onerror="this.src='/static/img/placeholder.jpg'">
            <h3>{producto[2]}</h3>
            <p>${producto[3]:,} CLP</p>
            <p class="precio-usd">Calculando USD...</p>
            <p>Stock: {producto[4]} unidades</p>
            <p>{producto[6]}</p>
            <button onclick="consultarStockAPI('{producto[1]}')" class="btn-stock-api">Consultar Stock API</button>
            <a href="/agregar_carrito/{producto[0]}">Agregar al Carrito</a>
        </div>
        """
        html_productos += html_producto

    print(html_productos)

    conn.close()
    return True

if __name__ == "__main__":
    debug_productos_server()
