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
    // Vercel WebSocket URL
    const socketUrl = process.env.NODE_ENV === 'production'
      ? 'wss://your-vercel-app-url.vercel.app'  // Production URL
      : 'http://127.0.0.1:3000';  // Local URL for development

    this.socket = io(socketUrl);

    this.messages.push({ text: "¡Bienvenido al Chatbot de Ayuda! ¿En qué puedo ayudarte hoy?", fromClient: false });

    this.socket.on('message', (text) => {
      setTimeout(() => {
        this.messages.push({ text, fromClient: false });
        this.loading = false;
        this.$nextTick(() => this.scrollChatToBottom());
      }, 1500);
    });

    this.socket.emit('saludo', 'Hola, soy un cliente de Vue.js');

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      this.recognition = new SpeechRecognition();
      this.recognition.lang = 'es-ES';
      this.recognition.continuous = false;
      this.recognition.interimResults = false;

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
    removeAccents(str) {
      return str.normalize("NFD").replace(/[\u0300-\u036f]/g, "");
    },
    startRecording() {
      if (this.recognition) {
        this.recognition.start();
      } else {
        alert('Reconocimiento de voz no soportado en este navegador.');
      }
    },
    sendMessage() {
      if (this.newMessage.trim() === '') return;
      this.loading = true;

      const messageText = this.removeAccents(this.newMessage);

      this.socket.emit('message', messageText);
      this.messages.push({ text: messageText, fromClient: true });
      this.newMessage = '';
      this.$nextTick(() => {
        this.scrollChatToBottom();
      });

      fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: messageText, user_id: this.socket.id }),
      })
      .then(response => response.json())
      .then(data => {
        this.messages.push({ text: data.response, fromClient: false });
        this.loading = false;
        this.newMessage = '';
        this.$nextTick(() => {
          this.scrollChatToBottom();
        });
      });
    },
    scrollChatToBottom() {
      if (this.$refs.chatMessages) {
        this.$refs.chatMessages.scrollTop = this.$refs.chatMessages.scrollHeight;
      }
    },
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
  border-bottom: 1px solid #e1e1e1;
}

.chat-container {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
  max-height: 400px;
}

.message {
  margin: 10px 0;
  padding: 10px;
  border-radius: 10px;
  max-width: 70%;
  background-color: #f1f1f1;
  word-wrap: break-word;
}

.client-message {
  background-color: #007bff;
  color: white;
  align-self: flex-end;
}

.bot-message {
  background-color: #e1e1e1;
}

.chat-input {
  display: flex;
  align-items: center;
  padding: 10px;
  background-color: #f9f9f9;
}

.chat-input input {
  flex: 1;
  padding: 10px;
  border-radius: 20px;
  border: 1px solid #ddd;
  margin-right: 10px;
}

.chat-input button {
  padding: 10px;
  border-radius: 50%;
  background-color: #007bff;
  color: white;
  border: none;
  cursor: pointer;
}

.chat-input button:disabled {
  background-color: #b0b0b0;
}

.loading {
  font-size: 0.9rem;
  color: #777;
}
</style>
