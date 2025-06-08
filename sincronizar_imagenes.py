import sqlite3
import os

def sincronizar_imagenes():
    """Sincroniza los nombres de imágenes en la BD con los archivos reales"""

    # Obtener lista de archivos reales en static/img
    archivos_reales = []
    if os.path.exists('static/img'):
        archivos_reales = [f for f in os.listdir('static/img') 
                          if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))]

    print("🖼️  Archivos de imagen encontrados:")
    for archivo in sorted(archivos_reales):
        print(f"   {archivo}")

    # Mapeo sugerido basado en nombres similares
    mapeo_sugerido = {
        'martillo.jpg': 'martillo_stanley.jpg',
        'destornillador.jpg': 'destornillador_phillips.jpg', 
        'taladro.jpg': 'taladro_bosch.jpg',
        'sierra.jpg': 'sierra_circular.jpg',
        'llave.jpg': 'llave_inglesa.jpg',
        'alicate.jpg': 'alicate_stanley.jpg',
        'nivel.jpg': 'nivel_laser.jpg',
        'pistola.jpg': 'pistola_calor.jpg',
        'serrucho.jpg': 'serrucho_electrico.jpg',
        'tornillos.jpg': 'tornillos_tenz.jpg',
        'cinta.jpg': 'cinta_metrica.jpg',
        'amoladora.jpg': 'amoladora_angular.jpg',
        'juego_llaves.jpg': 'juego_llaves.jpg',
        'taladro_percutor.jpg': 'taladro_percutor.jpg',
        'serrucho_tolsen.jpg': 'serrucho_tolsen.jpg'
    }

    try:
        conn = sqlite3.connect('ferremas.db')
        cursor = conn.cursor()

        # Obtener productos actuales
        cursor.execute("SELECT id, codigo, nombre, imagen FROM productos")
        productos = cursor.fetchall()

        print("\n🔄 Actualizando base de datos...")

        for producto_id, codigo, nombre, imagen_actual in productos:
            # Buscar mapeo sugerido
            if imagen_actual in mapeo_sugerido:
                nueva_imagen = mapeo_sugerido[imagen_actual]
                if nueva_imagen in archivos_reales:
                    cursor.execute("UPDATE productos SET imagen = ? WHERE id = ?", 
                                 (nueva_imagen, producto_id))
                    print(f"✅ {codigo}: {imagen_actual} → {nueva_imagen}")
                else:
                    print(f"⚠️  {codigo}: {nueva_imagen} no encontrada")
            else:
                # Buscar por coincidencia parcial
                nombre_base = imagen_actual.replace('.jpg', '').replace('.png', '')
                coincidencias = [f for f in archivos_reales if nombre_base.lower() in f.lower()]

                if coincidencias:
                    nueva_imagen = coincidencias[0]
                    cursor.execute("UPDATE productos SET imagen = ? WHERE id = ?", 
                                 (nueva_imagen, producto_id))
                    print(f"🔍 {codigo}: {imagen_actual} → {nueva_imagen} (coincidencia)")
                else:
                    print(f"❌ {codigo}: No se encontró imagen para {imagen_actual}")

        conn.commit()
        conn.close()
        print("\n🎉 ¡Sincronización completada!")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    sincronizar_imagenes()
