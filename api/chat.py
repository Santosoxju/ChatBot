from flask import Flask, request
from flask_socketio import SocketIO
from conexion import verificar_usuario, ejecutar_consulta
from cliente import generar_respuesta_cliente
import json

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

user_sessions = {}

@app.route('/')
def index():
    return "¡Bienvenido al servidor de chat!"

# Manejo de mensajes desde el cliente
@socketio.on('message')
def handle_message(message):
    user_id = request.sid  # ID de sesión único
    estado_usuario = user_sessions.get(user_id, {"autenticado": False, "tipo": None, "email": None})

    # Si el usuario aún no ha sido identificado como cliente o usuario
    if not estado_usuario["tipo"]:
        if "cliente" in message.lower():
            estado_usuario["tipo"] = "cliente"
            user_sessions[user_id] = estado_usuario
            socketio.send("Eres cliente. Puedes hacer preguntas.")
        elif "usuario" in message.lower():
            estado_usuario["tipo"] = "usuario"
            user_sessions[user_id] = estado_usuario
            socketio.send("Por favor, ingresa tu correo.")
        else:
            socketio.send("¿Eres cliente o usuario?")

    elif estado_usuario["tipo"] == "usuario" and not estado_usuario["autenticado"]:
        if "@" in message:
            estado_usuario["email"] = message
            socketio.send("Por favor, ingresa tu contraseña.")
        else:
            email = estado_usuario["email"]
            if email and verificar_usuario(email, message):
                estado_usuario["autenticado"] = True
                user_sessions[user_id] = estado_usuario
                socketio.send("Autenticación exitosa. Puedes hacer consultas.")
            else:
                socketio.send("Credenciales incorrectas. Inténtalo de nuevo.")

    elif estado_usuario["tipo"] == "usuario" and estado_usuario["autenticado"]:
        respuesta = ejecutar_consulta(message)
        socketio.send(respuesta)

    elif estado_usuario["tipo"] == "cliente":
        respuesta = generar_respuesta_cliente(message)
        socketio.send(respuesta)

if __name__ == '__main__':
    #socketio.run(app, host='127.0.0.1', port=3000)
    socketio.run(app, host='0.0.0.0', port=3000)
