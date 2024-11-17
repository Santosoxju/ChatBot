import logging
from tensorflow.keras.models import load_model# type: ignore
from tensorflow.keras.preprocessing.text import Tokenizer# type: ignore
from tensorflow.keras.preprocessing.sequence import pad_sequences # type: ignore
import numpy as np
import json

# Configurar logging
logging.basicConfig(level=logging.INFO)

# Cargar el modelo entrenado
try:
    modelo = load_model("modelo_entrenado.h5")
    logging.info("Modelo cargado correctamente.")
except Exception as e:
    logging.error(f"Error al cargar el modelo: {str(e)}")
    exit()

# Cargar preguntas y respuestas desde el archivo JSON
try:
    with open('preguntas_respuestas.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
    logging.info("Archivo JSON cargado correctamente.")
except FileNotFoundError:
    logging.error("Error: El archivo preguntas_respuestas.json no se encuentra.")
    exit()
except json.JSONDecodeError as e:
    logging.error(f"Error al leer el archivo JSON: {str(e)}")
    exit()

# Extraer preguntas y respuestas
try:
    preguntas = [pregunta['pregunta'] for pregunta in data['preguntas']]
    respuestas = data['respuestas']
except KeyError as e:
    logging.error(f"Error al procesar el archivo JSON: clave no encontrada {str(e)}")
    exit()

# Inicializar el tokenizador y ajustarlo a las preguntas
tokenizer = Tokenizer()
tokenizer.fit_on_texts(preguntas)

# Clase para evaluar certeza con lógica difusa
class LogicaDifusa:
    @staticmethod
    def evaluar_certeza(input_text, probabilidad):
        """
        Evaluar la certeza de la respuesta basándose en la longitud de la pregunta
        y la probabilidad del modelo.
        """
        palabras = input_text.split()
        longitud = len(palabras)
        
        # Evaluación basada en la probabilidad y la longitud de la pregunta
        if probabilidad > 0.85:
            return "alta"
        elif longitud > 7 and probabilidad > 0.6:
            return "alta"
        elif 4 <= longitud <= 7:
            return "media"
        else:
            return "baja"

# Crear instancia de la lógica difusa
logica_difusa = LogicaDifusa()

def generar_respuesta_cliente(input_text):
    """
    Genera una respuesta para el cliente basado en el texto de entrada.
    Procesa el texto, realiza la predicción con el modelo y ajusta la respuesta
    según la certeza estimada.
    """
    try:
        if not input_text or input_text.strip() == "":
            return "Por favor, ingresa un mensaje válido."
        
        # Preprocesamiento y predicción de la respuesta
        input_sequence = tokenizer.texts_to_sequences([input_text])
        max_length = max(len(p.split()) for p in preguntas)  # Puede optimizarse si se sabe que el modelo tiene un max_length fijo
        input_sequence = pad_sequences(input_sequence, maxlen=max_length, padding='post')

        prediccion = modelo.predict(input_sequence)
        respuesta_index = np.argmax(prediccion)
        probabilidad = np.max(prediccion)  # Obtener la probabilidad de la predicción

        if respuesta_index < len(respuestas):
            respuesta = respuestas[respuesta_index]
        else:
            return "Lo siento, no tengo una respuesta para esa pregunta."

        # Integración de la lógica difusa para preguntas largas o complejas
        certeza = logica_difusa.evaluar_certeza(input_text, probabilidad)
        if certeza == "alta":
            return f"{respuesta} (Estoy a su disposición para cualquier información adicional que pueda necesitar.)"
        elif certeza == "media":
            return f"{respuesta} (Esta información debería ser útil; sin embargo, si necesita mayor precisión, no dude en consultarme nuevamente.)"
        else:
            return f"{respuesta} (La respuesta proporcionada podría no cubrir todos los detalles. Le sugiero que reformule su consulta para obtener una información más precisa.)"

    except Exception as e:
        logging.error(f"Error al generar respuesta: {str(e)}")
        return f"Error al generar respuesta: {str(e)}"
