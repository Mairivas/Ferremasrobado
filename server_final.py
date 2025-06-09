import http.server
import socketserver
import urllib.parse
import os
import sqlite3
import requests

from model import product_model
from transbank.webpay.webpay_plus.transaction import Transaction
from transbank.common.options import WebpayOptions
from transbank.common.integration_type import IntegrationType
from transbank.common.integration_commerce_codes import IntegrationCommerceCodes
from transbank.common.integration_api_keys import IntegrationApiKeys
import uuid

webpay_options = WebpayOptions(
    commerce_code=IntegrationCommerceCodes.WEBPAY_PLUS,
    api_key=IntegrationApiKeys.WEBPAY,
    integration_type=IntegrationType.TEST
)

PORT = 8000

# Carrito de prueba
carrito = []

class MyHandler(http.server.SimpleHTTPRequestHandler):

    def do_GET(self):
        if self.path == "/":
            self.path = "view/index.html"

        elif self.path.startswith("/login"):
            with open("view/login.html", "r", encoding="utf-8") as file:
                html = file.read()

            # Mostrar mensaje si viene de registro exitoso
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            mensaje_html = ""
            if params.get("registered", ["0"])[0] == "1":
                mensaje_html = '<p style="color:green;">¡Registro exitoso! Ahora puedes iniciar sesión.</p>'
            elif params.get("error", ["0"])[0] == "1":
                mensaje_html = '<p style="color:red;">Correo o contraseña incorrectos.</p>'

            html = html.replace("{{mensaje}}", mensaje_html)

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(html.encode("utf-8"))
            return

        elif self.path.startswith("/register"):
            with open("view/register.html", "r", encoding="utf-8") as file:
                html = file.read()

            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            error_html = ""
            if params.get("error", ["0"])[0] == "1":
                error_html = '<p style="color:red;">El correo ya está registrado.</p>'
            html = html.replace("{{error}}", error_html)

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(html.encode("utf-8"))
            return

        elif self.path == "/catalog":
            with open("view/catalog.html", "r", encoding="utf-8") as file:
                html = file.read()

            productos_html = ""

            # Botón para administrar productos
            admin_button = """
            <div style="text-align: center; margin: 20px 0;">
                <a href="/admin_productos" style="background: #ffc107; color: #212529; padding: 12px 24px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                    🛠️ Administrar Productos (API)
                </a>
            </div>
            """    

            try:
                conn = sqlite3.connect('ferremas.db')
                cursor = conn.cursor()
                cursor.execute("SELECT codigo, nombre, valor, stock, imagen, descripcion FROM productos ORDER BY id")
                productos = cursor.fetchall()
                conn.close()

                print(f"DEBUG: Se obtuvieron {len(productos)} productos de la BD")

                # Generar HTML para cada producto - CON CONVERSIÓN CORREGIDA
                for producto in productos:
                    codigo, nombre, valor, stock, imagen, descripcion = producto

                    productos_html += f"""
                    <div class="product-card">
                        <img src="static/img/{imagen}" alt="{nombre}">
                        <h3>{nombre}</h3>
                        <p class="price">
                            ${valor:,} CLP<br>
                            <span style="color: #28a745; font-size: 0.9em;">
                                <button onclick="consultarDivisas('{codigo}', {valor})" style="background: #17a2b8; color: white; border: none; padding: 5px 10px; border-radius: 3px; cursor: pointer;">
                                    💱 Ver en USD
                                </button>
                            </span>
                        </p>
                        <p class="stock">Stock: {stock} unidades</p>
                        <p class="description">{descripcion}</p>
                        <button onclick="addToCart('{codigo}', '{nombre}', {valor})">Agregar al Carrito</button>
                        <button onclick="consultarStockAPI('{codigo}')" style="background: #28a745; margin-top: 5px;">
                            Consultar Stock API
                        </button>
                    </div>
                    """

                # JavaScript CORREGIDO para conversión de divisas
                javascript_code = """
                <script>
                    // ==================== CARRITO FUNCIONAL ====================
                    let carrito = JSON.parse(localStorage.getItem('carrito')) || [];

                    // Función para agregar productos al carrito
                    function addToCart(codigo, nombre, valor) {
                        const productoExistente = carrito.find(item => item.codigo === codigo);
                        
                        if (productoExistente) {
                            productoExistente.cantidad += 1;
                            alert(`Se aumentó la cantidad de ${nombre} en el carrito`);
                        } else {
                            const nuevoProducto = {
                                codigo: codigo,
                                nombre: nombre,
                                valor: valor,
                                cantidad: 1
                            };
                            carrito.push(nuevoProducto);
                            alert(`${nombre} agregado al carrito`);
                        }
                        
                        localStorage.setItem('carrito', JSON.stringify(carrito));
                    }

                    async function consultarDivisas(codigo, valorCLP) {
                        const button = event.target;
                        button.innerHTML = '⏳ Consultando...';
                        button.disabled = true;

                        try {
                            const response = await fetch(`http://localhost:5001/api/divisas/convertir/USD/${valorCLP}`, {
                                method: 'GET'
                            });

                            if (response.ok) {
                                const data = await response.json();
                                const valorUSD = data.monto_convertido;
                                button.innerHTML = `$${valorUSD} USD`;
                                button.style.background = '#28a745';
                            } else {
                                button.innerHTML = 'API no disponible';
                                button.style.background = '#dc3545';
                            }
                        } catch (error) {
                            button.innerHTML = 'Error conexión';
                            button.style.background = '#dc3545';
                        }

                        setTimeout(() => {
                            button.innerHTML = '💱 Ver en USD';
                            button.style.background = '#17a2b8';
                            button.disabled = false;
                        }, 5000);
                    }

                    async function consultarStockAPI(codigo) {
                        window.location.href = `/consultar_stock_api?codigo=${codigo}`;
                    }
                </script>
                """

                html = html.replace("{{productos}}", admin_button + productos_html + javascript_code)

            except Exception as e:
                print(f"ERROR en /catalog: {e}")
                html = html.replace("{{productos}}", f"<p>Error al cargar productos: {e}</p>")

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(html.encode("utf-8"))
            return
        
        elif self.path == "/cart":
            with open("view/cart.html", "r", encoding="utf-8") as file:
                html = file.read()

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(html.encode("utf-8"))
            return

        elif self.path.startswith("/consultar_stock_api"):
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            codigo = params.get("codigo", [""])[0]

            if codigo:
                try:
                    response = requests.get(f"http://localhost:5000/api/productos/{codigo}/stock", timeout=2)

                    if response.status_code == 200:
                        stock_data = response.json()
                        mensaje = f"""
                        <div style="max-width: 600px; margin: 50px auto; padding: 20px; border: 2px solid #28a745; border-radius: 10px; background: #f8f9fa;">
                            <h2 style="color: #28a745;">📊 Consulta de Stock via API</h2>
                            <p><strong>Código:</strong> {stock_data['codigo']}</p>
                            <p><strong>Stock disponible:</strong> {stock_data['stock']} unidades</p>
                            <p><strong>Fuente:</strong> API REST Ferremas</p>
                            <a href="/catalog" style="background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">← Volver al Catálogo</a>
                        </div>
                        """
                    else:
                        mensaje = f"""
                        <div style="max-width: 600px; margin: 50px auto; padding: 20px; border: 2px solid #dc3545; border-radius: 10px;">
                            <h2 style="color: #dc3545;">❌ Error en API</h2>
                            <p>No se pudo consultar el stock del producto {codigo}</p>
                            <a href="/catalog" style="background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">← Volver al Catálogo</a>
                        </div>
                        """
                except Exception as e:
                    mensaje = f"""
                    <div style="max-width: 600px; margin: 50px auto; padding: 20px; border: 2px solid #dc3545; border-radius: 10px;">
                        <h2 style="color: #dc3545;">❌ Error de Conexión</h2>
                        <p>No se pudo conectar con la API de productos</p>
                        <p>Error: {str(e)}</p>
                        <a href="/catalog" style="background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">← Volver al Catálogo</a>
                    </div>
                    """
            else:
                mensaje = "<p>Código de producto no válido</p>"

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(f"""
            <!DOCTYPE html>
            <html>
            <head><title>Consulta Stock API - Ferremas</title></head>
            <body>{mensaje}</body>
            </html>
            """.encode("utf-8"))
            return

        elif self.path.startswith("/static/"):
            return http.server.SimpleHTTPRequestHandler.do_GET(self)

        else:
            self.send_error(404)
            return

        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        if self.path == "/login":
            # Manejar login
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            self.send_response(302)
            self.send_header('Location', '/catalog')
            self.end_headers()
            return
        
        elif self.path == "/register":
            # Manejar registro
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            self.send_response(302)
            self.send_header('Location', '/login?registered=1')
            self.end_headers()
            return
        
        else:
            self.send_error(404, "Not Found")


# Cambiar el directorio raíz para servir archivos desde el proyecto
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# para poder utilizarlo en otro pc
with socketserver.TCPServer(("0.0.0.0", PORT), MyHandler) as httpd:
    print(f"🚀 Servidor corriendo en http://localhost:{PORT}")
    httpd.serve_forever()
