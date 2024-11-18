<template>
  <div class="chatbot-wrapper">
    <div class="chatbot-header">
      <h1 class="chatbot-title">Chat Bot Constructora</h1>
    </div>
    <div class="chatbot-body">
      <div class="chatbot-background">
        <img src="boot_fondo.png" alt="Fondo de la constructora y chatbot" class="background-image" />
      </div>
      <div class="chat-content">
        <div class="chat-toggle" @click="toggleChat">
          <button v-if="!isChatOpen">
            <span>🗨️ Abrir Chat</span>
          </button>
          <button v-else>
            <span>✖️ Cerrar Chat</span>
          </button>
        </div>

        <transition name="fade">
          <div v-if="isChatOpen" class="chat-container" ref="chatContainer">
            <div class="chat-messages" ref="chatMessages">
              <div v-for="(message, index) in messages" :key="index" class="message" :class="{ 'client-message': message.fromClient, 'bot-message': !message.fromClient }">
                <p>{{ message.text }}</p>
              </div>
              <div v-if="loading" class="loading">Escribiendo...</div>
            </div>

            <div class="chat-input">
              <input v-model="newMessage" @keyup.enter="sendMessage" placeholder="Escribe un mensaje o utiliza el micrófono" :disabled="loading" autofocus aria-label="Escribe tu mensaje aquí" />
              <button @click="startRecording" :disabled="loading">
                🎤
              </button>
              <button @click="sendMessage" :disabled="loading">Enviar</button>
            </div>
          </div>
        </transition>
      </div>
    </div>
  </div>
</template>

<script>
import io from 'socket.io-client';

export default {
  data() {
    return {
      messages: [],
      newMessage: '',
      socket: null,
      loading: false,
      isChatOpen: false,
      recognition: null,
    };
  },
  mounted() {
    // Conectar al servidor de WebSocket
    this.socket = io('https://chatbot-xd4b.onrender.com');
    //this.socket = io('http://127.0.0.1:3000'); local
    this.messages.push({ text: "¡Bienvenido al Chatbot de Ayuda! ¿En qué puedo ayudarte hoy?", fromClient: false });

    this.socket.on('message', (text) => {
      setTimeout(() => {
        this.messages.push({ text, fromClient: false });
        this.loading = false;
        this.$nextTick(() => this.scrollChatToBottom());
      }, 1500);
    });

    // Emitir saludo inicial
    this.socket.emit('saludo', 'Hola, soy un cliente de Vue.js');

    // Configuración del reconocimiento de voz
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      this.recognition = new SpeechRecognition();
      this.recognition.lang = 'es-ES';
      this.recognition.continuous = false;
      this.recognition.interimResults = false;

      // Asignar el resultado del reconocimiento a newMessage sin enviarlo automáticamente
      this.recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        this.newMessage = this.removeAccents(transcript);
      };

      this.recognition.onerror = (event) => {
        console.error('Error de reconocimiento:', event.error);
      };
    } else {
      alert('Reconocimiento de voz no soportado en este navegador.');
    }
  },
  methods: {
    // Función para quitar acentos del texto
    removeAccents(str) {
      return str.normalize("NFD").replace(/[\u0300-\u036f]/g, "");
    },
    // Método para iniciar la grabación de voz
    startRecording() {
      if (this.recognition) {
        this.recognition.start();
      } else {
        alert('Reconocimiento de voz no soportado en este navegador.');
      }
    },
    // Método para enviar el mensaje
    sendMessage() {
      if (this.newMessage.trim() === '') return;
      this.loading = true;
      // Elimina acentos antes de enviar el mensaje
      const messageText = this.removeAccents(this.newMessage);
      this.socket.emit('message', messageText);
      this.messages.push({ text: messageText, fromClient: true });
      this.newMessage = '';
      this.$nextTick(() => {
        this.scrollChatToBottom();
      });
    },
    // Método para hacer scroll hacia abajo
    scrollChatToBottom() {
      if (this.$refs.chatMessages) {
        this.$refs.chatMessages.scrollTop = this.$refs.chatMessages.scrollHeight;
      }
    },
    // Método para alternar la apertura del chat
    toggleChat() {
      this.isChatOpen = !this.isChatOpen;
    },
  },
};
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');

body {
  font-family: 'Roboto', sans-serif;
  background: #f7f9fc;
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
}

.chatbot-wrapper {
  width: 80%;
  max-width: 80%;
  background-color: #ffffff;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  margin-left: 115px;
}

.chatbot-header {
  background-color: #007bff;
  color: white;
  padding: 20px;
  text-align: center;
}

.chatbot-title {
  margin: 0;
  font-size: 1.8rem;
}

.chatbot-body {
  display: flex;
  flex: 1;
}

.chatbot-background {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #ebf2fa;
}

.background-image {
  max-width: 100%;
  height: auto;
}

.chat-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.chat-toggle {
  text-align: center;
  padding: 10px;
  background-color: #f8f8f8;
  border-bottom: 2px solid #e0e0e0;
}

.chat-container {
  display: flex;
  flex-direction: column;
  height: 500px;
}

.chat-messages {
  flex: 1;
  padding: 15px;
  overflow-y: auto;
  background-color: #fafafa;
  border-bottom: 2px solid #e0e0e0;
}

.message {
  margin-bottom: 10px;
  border-radius: 20px;
  padding: 10px 15px;
  max-width: 75%;
  word-wrap: break-word;
}

.client-message {
  background-color: #007bff;
  color: white;
  align-self: flex-end;
}

.bot-message {
  background-color: #e0e0e0;
  color: #333;
  align-self: flex-start;
}

.chat-input {
  padding: 10px;
  background-color: #ffffff;
  border-top: 2px solid #e0e0e0;
  display: flex;
}

input {
  flex: 1;
  padding: 10px;
  border: 2px solid #ccc;
  border-radius: 20px;
  outline: none;
  transition: border 0.3s;
  margin-right: 10px;
}

input:focus {
  border-color: #007bff;
}

button {
  padding: 10px 20px;
  border: none;
  border-radius: 20px;
  background-color: #007bff;
  color: white;
  cursor: pointer;
  transition: background-color 0.3s;
  margin-left: 5px;
}

button:hover {
  background-color: #0056b3;
}

.loading {
  font-size: 1rem;
  color: #007bff;
  text-align: center;
  padding: 10px;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.5s;
}

.fade-enter, .fade-leave-to {
  opacity: 0;
}
</style>
