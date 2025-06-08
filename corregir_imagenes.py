import sqlite3

def corregir_rutas_imagenes():
    """Corrige las rutas duplicadas de imágenes en la base de datos"""
    try:
        conn = sqlite3.connect('ferremas.db')
        cursor = conn.cursor()

        # Obtener todos los productos
        cursor.execute("SELECT id, codigo, imagen FROM productos")
        productos = cursor.fetchall()

        print("🔍 Revisando rutas de imágenes...")

        for producto_id, codigo, imagen in productos:
            # Si la imagen tiene "static/img/" al inicio, quitarlo
            if imagen and imagen.startswith('static/img/'):
                nueva_imagen = imagen.replace('static/img/', '')

                # Actualizar en la base de datos
                cursor.execute("UPDATE productos SET imagen = ? WHERE id = ?", (nueva_imagen, producto_id))
                print(f"✅ Corregido {codigo}: {imagen} → {nueva_imagen}")
            else:
                print(f"✓ OK {codigo}: {imagen}")

        conn.commit()
        conn.close()
        print("\n🎉 ¡Rutas de imágenes corregidas!")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    corregir_rutas_imagenes()
