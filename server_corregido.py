import http.server
import socketserver
import urllib.parse
import os
import sqlite3

from model import product_model
from transbank.webpay.webpay_plus.transaction import Transaction
from transbank.common.options import WebpayOptions
from transbank.common.integration_type import IntegrationType
from transbank.common.integration_commerce_codes import IntegrationCommerceCodes
from transbank.common.integration_api_keys import IntegrationApiKeys
import uuid
import requests
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

                # Generar HTML para cada producto
                for producto in productos:
                    codigo, nombre, valor, stock, imagen, descripcion = producto

                    # Obtener precio en USD
                    try:
                        response = requests.get("http://localhost:5001/api/divisas/USD", timeout=2)
                        if response.status_code == 200:
                            data = response.json()
                            valor_usd = round(valor / data['valor'], 2)
                            precio_usd = f"${valor_usd} USD"
                        else:
                            precio_usd = "No disponible"
                    except:
                        precio_usd = "No disponible"

                    productos_html += f"""
                    <div class="product-card">
                        <img src="static/images/{imagen}" alt="{nombre}">
                        <h3>{nombre}</h3>
                        <p class="price">
                            ${valor:,} CLP<br>
                            <span style="color: #28a745; font-size: 0.9em;">{precio_usd}</span>
                        </p>
                        <p class="stock">Stock: {stock} unidades</p>
                        <p class="description">{descripcion}</p>
                        <button onclick="addToCart('{codigo}', '{nombre}', {valor})">Agregar al Carrito</button>
                        <button onclick="consultarStockAPI('{codigo}')" style="background: #28a745; margin-top: 5px;">
                            Consultar Stock API
                        </button>
                    </div>
                    """

                html = html.replace("{{productos}}", admin_button + productos_html)

            except Exception as e:
                print(f"ERROR en /catalog: {e}")
                html = html.replace("{{productos}}", f"<p>Error al cargar productos: {e}</p>")

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(html.encode("utf-8"))
            return

        elif self.path.startswith("/product_detail"): 
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            codigo = params.get("codigo", [""])[0]

            producto = product_model.obtener_producto_por_codigo(codigo)

            if producto:
                with open("view/product_detail.html", "r", encoding="utf-8") as file:
                    html = file.read()

                producto["imagen"] = f"/static/img/{producto['imagen']}"

                for key, value in producto.items():
                    html = html.replace(f"{{{{key}}}}", str(value))

                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(html.encode("utf-8"))
            else:
                self.send_error(404, "Producto no encontrado")
            return

        elif self.path.startswith("/add_to_cart"):
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            codigo = params.get("codigo", [""])[0]

            if codigo:
                for item in carrito:
                    if item["codigo"] == codigo:
                        item["cantidad"] += 1
                        break
                else:
                    carrito.append({"codigo": codigo, "cantidad": 1})

            self.send_response(302)
            self.send_header("Location", "/cart")
            self.end_headers()
            return

        elif self.path.startswith("/cart"):
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)

            codigo_sumar = params.get("sumar", [None])[0]
            codigo_restar = params.get("restar", [None])[0]
            codigo_eliminar = params.get("eliminar", [None])[0]

            if codigo_sumar:
                for item in carrito:
                    if item["codigo"] == codigo_sumar:
                        item["cantidad"] += 1
                        break

            if codigo_restar:
                for item in carrito:
                    if item["codigo"] == codigo_restar:
                        if item["cantidad"] > 1:
                            item["cantidad"] -= 1
                        break

            if codigo_eliminar:
                carrito[:] = [item for item in carrito if item["codigo"] != codigo_eliminar]

            with open("view/cart.html", "r", encoding="utf-8") as file:
                html = file.read()

            productos_html = ""
            total = 0

            if carrito:
                for item in carrito:
                    producto = product_model.obtener_producto_por_codigo(item["codigo"])
                    if producto:
                        subtotal = producto["valor"] * item["cantidad"]
                        total += subtotal
                        productos_html += f"""
                        <tr>
                            <td>{producto['nombre']}</td>
                            <td>
                                {item['cantidad']}
                                <a href="/cart?sumar={item['codigo']}">➕</a>
                                <a href="/cart?restar={item['codigo']}">➖</a>
                            </td>
                            <td>${subtotal}</td>
                            <td><a href="/cart?eliminar={item['codigo']}">❌</a></td>
                        </tr>
                        """
                mensaje = ""
            else:
                mensaje = "<strong>Tu carrito está vacío</strong>"

            html = html.replace("{{productos}}", productos_html)
            html = html.replace("{{total}}", f"${total}")
            html = html.replace("{{mensaje_carrito}}", mensaje)

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
                    # Consultar nuestra propia API de productos
                    import requests
                    response = requests.get(f"http://localhost:5000/api/productos/{codigo}/stock", timeout=2)

                    if response.status_code == 200:
                        stock_data = response.json()
                        mensaje = f"""
                        <div style="max-width: 600px; margin: 50px auto; padding: 20px; border: 2px solid #28a745; border-radius: 10px; background: #f8f9fa;">
                            <h2 style="color: #28a745;">📊 Consulta de Stock via API</h2>
                            <p><strong>Código:</strong> {stock_data['codigo']}</p>
                            <p><strong>Stock disponible:</strong> {stock_data['stock']} unidades</p>
                            <p><strong>Fuente:</strong> API REST Ferremas</p>
                            <p><strong>Endpoint:</strong> GET /api/productos/{codigo}/stock</p>
                            <hr>
                            <p style="font-size: 12px; color: #666;">Esta información fue obtenida mediante nuestra API REST, 
                            que puede ser consumida por otras tiendas o sucursales para consultar stock en tiempo real.</p>
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

        elif self.path == "/admin_productos":
            # Página de administración de productos
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Administración de Productos - Ferremas</title>
                <style>
                    body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
                    .form-container { background: #f8f9fa; padding: 30px; border-radius: 10px; border: 2px solid #007bff; }
                    .form-group { margin-bottom: 15px; }
                    label { display: block; margin-bottom: 5px; font-weight: bold; }
                    input, textarea, select { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
                    button { background: #28a745; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
                    button:hover { background: #218838; }
                    .back-btn { background: #6c757d; margin-right: 10px; }
                    .back-btn:hover { background: #545b62; }
                </style>
            </head>
            <body>
                <div class="form-container">
                    <h2>Administracion de Productos</h2>
                    <p>Agregar nuevo producto usando API REST</p>

                    <form id="productoForm">
                        <div class="form-group">
                            <label for="codigo">Codigo del Producto:</label>
                            <input type="text" id="codigo" name="codigo" required placeholder="Ej: P002">
                        </div>

                        <div class="form-group">
                            <label for="nombre">Nombre del Producto:</label>
                            <input type="text" id="nombre" name="nombre" required placeholder="Ej: Martillo Stanley">
                        </div>

                        <div class="form-group">
                            <label for="valor">Precio (CLP):</label>
                            <input type="number" id="valor" name="valor" required placeholder="Ej: 25990">
                        </div>

                        <div class="form-group">
                            <label for="stock">Stock:</label>
                            <input type="number" id="stock" name="stock" required placeholder="Ej: 20">
                        </div>

                        <div class="form-group">
                            <label for="imagen">Nombre de la imagen:</label>
                            <input type="text" id="imagen" name="imagen" required placeholder="Ej: martillo.jpg">
                        </div>

                        <div class="form-group">
                            <label for="descripcion">Descripcion:</label>
                            <textarea id="descripcion" name="descripcion" rows="3" placeholder="Descripcion del producto..."></textarea>
                        </div>

                        <button type="button" class="back-btn" onclick="window.location.href='/catalog'">← Volver al Catalogo</button>
                        <button type="submit">Agregar Producto via API</button>
                    </form>

                    <div id="resultado" style="margin-top: 20px;"></div>
                </div>

                <script>
                document.getElementById('productoForm').addEventListener('submit', async function(e) {
                    e.preventDefault();

                    const formData = {
                        codigo: document.getElementById('codigo').value,
                        nombre: document.getElementById('nombre').value,
                        valor: parseInt(document.getElementById('valor').value),
                        stock: parseInt(document.getElementById('stock').value),
                        imagen: document.getElementById('imagen').value,
                        descripcion: document.getElementById('descripcion').value
                    };

                    try {
                        const response = await fetch('http://localhost:5000/api/productos', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify(formData)
                        });

                        const result = await response.json();

                        if (response.ok) {
                            document.getElementById('resultado').innerHTML = `
                            <div style="background: #d4edda; color: #155724; padding: 15px; border-radius: 5px; border: 1px solid #c3e6cb;">
                                <h3>✅ ¡Producto agregado exitosamente!</h3>
                                <p><strong>Código:</strong> ${result.codigo}</p>
                                <p><strong>Nombre:</strong> ${result.nombre}</p>
                                <p><strong>Precio:</strong> $${result.valor}</p>
                                <p><strong>Stock:</strong> ${result.stock} unidades</p>
                                <a href="/catalog" style="background: #007bff; color: white; padding: 8px 16px; text-decoration: none; border-radius: 4px;">Ver en Catálogo</a>
                            </div>
                            `;
                            document.getElementById('productoForm').reset();
                        } else {
                            throw new Error(result.error || 'Error desconocido');
                        }
                    } catch (error) {
                        document.getElementById('resultado').innerHTML = `
                        <div style="background: #f8d7da; color: #721c24; padding: 15px; border-radius: 5px; border: 1px solid #f5c6cb;">
                            <h3>❌ Error al agregar producto</h3>
                            <p>${error.message}</p>
                        </div>
                        `;
                    }
                });
                </script>
            </body>
            </html>
            """

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(html.encode("utf-8"))
            return

        elif self.path == "/checkout":
            # Calcular el total del carrito
            total = 0
            for item in carrito:
                producto = product_model.obtener_producto_por_codigo(item["codigo"])
                if producto:
                    subtotal = producto["valor"] * item["cantidad"]
                    total += subtotal

            # Crear una orden de compra única
            buy_order = uuid.uuid4().hex[:26]
            session_id = str(uuid.uuid4())
            return_url = "http://localhost:8000/confirmacion_pago"

            # Crear la transacción
            tx = Transaction(webpay_options)
            response = tx.create(buy_order, session_id, total, return_url)

            # Redirigir al usuario al formulario de pago de Webpay
            self.send_response(302)
            self.send_header("Location", response['url'] + "?token_ws=" + response['token'])
            self.end_headers()
            return

        elif self.path.startswith("/confirmacion_pago"):
            parsed_url = urllib.parse.urlparse(self.path)
            query = urllib.parse.parse_qs(parsed_url.query)

            tbk_token = query.get('TBK_TOKEN', [None])[0]
            tbk_orden_compra = query.get('TBK_ORDEN_COMPRA', [None])[0]
            tbk_id_sesion = query.get('TBK_ID_SESION', [None])[0]

            # Aquí se puede procesar el resultado

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            if tbk_token is None:
                mensaje = "<h1>Pago aprovado</h1>"
            else:
                mensaje = f"<h1>Pago cancelado</h1><p>Orden: {tbk_orden_compra}</p>"

            self.wfile.write(f"""
            <html><body>
                {mensaje}
                <p><a href='/catalog'>Volver al catalogo</a></p>
            </body></html>
            """.encode("utf-8"))
            return

        elif self.path == "/agregar_producto":
            with open("view/agregar_producto.html", "r", encoding="utf-8") as file:
                html = file.read()

            mensaje = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query).get("mensaje", [""])[0]
            html = html.replace("{{mensaje}}", f"<p style='color:green;'>{mensaje}</p>" if mensaje else "")

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(html.encode("utf-8"))
            return

        elif self.path.startswith("/static/"):
            return http.server.SimpleHTTPRequestHandler.do_GET(self)

        else:
            self.send_error(404)
            return

        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        if self.path == "/login":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            fields = urllib.parse.parse_qs(post_data.decode('utf-8'))

            email = fields.get('email', [''])[0]
            password = fields.get('password', [''])[0]

            try:
                conn = sqlite3.connect("ferremas.db")
                cursor = conn.cursor()

                cursor.execute("SELECT * FROM usuarios WHERE email = ? AND password = ?", (email, password))
                usuario_valido = cursor.fetchone()

                if usuario_valido:
                    self.send_response(302)
                    self.send_header("Location", "/catalog")
                    self.end_headers()
                else:
                    self.send_response(302)
                    self.send_header("Location", "/login?error=1")
                    self.end_headers()
            except Exception as e:
                print("Error en login:", e)
                self.send_error(500, "Error interno del servidor")
            finally:
                conn.close()

        elif self.path.startswith("/register"):
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            fields = urllib.parse.parse_qs(post_data.decode('utf-8'))

            nombre = fields.get('nombre', [''])[0]
            email = fields.get('email', [''])[0]
            password = fields.get('password', [''])[0]

            try:
                conn = sqlite3.connect("ferremas.db")
                cursor = conn.cursor()

                # Verificar si ya existe email
                cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
                existente = cursor.fetchone()

                if existente:
                    # Si existe, redirigir con error
                    self.send_response(302)
                    self.send_header("Location", "/register?error=1")
                    self.end_headers()
                else:
                    # Insertar nuevo usuario
                    cursor.execute("INSERT INTO usuarios (name, email, password) VALUES (?, ?, ?)",
                                 (nombre, email, password))
                    conn.commit()

                    # Redirigir a login con mensaje de éxito
                    self.send_response(302)
                    self.send_header("Location", "/login?registered=1")
                    self.end_headers()
            except Exception as e:
                print("Error al registrar usuario:", e)
                self.send_error(500, "Error interno del servidor")
            finally:
                conn.close()

        elif self.path == "/confirmacion_pago":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            fields = urllib.parse.parse_qs(post_data.decode('utf-8'))
            token = fields.get('token_ws', [''])[0]

            # Confirmar la transacción
            tx = Transaction(webpay_options)
            result = tx.commit(token)

            # Verificar el resultado de la transacción
            if result['status'] == 'AUTHORIZED':
                carrito.clear()  # Vaciar el carrito
                mensaje = "Pago realizado con éxito. Gracias por su compra."
            else:
                mensaje = "El pago no fue autorizado. Intente nuevamente."

            # Mostrar la confirmación
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(f"<html><body><h1>{mensaje}</h1></body></html>".encode("utf-8"))
            return

        elif self.path == "/agregar_producto": 
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            fields = urllib.parse.parse_qs(post_data.decode('utf-8'))

            codigo = fields.get('codigo', [''])[0]
            nombre = fields.get('nombre', [''])[0]
            valor = int(fields.get('valor', ['0'])[0])
            descripcion = fields.get('descripcion', [''])[0]
            imagen = fields.get('imagen', [''])[0]
            stock = int(fields.get('stock', ['0'])[0])

            try:
                conn = sqlite3.connect("ferremas.db")
                cursor = conn.cursor()

                # Verificar si ya existe producto con mismo código
                cursor.execute("SELECT * FROM productos WHERE codigo = ?", (codigo,))
                if cursor.fetchone():
                    self.send_response(302)
                    self.send_header("Location", "/agregar_producto?mensaje=Ya+existe+un+producto+con+ese+codigo.")
                    self.end_headers()
                else:
                    cursor.execute(
                        "INSERT INTO productos (codigo, nombre, descripcion, stock, valor, imagen) VALUES (?, ?, ?, ?, ?, ?)",
                        (codigo, nombre, descripcion, stock, valor, imagen)
                    )
                    conn.commit()

                    self.send_response(302)
                    self.send_header("Location", "/catalog")
                    self.end_headers()

            except Exception as e:
                print("Error al agregar producto:", e)
                self.send_error(500, "Error interno del servidor")
            finally:
                conn.close()

        else:
            self.send_error(501, "Unsupported method (POST)")


# Cambiar el directorio raíz para servir archivos desde el proyecto
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# para poder utilizarlo en otro pc
with socketserver.TCPServer(("0.0.0.0", PORT), MyHandler) as httpd:
    print(f"Servidor corriendo en http://localhost:{PORT}")
    httpd.serve_forever()
