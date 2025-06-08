import sqlite3

def corregir_imagenes_y_productos():
    conn = sqlite3.connect('ferremas.db')
    cursor = conn.cursor()

    print("🔧 CORRIGIENDO NOMBRES DE IMÁGENES...")

    # Mapeo de productos existentes con sus imágenes correctas
    correcciones = [
        ("P001", "martillo_stanley.jpg"),
        ("P002", "alicate_stanley.jpg"), 
        ("P003", "serrucho_tolsen.jpg"),
        ("P004", "serrucho_electrico.jpg"),
        ("P005", "tornillos_tenz.jpg"),
        ("P006", "taladro_bosch.jpg")
    ]

    for codigo, imagen in correcciones:
        cursor.execute("UPDATE productos SET imagen = ? WHERE codigo = ?", (imagen, codigo))
        print(f"✅ {codigo}: {imagen}")

    print("\n➕ AGREGANDO PRODUCTOS NUEVOS...")

    # Productos adicionales (usaremos imágenes generadas)
    nuevos_productos = [
        ("P012", "Destornillador Phillips Stanley", 8990, 25, "destornillador_phillips.jpg", "Destornillador Phillips profesional Stanley, mango ergonómico"),
        ("P013", "Llave Inglesa Bahco", 15990, 18, "llave_inglesa.jpg", "Llave inglesa ajustable Bahco 250mm, acero forjado"),
        ("P014", "Nivel Laser Bosch", 89990, 8, "nivel_laser.jpg", "Nivel láser Bosch GLL 3-80, alcance 30m, precisión ±3mm"),
        ("P015", "Cinta Métrica Stanley", 12990, 30, "cinta_metrica.jpg", "Cinta métrica Stanley 5m, carcasa resistente a impactos"),
        ("P016", "Taladro Percutor Black+Decker", 45990, 12, "taladro_percutor.jpg", "Taladro percutor 600W, mandril 13mm, velocidad variable"),
        ("P017", "Sierra Circular Makita", 125990, 6, "sierra_circular.jpg", "Sierra circular Makita 1200W, disco 185mm, guía láser"),
        ("P018", "Juego Llaves Combinadas", 35990, 15, "juego_llaves.jpg", "Juego 12 llaves combinadas 8-19mm, acero cromo vanadio"),
        ("P019", "Pistola Calor Einhell", 28990, 10, "pistola_calor.jpg", "Pistola de calor 2000W, temperatura regulable 50-600°C"),
        ("P020", "Amoladora Angular Bosch", 55990, 14, "amoladora_angular.jpg", "Amoladora angular 750W, disco 115mm, empuñadura lateral")
    ]

    for codigo, nombre, valor, stock, imagen, descripcion in nuevos_productos:
        try:
            cursor.execute("""
                INSERT INTO productos (codigo, nombre, valor, stock, imagen, descripcion) 
                VALUES (?, ?, ?, ?, ?, ?)
            """, (codigo, nombre, valor, stock, imagen, descripcion))
            print(f"✅ Agregado: {codigo} - {nombre}")
        except sqlite3.IntegrityError:
            print(f"⚠️  Ya existe: {codigo}")

    conn.commit()
    conn.close()

    print("\n🎉 ¡CORRECCIÓN COMPLETADA!")
    print("✅ Imágenes existentes corregidas")
    print("✅ Productos nuevos agregados")
    print("\n📋 PRÓXIMO PASO: Generar imágenes faltantes")

if __name__ == "__main__":
    corregir_imagenes_y_productos()
