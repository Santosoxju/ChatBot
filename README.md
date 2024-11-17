# chatbot-constructora

## ChatBot de Ayuda al Cliente

Este es un simple chatbot de ayuda al cliente desarrollado con Vue.js y Flask-SocketIO.

## Requisitos

- Python 3.x
- Node.js
- npm (Node Package Manager)

## Configuración

### Servidor (Flask)

1. Crea un entorno virtual:

    ```bash
    python -m venv venv
    ```

2. Activa el entorno virtual (en sistemas Windows):

    ```bash
    venv\Scripts\activate
    ```

   O, activa el entorno virtual en sistemas basados en Unix o macOS:

    ```bash
    source venv/bin/activate
    ```

3. Instala las dependencias del servidor:

    ```bash
    pip install -r requirements.txt
    ```

4. Ejecuta el servidor:

    ```bash
    python chat.py
    ```

### Cliente (Vue.js)

1. Instala las dependencias del cliente:

    ```bash
    npm install
    ```

    ```bash
    npm install sockect.io-client
    ```

2. Ejecuta la aplicación Vue.js:

    ```bash
    npm run serve
    ```

## Uso

1. Accede a la aplicación en tu navegador: `http://localhost:8080`.
2. ¡Disfruta del chatbot de ayuda al cliente!

## Personalización

- Puedes personalizar las respuestas del chatbot en el servidor (`server.py`) y las interacciones del cliente en el componente Vue (`Chat.vue`).

## Contribuir

Si encuentras errores o tienes mejoras, ¡siéntete libre de abrir un problema o enviar un pull request!

## Licencia

Este proyecto está bajo la Licencia MIT - consulta el archivo [LICENSE](LICENSE) para más detalles.
