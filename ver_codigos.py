
import sqlite3

def ver_codigos_disponibles():
    try:
        conn = sqlite3.connect('productos.db')
        cursor = conn.cursor()

        # Obtener todos los códigos existentes
        cursor.execute("SELECT codigo FROM productos ORDER BY codigo")
        codigos_existentes = [row[0] for row in cursor.fetchall()]

        print("🔍 CÓDIGOS EXISTENTES:")
        for codigo in codigos_existentes:
            print(f"   ✅ {codigo}")

        print()
        print("💡 CÓDIGOS DISPONIBLES PARA USAR:")

        # Buscar el siguiente código disponible
        for i in range(17, 25):  # P017 a P024
            codigo_test = f"P{i:03d}"
            if codigo_test not in codigos_existentes:
                print(f"   🆓 {codigo_test} - DISPONIBLE")
                break

        conn.close()

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    ver_codigos_disponibles()
