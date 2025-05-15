import http.server
import socketserver
import urllib.parse
import os

PORT = 8000

# Usuario registrado de ejemplo
USUARIO_REGISTRADO = {
    "email": "cliente1@gmail.com",
    "password": "Cliente.01"
}

class MyHandler(http.server.SimpleHTTPRequestHandler):

    def do_GET(self):
        if self.path == "/":
            self.path = "view/index.html"
        elif self.path == "/login":
            self.path = "view/login.html"
        elif self.path == "/catalog":
            self.path = "view/catalog.html"
        elif self.path.startswith("/product_detail"):
            self.path = "view/product_detail.html"
        elif self.path == "/cart":
            self.path = "view/cart.html"
        elif self.path == "/checkout":
            self.path = "view/checkout.html"
        elif self.path.startswith("/static/"):
            # Aquí dejamos que SimpleHTTPRequestHandler maneje los archivos estáticos
            return http.server.SimpleHTTPRequestHandler.do_GET(self)
        else:
            self.send_error(404)
            return

        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        if self.path == "/login":
            # Leer datos enviados por POST
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            fields = urllib.parse.parse_qs(post_data.decode('utf-8'))

            email = fields.get('email', [''])[0]
            password = fields.get('password', [''])[0]

            if email == USUARIO_REGISTRADO["email"] and password == USUARIO_REGISTRADO["password"]:
                # Redirigir a catálogo
                self.send_response(302)
                self.send_header("Location", "/catalog")
                self.end_headers()
            else:
                # Redirigir al login con error
                self.send_response(302)
                self.send_header("Location", "/login?error=1")
                self.end_headers()
        else:
            self.send_error(501, "Unsupported method (POST)")

# Cambiar el directorio raíz para servir archivos desde el proyecto
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Levantar servidor
with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
    print(f"Servidor corriendo en http://localhost:{PORT}")
    httpd.serve_forever()