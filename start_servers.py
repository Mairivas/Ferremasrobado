import subprocess
import time
import threading
import sys
import os

def start_api_productos():
    """Inicia la API de productos en puerto 5000"""
    try:
        print("🚀 Iniciando API de Productos (puerto 5000)...")
        subprocess.run([sys.executable, "api_productos.py"])
    except Exception as e:
        print(f"❌ Error iniciando API de productos: {e}")

def start_api_divisas():
    """Inicia la API de divisas en puerto 5001"""
    try:
        print("💱 Iniciando API de Divisas (puerto 5001)...")
        subprocess.run([sys.executable, "api_divisas.py"])
    except Exception as e:
        print(f"❌ Error iniciando API de divisas: {e}")

def start_main_server():
    """Inicia el servidor principal en puerto 8000"""
    try:
        print("⏳ Esperando que las APIs inicien...")
        time.sleep(3)  # Esperar que las APIs inicien completamente
        print("🌐 Iniciando Servidor Principal (puerto 8000)...")
        subprocess.run([sys.executable, "server.py"])
    except Exception as e:
        print(f"❌ Error iniciando servidor principal: {e}")

def check_files():
    """Verifica que todos los archivos necesarios existan"""
    required_files = ["api_productos.py", "api_divisas.py", "server.py"]
    missing_files = []

    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)

    if missing_files:
        print(f"❌ Archivos faltantes: {', '.join(missing_files)}")
        print("Asegúrate de estar en el directorio correcto del proyecto")
        return False
    return True

if __name__ == "__main__":
    print("=" * 50)
    print("🏪 FERREMAS - INICIADOR DE SERVIDORES")
    print("=" * 50)

    # Verificar archivos
    if not check_files():
        sys.exit(1)

    print("✅ Todos los archivos encontrados")
    print("🔄 Iniciando servidores...")
    print()

    try:
        # Iniciar APIs en hilos separados (daemon=True para que terminen con el programa principal)
        thread_productos = threading.Thread(target=start_api_productos, daemon=True)
        thread_divisas = threading.Thread(target=start_api_divisas, daemon=True)

        thread_productos.start()
        thread_divisas.start()

        # Iniciar servidor principal (este bloquea hasta que se cierre)
        start_main_server()

    except KeyboardInterrupt:
        print("\n🛑 Cerrando servidores...")
        print("👋 ¡Hasta luego!")
    except Exception as e:
        print(f"❌ Error general: {e}")
