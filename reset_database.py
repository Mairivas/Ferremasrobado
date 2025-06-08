#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para resetear completamente la base de datos de Ferremas
Archivo: reset_database.py
"""

import sqlite3
import os
import json
from datetime import datetime

def resetear_base_datos():
    """Elimina y recrea la base de datos con productos de ejemplo"""

    # Nombre de la base de datos
    db_name = 'ferremas.db'

    print("🗑️  RESETEANDO BASE DE DATOS FERREMAS")
    print("=" * 50)

    # 1. Eliminar base de datos existente
    if os.path.exists(db_name):
        os.remove(db_name)
        print(f"✅ Base de datos '{db_name}' eliminada")
    else:
        print(f"ℹ️  Base de datos '{db_name}' no existía")

    # 2. Crear nueva base de datos
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # 3. Crear tabla de usuarios
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT,
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 4. Crear tabla de productos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE NOT NULL,
            nombre TEXT NOT NULL,
            valor INTEGER NOT NULL,
            stock INTEGER NOT NULL,
            imagen TEXT,
            descripcion TEXT,
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 5. Crear tabla de carrito
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS carrito (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            producto_id INTEGER,
            cantidad INTEGER DEFAULT 1,
            fecha_agregado TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (usuario_id) REFERENCES usuarios (id),
            FOREIGN KEY (producto_id) REFERENCES productos (id)
        )
    """)

    print("✅ Tablas creadas correctamente")

    # 6. Insertar usuario de prueba
    cursor.execute("""
        INSERT INTO usuarios (username, password, email) 
        VALUES (?, ?, ?)
    """, ('admin', 'admin123', 'admin@ferremas.cl'))

    cursor.execute("""
        INSERT INTO usuarios (username, password, email) 
        VALUES (?, ?, ?)
    """, ('usuario', '123456', 'usuario@ferremas.cl'))

    print("✅ Usuarios de prueba creados:")
    print("   👤 admin / admin123")
    print("   👤 usuario / 123456")

    # 7. Insertar productos de ejemplo
    productos_ejemplo = [
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

    for producto in productos_ejemplo:
        cursor.execute("""
            INSERT INTO productos (codigo, nombre, valor, stock, imagen, descripcion)
            VALUES (?, ?, ?, ?, ?, ?)
        """, producto)

    print(f"✅ {len(productos_ejemplo)} productos de ejemplo insertados")

    # 8. Confirmar cambios
    conn.commit()
    conn.close()

    print("✅ Base de datos reseteada exitosamente")
    print()
    print("🎯 PRÓXIMOS PASOS:")
    print("   1. Ejecuta: python start_servers.py")
    print("   2. Visita: http://localhost:8000")
    print("   3. Inicia sesión con: admin / admin123")
    print("   4. Ve al catálogo para ver los productos")

    return True

if __name__ == "__main__":
    try:
        resetear_base_datos()
        print("\n🎉 PROCESO COMPLETADO EXITOSAMENTE")
    except Exception as e:
        print(f"❌ Error: {e}")
