import sqlite3

conn = sqlite3.connect('ferremas.db')
cursor = conn.cursor()
cursor.execute("SELECT * FROM productos")
productos = cursor.fetchall()

print("=== PRODUCTOS EN BASE DE DATOS ===")
for producto in productos:
    print(f"Código: {producto[0]}, Nombre: {producto[1]}, Precio: {producto[2]}, Stock: {producto[3]}, Imagen: {producto[4]}")

print(f"\nTotal: {len(productos)} productos")
conn.close()