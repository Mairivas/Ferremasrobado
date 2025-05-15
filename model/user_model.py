 # Simulación de base de datos de usuarios
usuarios = [
    {"email": "cliente1@gmail.com", "password": "Cliente.01"}
]

def verificar_usuario(email, password):
    for user in usuarios:
        if user["email"] == email and user["password"] == password:
            return True
    return False

