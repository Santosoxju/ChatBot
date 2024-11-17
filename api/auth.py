import bcrypt
from conexion import conectar_bd

class Auth:
    def __init__(self):
        self.db = conectar_bd()

    def verificar_usuario(email, password):
        """Verifica si las credenciales del usuario son correctas."""
        with conectar_bd() as conexion:
            cursor = conexion.cursor()
        cursor.execute("SELECT password FROM usuarios WHERE email = %s", (email,))
        resultado = cursor.fetchone()
        if resultado:
            hashed_password = resultado[0]
            return bcrypt.checkpw(password.encode(), hashed_password.encode())
        return False
