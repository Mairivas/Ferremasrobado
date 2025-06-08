import sqlite3

def corregir_rutas_imagenes():
    """
    Corrige las rutas de imágenes en la base de datos
    """
    try:
        conn = sqlite3.connect('ferremas.db')
        cursor = conn.cursor()

        # Ver productos actuales
        cursor.execute("SELECT codigo, nombre, imagen FROM productos")
        productos = cursor.fetchall()

        print("🔍 PRODUCTOS ACTUALES:")
        print("=" * 50)
        for codigo, nombre, imagen in productos:
            print(f"📦 {codigo}: {nombre} -> {imagen}")

        print("\n🛠️ CORRIGIENDO RUTAS...")

        # Actualizar rutas que tengan 'images' por 'img'
        cursor.execute("""
            UPDATE productos 
            SET imagen = REPLACE(imagen, 'images/', 'img/')
            WHERE imagen LIKE '%images/%'
        """)

        # También corregir si tienen ruta completa static/
        cursor.execute("""
            UPDATE productos 
            SET imagen = REPLACE(imagen, 'static/img/', '')
            WHERE imagen LIKE 'static/img/%'
        """)

        cursor.execute("""
            UPDATE productos 
            SET imagen = REPLACE(imagen, 'static/images/', '')
            WHERE imagen LIKE 'static/images/%'
        """)

        conn.commit()

        # Ver productos corregidos
        cursor.execute("SELECT codigo, nombre, imagen FROM productos")
        productos_corregidos = cursor.fetchall()

        print("\n✅ PRODUCTOS CORREGIDOS:")
        print("=" * 50)
        for codigo, nombre, imagen in productos_corregidos:
            print(f"📦 {codigo}: {nombre} -> {imagen}")

        print(f"\n🎯 TOTAL PRODUCTOS: {len(productos_corregidos)}")
        print("✅ Rutas de imágenes corregidas!")

        conn.close()

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    corregir_rutas_imagenes()
