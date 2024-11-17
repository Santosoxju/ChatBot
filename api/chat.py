from flask import Flask, request
from flask_socketio import SocketIO, send
import eventlet

# Esto es necesario para que Flask-SocketIO funcione correctamente en Vercel
eventlet.monkey_patch()

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

user_sessions = {}

@app.route('/')
def index():
    return "¡Bienvenido al servidor de chat!"

@socketio.on('message')
def handle_message(message):
    user_id = request.sid  # ID de sesión único
    estado_usuario = user_sessions.get(user_id, {"autenticado": False, "tipo": None, "email": None})

    if not estado_usuario["tipo"]:
        if "cliente" in message.lower():
            estado_usuario["tipo"] = "cliente"
            user_sessions[user_id] = estado_usuario
            send("Eres cliente. Puedes hacer preguntas.")
        elif "usuario" in message.lower():
            estado_usuario["tipo"] = "usuario"
            user_sessions[user_id] = estado_usuario
            send("Por favor, ingresa tu correo.")
        else:
            send("¿Eres cliente o usuario?")

    elif estado_usuario["tipo"] == "usuario" and not estado_usuario["autenticado"]:
        if "@" in message:
            estado_usuario["email"] = message
            send("Por favor, ingresa tu contraseña.")
        else:
            email = estado_usuario["email"]
            if email and verificar_usuario(email, message):
                estado_usuario["autenticado"] = True
                user_sessions[user_id] = estado_usuario
                send("Autenticación exitosa. Puedes hacer consultas.")
            else:
                send("Credenciales incorrectas. Inténtalo de nuevo.")

    elif estado_usuario["tipo"] == "usuario" and estado_usuario["autenticado"]:
        respuesta = ejecutar_consulta(message)
        send(respuesta)

    elif estado_usuario["tipo"] == "cliente":
        respuesta = generar_respuesta_cliente(message)
        send(respuesta)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=3000)
