import sqlite3
import os

def diagnosticar_imagenes_faltantes():
    """Muestra exactamente qué imágenes faltan y qué archivos están disponibles"""

    # Obtener archivos reales
    archivos_reales = []
    if os.path.exists('static/img'):
        archivos_reales = [f for f in os.listdir('static/img') 
                          if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))]

    try:
        conn = sqlite3.connect('ferremas.db')
        cursor = conn.cursor()

        # Obtener productos que NO tienen imagen o imagen faltante
        cursor.execute("SELECT codigo, nombre, imagen FROM productos")
        productos = cursor.fetchall()

        print("❌ IMÁGENES FALTANTES:")
        print("=" * 50)

        faltantes = []
        for codigo, nombre, imagen in productos:
            if not imagen or imagen not in archivos_reales:
                faltantes.append((codigo, nombre, imagen))
                print(f"Código: {codigo}")
                print(f"Nombre: {nombre}")
                print(f"Imagen BD: {imagen}")
                print("-" * 30)

        print(f"\n📁 ARCHIVOS DISPONIBLES EN static/img:")
        print("=" * 50)
        for archivo in sorted(archivos_reales):
            print(f"  {archivo}")

        print(f"\n🔍 SUGERENCIAS DE MAPEO:")
        print("=" * 50)

        # Sugerir mapeos basados en palabras clave
        for codigo, nombre, imagen_bd in faltantes:
            print(f"\n{codigo} ({nombre}):")
            print(f"  BD busca: {imagen_bd}")

            # Buscar coincidencias por palabras clave del nombre del producto
            palabras_clave = nombre.lower().split()
            coincidencias = []

            for archivo in archivos_reales:
                archivo_lower = archivo.lower()
                for palabra in palabras_clave:
                    if palabra in archivo_lower and len(palabra) > 3:  # Solo palabras significativas
                        coincidencias.append(archivo)
                        break

            if coincidencias:
                print(f"  Posibles coincidencias:")
                for coincidencia in coincidencias[:3]:  # Mostrar máximo 3
                    print(f"    → {coincidencia}")
            else:
                print(f"  No se encontraron coincidencias obvias")

        conn.close()

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    diagnosticar_imagenes_faltantes()
