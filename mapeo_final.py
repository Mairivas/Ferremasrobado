import sqlite3

def aplicar_mapeo_final():
    """Aplica el mapeo final basado en las coincidencias encontradas"""

    # Mapeo definitivo basado en el diagnóstico
    mapeo_definitivo = {
        'MART001': 'martillo_stanley.jpg',
        'DEST001': 'destornillador_phillips.jpg', 
        'TALA001': 'taladro_bosch.jpg',  # Elegimos el más específico
        'LLAV001': 'llave_inglesa.jpg',  # Elegimos el más específico
        'SERR001': 'sierra_circular.jpg',
        'ALIC001': 'alicate_stanley.jpg',
        'NIVE001': 'nivel_laser.jpg',
        'TORN001': 'tornillos_tenz.jpg',
        # Los que no tienen coincidencia los dejamos como están
        'METR001': 'metro.jpg',  # Mantener original (tal vez tengas la imagen)
        'CLAV001': 'clavos.jpg'  # Mantener original (tal vez tengas la imagen)
    }

    try:
        conn = sqlite3.connect('ferremas.db')
        cursor = conn.cursor()

        print("🔄 Aplicando mapeo final...")

        for codigo, nueva_imagen in mapeo_definitivo.items():
            cursor.execute("UPDATE productos SET imagen = ? WHERE codigo = ?", 
                         (nueva_imagen, codigo))
            print(f"✅ {codigo} → {nueva_imagen}")

        conn.commit()
        conn.close()

        print("\n🎉 ¡Mapeo final completado!")
        print("\n📋 Próximos pasos:")
        print("1. Reinicia tu servidor: python start_final.py")
        print("2. Ve a http://localhost:8000/catalog")
        print("3. ¡Deberías ver casi todas las imágenes!")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    aplicar_mapeo_final()
