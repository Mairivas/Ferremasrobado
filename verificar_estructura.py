import os

def verificar_estructura():
    """Verifica la estructura de carpetas y archivos de imágenes"""
    print("🔍 Verificando estructura del proyecto...")

    # Verificar carpetas principales
    carpetas_necesarias = ['static', 'static/img', 'view']

    for carpeta in carpetas_necesarias:
        if os.path.exists(carpeta):
            print(f"✅ Carpeta existe: {carpeta}")
        else:
            print(f"❌ Carpeta faltante: {carpeta}")

    # Verificar archivos de imagen en static/img
    if os.path.exists('static/img'):
        print("\n📁 Archivos en static/img:")
        archivos = os.listdir('static/img')
        for archivo in sorted(archivos):
            if archivo.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                print(f"  🖼️  {archivo}")
            else:
                print(f"  📄 {archivo}")
    else:
        print("\n❌ La carpeta static/img no existe")

    # Verificar si hay imágenes en otras ubicaciones
    print("\n🔍 Buscando imágenes en otras carpetas...")
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                ruta_completa = os.path.join(root, file)
                if 'static/img' not in ruta_completa:
                    print(f"  📍 Imagen encontrada en: {ruta_completa}")

if __name__ == "__main__":
    verificar_estructura()
