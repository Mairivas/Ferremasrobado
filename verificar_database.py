#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar el contenido de la base de datos
Archivo: verificar_database.py
"""

import sqlite3
import os

def verificar_base_datos():
    """Verifica el contenido de la base de datos"""

    db_name = 'ferremas.db'

    if not os.path.exists(db_name):
        print(f"❌ Base de datos '{db_name}' no existe")
        return False

    print("🔍 VERIFICANDO BASE DE DATOS FERREMAS")
    print("=" * 50)

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Verificar usuarios
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    usuarios_count = cursor.fetchone()[0]
    print(f"👥 Usuarios registrados: {usuarios_count}")

    if usuarios_count > 0:
        cursor.execute("SELECT username, email FROM usuarios")
        usuarios = cursor.fetchall()
        for usuario in usuarios:
            print(f"   - {usuario[0]} ({usuario[1]})")

    # Verificar productos
    cursor.execute("SELECT COUNT(*) FROM productos")
    productos_count = cursor.fetchone()[0]
    print(f"\n📦 Productos en catálogo: {productos_count}")

    if productos_count > 0:
        cursor.execute("SELECT codigo, nombre, valor, stock FROM productos")
        productos = cursor.fetchall()
        for producto in productos:
            print(f"   - {producto[0]}: {producto[1]} (${producto[2]:,} - Stock: {producto[3]})")

    # Verificar carrito
    cursor.execute("SELECT COUNT(*) FROM carrito")
    carrito_count = cursor.fetchone()[0]
    print(f"\n🛒 Items en carritos: {carrito_count}")

    conn.close()

    print("\n✅ Verificación completada")
    return True

if __name__ == "__main__":
    verificar_base_datos()
