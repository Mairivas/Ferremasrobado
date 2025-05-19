import sqlite3

# Crear/conectar a la base de datos
conn = sqlite3.connect("ferremas.db")
cursor = conn.cursor()

# Crear tabla de usuarios
cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
)
""")

# Crear tabla de productos
cursor.execute("""
CREATE TABLE IF NOT EXISTS productos (
    codigo TEXT PRIMARY KEY,
    nombre TEXT NOT NULL,
    descripcion TEXT,
    stock INTEGER NOT NULL,
    valor INTEGER NOT NULL,
    imagen TEXT
)
""")

# datos de ejemplo
cursor.execute("INSERT OR IGNORE INTO usuarios (name, email, password) VALUES (?, ?, ?)", ("Juan", "cliente1@gmail.com", "Cliente.01"))

productos = [
    ("P001", "Taladro Bosch", "Taladro percutor Bosch 500W.", 10, 49990, "taladro_bosch.jpg"),
    ("P002", "Martillo Stanley", "Martillo de carpintero 16oz Stanley.", 25, 8990, "martillo_stanley.jpg"),
    ("P003", "Caja de Tornillos Tenz", "Paquete con 100 tornillos de alta resistencia.", 50, 150000, "tornillos_tenz.jpg")
]

cursor.executemany("INSERT OR IGNORE INTO productos VALUES (?, ?, ?, ?, ?, ?)", productos)

conn.commit()
conn.close()
print("Base de datos creada con éxito.")
