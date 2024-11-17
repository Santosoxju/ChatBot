from flask import Flask, request, jsonify
from cliente import generar_respuesta_cliente
from conexion import verificar_usuario, ejecutar_consulta
import json

app = Flask(__name__)

user_sessions = {}

@app.route('/chat', methods=['POST'])
def chat():
    # Extract message and session ID from the request
    data = request.json
    message = data.get('message')
    user_id = data.get('user_id')  # User session ID
    
    estado_usuario = user_sessions.get(user_id, {"autenticado": False, "tipo": None, "email": None})

    # If user type is not defined, handle identification
    if not estado_usuario["tipo"]:
        if "cliente" in message.lower():
            estado_usuario["tipo"] = "cliente"
            user_sessions[user_id] = estado_usuario
            return jsonify({"response": "Eres cliente. Puedes hacer preguntas."})
        elif "usuario" in message.lower():
            estado_usuario["tipo"] = "usuario"
            user_sessions[user_id] = estado_usuario
            return jsonify({"response": "Por favor, ingresa tu correo."})
        else:
            return jsonify({"response": "¿Eres cliente o usuario?"})

    elif estado_usuario["tipo"] == "usuario" and not estado_usuario["autenticado"]:
        if "@" in message:
            estado_usuario["email"] = message
            return jsonify({"response": "Por favor, ingresa tu contraseña."})
        else:
            email = estado_usuario["email"]
            if email and verificar_usuario(email, message):
                estado_usuario["autenticado"] = True
                user_sessions[user_id] = estado_usuario
                return jsonify({"response": "Autenticación exitosa. Puedes hacer consultas."})
            else:
                return jsonify({"response": "Credenciales incorrectas. Inténtalo de nuevo."})

    elif estado_usuario["tipo"] == "usuario" and estado_usuario["autenticado"]:
        respuesta = ejecutar_consulta(message)
        return jsonify({"response": respuesta})

    elif estado_usuario["tipo"] == "cliente":
        respuesta = generar_respuesta_cliente(message)
        return jsonify({"response": respuesta})

if __name__ == '__main__':
    app.run(debug=True)
