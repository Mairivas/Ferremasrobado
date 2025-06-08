import subprocess
import sys
import time
import os

def iniciar_servidores():
    print("🚀 INICIANDO TODOS LOS SERVIDORES...")

    try:
        # Verificar que los archivos existen
        archivos_necesarios = ['api_productos.py', 'api_divisas_corregida.py', 'server.py']
        for archivo in archivos_necesarios:
            if not os.path.exists(archivo):
                print(f"❌ Error: No se encuentra {archivo}")
                return

        print("✅ Todos los archivos encontrados")

        # Iniciar API productos
        print("📦 Iniciando API Productos (puerto 5000)...")
        proceso_productos = subprocess.Popen([sys.executable, "api_productos.py"])
        time.sleep(3)

        # Iniciar API divisas CORREGIDA
        print("💱 Iniciando API Divisas (puerto 5001)...")
        proceso_divisas = subprocess.Popen([sys.executable, "api_divisas_corregida.py"])
        time.sleep(3)

        # Iniciar servidor principal
        print("🌐 Iniciando Servidor Principal (puerto 8000)...")
        proceso_servidor = subprocess.Popen([sys.executable, "server.py"])

        print("\n" + "="*50)
        print("✅ TODOS LOS SERVIDORES INICIADOS")
        print("🌐 Página: http://localhost:8000")
        print("📦 API Productos: http://localhost:5000")
        print("💱 API Divisas: http://localhost:5001")
        print("="*50)
        print("\n⚠️  MANTÉN ESTA VENTANA ABIERTA")
        print("⚠️  Para detener: Ctrl + C")

        # Esperar
        input("\nPresiona ENTER para detener todos los servidores...")

        # Terminar procesos
        print("\n🛑 Deteniendo servidores...")
        proceso_productos.terminate()
        proceso_divisas.terminate() 
        proceso_servidor.terminate()
        print("✅ Servidores detenidos")

    except KeyboardInterrupt:
        print("\n🛑 Deteniendo servidores...")
        try:
            proceso_productos.terminate()
            proceso_divisas.terminate() 
            proceso_servidor.terminate()
        except:
            pass
        print("✅ Servidores detenidos")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    iniciar_servidores()
