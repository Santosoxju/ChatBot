# logica_difusa.py
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

class LogicaDifusa:
    def __init__(self):
        # Definir variables difusas
        self.longitud_pregunta = ctrl.Antecedent(np.arange(0, 101, 1), 'longitud_pregunta')
        self.palabras_clave = ctrl.Antecedent(np.arange(0, 11, 1), 'palabras_clave')
        self.certeza = ctrl.Consequent(np.arange(0, 101, 1), 'certeza')

        # Definir funciones de pertenencia para la longitud de la pregunta
        self.longitud_pregunta['corta'] = fuzz.trimf(self.longitud_pregunta.universe, [0, 0, 50])
        self.longitud_pregunta['media'] = fuzz.trimf(self.longitud_pregunta.universe, [0, 50, 100])
        self.longitud_pregunta['larga'] = fuzz.trimf(self.longitud_pregunta.universe, [50, 100, 100])

        # Definir funciones de pertenencia para el número de palabras clave
        self.palabras_clave['pocas'] = fuzz.trimf(self.palabras_clave.universe, [0, 0, 5])
        self.palabras_clave['algunas'] = fuzz.trimf(self.palabras_clave.universe, [0, 5, 10])
        self.palabras_clave['muchas'] = fuzz.trimf(self.palabras_clave.universe, [5, 10, 10])

        # Definir funciones de pertenencia para la certeza
        self.certeza['baja'] = fuzz.trimf(self.certeza.universe, [0, 0, 50])
        self.certeza['media'] = fuzz.trimf(self.certeza.universe, [0, 50, 100])
        self.certeza['alta'] = fuzz.trimf(self.certeza.universe, [50, 100, 100])

        # Reglas difusas
        rule1 = ctrl.Rule(self.longitud_pregunta['corta'] & self.palabras_clave['pocas'], self.certeza['baja'])
        rule2 = ctrl.Rule(self.longitud_pregunta['media'] & self.palabras_clave['algunas'], self.certeza['media'])
        rule3 = ctrl.Rule(self.longitud_pregunta['larga'] & self.palabras_clave['muchas'], self.certeza['alta'])
        rule4 = ctrl.Rule(self.longitud_pregunta['corta'] & self.palabras_clave['muchas'], self.certeza['media'])
        rule5 = ctrl.Rule(self.longitud_pregunta['larga'] & self.palabras_clave['pocas'], self.certeza['baja'])

        # Controlador difuso
        self.certeza_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5])
        self.certeza_simulador = ctrl.ControlSystemSimulation(self.certeza_ctrl)

    def evaluar_certeza(self, pregunta):
        # Calcular la longitud de la pregunta
        longitud = min(len(pregunta.split()), 100)

        # Contar palabras clave en la pregunta
        palabras_clave_relevantes = {'cómo', 'por qué', 'cuándo', 'dónde', 'qué'}
        palabras_pregunta = set(pregunta.lower().split())
        num_palabras_clave = len(palabras_pregunta.intersection(palabras_clave_relevantes))
        num_palabras_clave = min(num_palabras_clave, 10)  # Limitar a 10 para el universo

        # Configurar las entradas del sistema difuso
        self.certeza_simulador.input['longitud_pregunta'] = longitud
        self.certeza_simulador.input['palabras_clave'] = num_palabras_clave

        # Computar la certeza
        self.certeza_simulador.compute()
        certeza_resultado = self.certeza_simulador.output['certeza']

        # Interpretar el resultado en una categoría
        if certeza_resultado > 70:
            return "alta"
        elif certeza_resultado > 40:
            return "media"
        else:
            return "baja"
