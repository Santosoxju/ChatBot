import json
import numpy as np
import psycopg2
import bcrypt
from tensorflow.keras.models import load_model# type: ignore
from tensorflow.keras.preprocessing.text import Tokenizer # type: ignore
from tensorflow.keras.preprocessing.sequence import pad_sequences # type: ignore
import re

# Cargar el modelo entrenado
model = load_model("api/modelo_entrenadoBD.h5")

# Cargar preguntas y respuestas desde el archivo JSON
with open('preguntas_respuestasBD.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# Preparar el tokenizador con las preguntas
preguntas = list(data.keys())  # Las claves son las preguntas
respuestas = [data[p]["consulta"] for p in preguntas]
tokenizer = Tokenizer()
tokenizer.fit_on_texts(preguntas)

# Diccionarios de índice para consultas
respuesta_indices = {res: i for i, res in enumerate(respuestas)}
indices_respuesta = {i: res for res, i in respuesta_indices.items()}
max_length = max(len(p.split()) for p in preguntas)

# Configuración de la base de datos
DATABASE = {
    'dbname': 'constructora',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'localhost',
    'port': '5432'
}

def conectar_bd():
    """Establece la conexión con la base de datos."""
    try:
        conexion = psycopg2.connect(
            dbname=DATABASE['dbname'],
            user=DATABASE['user'],
            password=DATABASE['password'],
            host=DATABASE['host'],
            port=DATABASE['port']
        )
        return conexion
    except psycopg2.DatabaseError as e:
        print(f"Error en la conexión a la base de datos: {str(e)}")
        return None

def verificar_usuario(email, password):
    """Verifica si las credenciales del usuario son correctas."""
    try:
        with conectar_bd() as conexion:
            if conexion:
                cursor = conexion.cursor()
                cursor.execute("SELECT password FROM usuarios WHERE email = %s", (email,))
                resultado = cursor.fetchone()
                if resultado:
                    hashed_password = resultado[0]
                    # Comprobar la contraseña usando bcrypt
                    return bcrypt.checkpw(password.encode(), hashed_password.encode())
        return False
    except psycopg2.DatabaseError as e:
        print(f"Error en la base de datos al verificar usuario: {str(e)}")
        return False
    except Exception as e:
        print(f"Error desconocido al verificar usuario: {str(e)}")
        return False


def generar_consulta(input_text):
    """Genera la consulta SQL basada en el texto de entrada."""
    try:
        # Preprocesar el texto de entrada
        input_sequence = tokenizer.texts_to_sequences([input_text])
        input_padded = pad_sequences(input_sequence, maxlen=max_length, padding='post')

        # Hacer la predicción
        prediccion = model.predict(input_padded)
        respuesta_index = np.argmax(prediccion)
        
        # Imprimir para depuración
        print(f"Input: {input_text}")
        print(f"Predicción: {prediccion}")
        print(f"Índice de respuesta: {respuesta_index}")

        # Obtener la consulta correspondiente
        consulta = respuestas[respuesta_index] if respuesta_index < len(respuestas) else None
        
        if not consulta:
            return None, []  # Si no se genera consulta, devolver None

        # Verificar si la consulta requiere parámetros y extraerlos del input_text
        parametros = []
        if '%s' in consulta:
            # Extraemos los valores basados en palabras clave en la entrada
            if 'correo' in input_text:
                email = re.search(r"correo (\S+)", input_text)
                if email:
                    parametros = (email.group(1),)
            elif 'empresa' in input_text:
                empresa = re.search(r"empresa (\S+)", input_text)
                if empresa:
                    parametros = (empresa.group(1),)
            elif 'proyecto' in input_text:
                proyecto_id = re.search(r"proyecto (\d+)", input_text)
                if proyecto_id:
                    parametros = (int(proyecto_id.group(1)),)
                else:
                    return None, []  # Si el parámetro no es válido, retornar None
            elif 'solicitud' in input_text:
                folio_solicitud = re.search(r"solicitud (\d+)", input_text)
                if folio_solicitud:
                    parametros = (int(folio_solicitud.group(1)),)
                else:
                    return None, []  # Si el parámetro no es válido, retornar None

        # Imprimir para depuración
        print(f"Consulta generada: {consulta}")
        print(f"Parámetros extraídos: {parametros}")

        return consulta, parametros
    except Exception as e:
        print(f"Error al generar consulta: {str(e)}")
        return None, []

def ejecutar_consulta(input_text):
    """Ejecuta la consulta SQL generada por el modelo."""
    try:
        consulta, parametros = generar_consulta(input_text)
        if consulta is None:
            return "No entiendo la pregunta. Por favor, intenta con otra consulta."  # Mensaje de error más claro

        # Ejecutar la consulta en la base de datos
        with conectar_bd() as conexion:
            if conexion:
                cursor = conexion.cursor()
                if parametros:
                    cursor.execute(consulta, parametros)
                else:
                    cursor.execute(consulta)
                
                resultados = cursor.fetchall()
                # Formatear los resultados para hacerlos más legibles
                if not resultados:
                    return "No se encontraron resultados para esta consulta."
                else:
                    # Convertir cada resultado a una cadena legible (opcional: presentarlo en tabla)
                    return "\n".join([str(r) for r in resultados])
    except psycopg2.DatabaseError as e:
        return f"Error en la base de datos: {str(e)}"
    except Exception as e:
        return f"Error desconocido: {str(e)}"


