
import subprocess
import sys
import time
import os

def iniciar_servidores():
    print("🚀 INICIANDO SERVIDORES SIN REQUESTS...")

    try:
        # Iniciar API productos
        print("📦 Iniciando API Productos (puerto 5000)...")
        proceso_productos = subprocess.Popen([sys.executable, "api_productos.py"])
        time.sleep(2)

        # Iniciar API divisas  
        print("💱 Iniciando API Divisas (puerto 5001)...")
        proceso_divisas = subprocess.Popen([sys.executable, "api_divisas.py"])
        time.sleep(2)

        # Iniciar servidor principal
        print("🌐 Iniciando Servidor Principal (puerto 8000)...")
        proceso_servidor = subprocess.Popen([sys.executable, "server.py"])

        print("\n✅ TODOS LOS SERVIDORES INICIADOS")
        print("🌐 Página: http://localhost:8000")
        print("\n⚠️  MANTÉN ESTA VENTANA ABIERTA")
        print("⚠️  Para detener: Ctrl + C")

        # Esperar
        input("\nPresiona ENTER para detener todos los servidores...")

        # Terminar procesos
        proceso_productos.terminate()
        proceso_divisas.terminate() 
        proceso_servidor.terminate()

    except KeyboardInterrupt:
        print("\n🛑 Deteniendo servidores...")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    iniciar_servidores()
