#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar y agregar productos faltantes
Archivo: fix_productos.py
"""

import sqlite3
import os

def verificar_y_agregar_productos():
    """Verifica productos en la BD y agrega los faltantes"""

    db_name = 'ferremas.db'

    if not os.path.exists(db_name):
        print(f"❌ Base de datos '{db_name}' no existe")
        return False

    print("🔍 VERIFICANDO PRODUCTOS EN LA BASE DE DATOS")
    print("=" * 50)

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Verificar productos actuales
    cursor.execute("SELECT codigo, nombre FROM productos")
    productos_actuales = cursor.fetchall()

    print(f"📦 Productos actuales en BD: {len(productos_actuales)}")
    for producto in productos_actuales:
        print(f"   ✅ {producto[0]}: {producto[1]}")

    # Lista completa de productos que deberían estar
    productos_completos = [
        ('MART001', 'Martillo de Carpintero', 15000, 25, '/static/img/martillo.jpg', 'Martillo profesional de carpintero con mango de madera'),
        ('DEST001', 'Destornillador Phillips', 3500, 50, '/static/img/destornillador.jpg', 'Destornillador Phillips #2 con mango ergonómico'),
        ('TALA001', 'Taladro Eléctrico Bosch', 89000, 8, '/static/img/taladro_bosch.jpg', 'Taladro eléctrico Bosch 650W con percutor'),
        ('LLAV001', 'Llave Inglesa 12"', 12000, 15, '/static/img/llave_inglesa.jpg', 'Llave inglesa ajustable de 12 pulgadas'),
        ('SERR001', 'Sierra de Metal', 8500, 20, '/static/img/sierra.jpg', 'Sierra de metal con hoja de acero templado'),
        ('ALIC001', 'Alicate Universal', 6500, 30, '/static/img/alicate.jpg', 'Alicate universal con aislamiento eléctrico'),
        ('NIVE001', 'Nivel de Burbuja 60cm', 18000, 12, '/static/img/nivel.jpg', 'Nivel de burbuja profesional de 60cm'),
        ('METR001', 'Metro de Carpintero 5m', 4500, 40, '/static/img/metro.jpg', 'Metro de carpintero de 5 metros con freno'),
        ('TORN001', 'Tornillos Autorroscantes x100', 2500, 100, '/static/img/tornillos.jpg', 'Pack de 100 tornillos autorroscantes 4x40mm'),
        ('CLAV001', 'Clavos de Acero x500g', 1800, 80, '/static/img/clavos.jpg', 'Clavos de acero galvanizado 500g surtidos')
    ]

    # Obtener códigos actuales
    codigos_actuales = [p[0] for p in productos_actuales]

    # Agregar productos faltantes
    productos_agregados = 0
    for producto in productos_completos:
        if producto[0] not in codigos_actuales:
            try:
                cursor.execute("""
                    INSERT INTO productos (codigo, nombre, valor, stock, imagen, descripcion)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, producto)
                print(f"   ➕ Agregado: {producto[0]} - {producto[1]}")
                productos_agregados += 1
            except sqlite3.IntegrityError:
                print(f"   ⚠️  Ya existe: {producto[0]}")

    if productos_agregados > 0:
        conn.commit()
        print(f"\n✅ {productos_agregados} productos agregados exitosamente")
    else:
        print("\n✅ Todos los productos ya están en la base de datos")

    # Verificar total final
    cursor.execute("SELECT COUNT(*) FROM productos")
    total_productos = cursor.fetchone()[0]
    print(f"\n📊 Total de productos en BD: {total_productos}")

    conn.close()
    return True

if __name__ == "__main__":
    verificar_y_agregar_productos()
