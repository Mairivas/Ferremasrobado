import sqlite3

conn = sqlite3.connect('ferremas.db')
cursor = conn.cursor()

print("=== ANTES DE LIMPIAR ===")
cursor.execute("SELECT codigo, COUNT(*) FROM productos GROUP BY codigo")
duplicados = cursor.fetchall()
for codigo, cantidad in duplicados:
    print(f"{codigo}: {cantidad} veces")

# Eliminar duplicados, mantener solo uno de cada código
cursor.execute("""
DELETE FROM productos 
WHERE rowid NOT IN (
    SELECT MIN(rowid) 
    FROM productos 
    GROUP BY codigo
)
""")

conn.commit()

print(f"\n=== DESPUÉS DE LIMPIAR ===")
cursor.execute("SELECT * FROM productos")
productos = cursor.fetchall()
for producto in productos:
    print(f"Código: {producto[0]}, Nombre: {producto[1]}")

print(f"\nTotal productos únicos: {len(productos)}")
conn.close()