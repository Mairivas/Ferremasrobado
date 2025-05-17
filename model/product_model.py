 # Simulación de base de datos de productos
productos = [
    {
        "codigo": "P001",
        "nombre": "Taladro Inalámbrico Bosch",
        "descripcion": "Taladro inalámbrico de 18V con batería de larga duración.",
        "stock": 15,
        "valor": 120000,
        "imagen": "taladro_bosch.jpg"
    },
    {
        "codigo": "P002",
        "nombre": "Martillo Stanley",
        "descripcion": "Martillo de acero con mango ergonómico.",
        "stock": 30,
        "valor": 8000,
        "imagen": "martillo_stanley.jpg"
    },
    {
        "codigo": "P003",
        "nombre": "Caja de Tornillos Tenz",
        "descripcion": "Paquete con 100 tornillos de alta resistencia.",
        "stock": 50,
        "valor": 15000,
        "imagen": "tornillos_tenz.jpg"
    }
]

def listar_productos():
    return productos

def obtener_producto_por_codigo(codigo):
    for producto in productos:
        if producto["codigo"] == codigo:
            return producto
    return None

def actualizar_stock(codigo, cantidad):
    for producto in productos:
        if producto["codigo"] == codigo:
            if producto["stock"] >= cantidad:
                producto["stock"] -= cantidad
                return True
            else:
                return False
    return False

