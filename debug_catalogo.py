import sqlite3

print("=== DEBUG CATÁLOGO ===")

# Verificar productos en DB
conn = sqlite3.connect('ferremas.db')
cursor = conn.cursor()
cursor.execute("SELECT * FROM productos")
productos = cursor.fetchall()

print(f"Productos en DB: {len(productos)}")
for producto in productos:
    print(f"- {producto[0]}: {producto[1]}")

conn.close()

# Simular consulta del catálogo
print("\n=== SIMULANDO CONSULTA CATÁLOGO ===")
conn = sqlite3.connect('ferremas.db')
cursor = conn.cursor()
cursor.execute("SELECT codigo, nombre, valor, stock, imagen FROM productos")
productos_catalogo = cursor.fetchall()

print(f"Productos para catálogo: {len(productos_catalogo)}")
for producto in productos_catalogo:
    print(f"- {producto}")

conn.close()