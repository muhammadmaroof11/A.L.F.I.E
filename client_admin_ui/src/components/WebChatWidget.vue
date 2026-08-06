<template>
  <div class="webchat-widget-container">
    <!-- Floating Toggle Button -->
    <button class="chat-toggle-btn" @click="isOpen = !isOpen">
      <span v-if="!isOpen">💬 Chat with Us</span>
      <span v-else>✕ Close</span>
    </button>

    <!-- Chat Box Drawer -->
    <div v-if="isOpen" class="chat-box">
      <!-- Header -->
      <div class="chat-header">
        <div class="header-info">
          <div class="avatar-dot"></div>
          <div>
            <div class="tenant-name">{{ tenantName || 'AI Sales Assistant' }}</div>
            <div class="status-sub">Online · Instant Answers</div>
          </div>
        </div>
        <button class="close-btn" @click="isOpen = false">✕</button>
      </div>

      <!-- Messages Area -->
      <div class="chat-messages" ref="messagesContainer">
        <div v-for="(msg, idx) in messages" :key="idx" :class="['msg-row', msg.role]">
          <div class="msg-bubble">
            {{ msg.content }}
          </div>
        </div>

        <div v-if="isTyping" class="msg-row assistant">
          <div class="msg-bubble typing">
            <span class="dot"></span><span class="dot"></span><span class="dot"></span>
          </div>
        </div>

        <!-- Phone Escalation Modal inside Chat -->
        <div v-if="showEscalationPrompt" class="escalation-banner">
          <div class="banner-title">📞 Connect Over Phone Call</div>
          <div class="banner-desc">Enter your phone number so our voice assistant can greet you with full context of this chat:</div>
          
          <div v-if="!escalatedResult" style="margin-top:8px;">
            <input v-model="userPhone" type="tel" class="phone-input" placeholder="+1 555 123 4567" />
            <button class="call-btn" @click="escalateToCall" :disabled="!userPhone.trim()">
              Confirm Phone Handoff →
            </button>
          </div>

          <div v-else class="escalated-success">
            <div style="font-weight:700; color:#10B981; margin-bottom:4px;">✅ Handoff Registered!</div>
            <div>{{ escalatedResult.instructions }}</div>
          </div>
        </div>
      </div>

      <!-- Input Bar -->
      <div class="chat-input-bar">
        <input 
          v-model="inputMessage" 
          type="text" 
          placeholder="Type your message..." 
          @keyup.enter="sendMessage" 
          :disabled="isTyping" 
        />
        <button @click="sendMessage" :disabled="!inputMessage.trim() || isTyping">
          Send
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue';
import axios from 'axios';

const props = defineProps({
  tenantId: { type: String, default: 'alfie_realty_pk' }
});

const isOpen = ref(false);
const sessionId = ref('');
const tenantName = ref('');
const inputMessage = ref('');
const messages = ref([]);
const isTyping = ref(false);
const showEscalationPrompt = ref(false);
const userPhone = ref('');
const escalatedResult = ref(null);
const messagesContainer = ref(null);

const scrollToBottom = async () => {
  await nextTick();
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
  }
};

const initChat = async () => {
  try {
    const res = await axios.post('/api/public/chat/init', {
      tenant_id: props.tenantId,
      user_name: 'Website Visitor'
    });
    sessionId.value = res.data.session_id;
    tenantName.value = res.data.tenant_name;
    messages.value.push({ role: 'assistant', content: res.data.greeting });
    scrollToBottom();
  } catch (err) {
    console.warn('Could not init chat session:', err);
    messages.value.push({ role: 'assistant', content: 'Hello! How can I help you today?' });
  }
};

const sendMessage = async () => {
  if (!inputMessage.value.trim() || isTyping.value) return;
  const userText = inputMessage.value.trim();
  messages.value.push({ role: 'user', content: userText });
  inputMessage.value = '';
  scrollToBottom();
  
  isTyping.value = true;
  try {
    const res = await axios.post('/api/public/chat/message', {
      session_id: sessionId.value,
      message: userText
    });
    messages.value.push({ role: 'assistant', content: res.data.reply });
    
    if (res.data.escalation_offered) {
      showEscalationPrompt.value = true;
    }
  } catch (err) {
    messages.value.push({ role: 'assistant', content: 'Apologies, I encountered an issue. Would you like to speak over a phone call?' });
    showEscalationPrompt.value = true;
  } finally {
    isTyping.value = false;
    scrollToBottom();
  }
};

const escalateToCall = async () => {
  if (!userPhone.value.trim()) return;
  try {
    const res = await axios.post('/api/public/chat/escalate', {
      session_id: sessionId.value,
      user_phone: userPhone.value.trim()
    });
    escalatedResult.value = res.data;
  } catch (err) {
    alert('Could not process phone handoff.');
  }
};

onMounted(() => {
  initChat();
});
</script>

<style scoped>
.webchat-widget-container {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 9999;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.chat-toggle-btn {
  background: linear-gradient(135deg, #3B82F6, #8B5CF6);
  color: #ffffff;
  border: none;
  padding: 12px 20px;
  border-radius: 30px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  box-shadow: 0 8px 24px rgba(59, 130, 246, 0.35);
  transition: transform 0.2s, box-shadow 0.2s;
}
.chat-toggle-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 28px rgba(59, 130, 246, 0.45);
}

.chat-box {
  width: 360px;
  height: 500px;
  background: #0F172A;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5);
  overflow: hidden;
  margin-bottom: 12px;
}

.chat-header {
  background: #1E293B;
  padding: 14px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}
.header-info {
  display: flex;
  align-items: center;
  gap: 10px;
}
.avatar-dot {
  width: 10px;
  height: 10px;
  background: #10B981;
  border-radius: 50%;
}
.tenant-name {
  color: #F8FAFC;
  font-weight: 600;
  font-size: 14px;
}
.status-sub {
  color: #94A3B8;
  font-size: 11px;
}
.close-btn {
  background: transparent;
  border: none;
  color: #94A3B8;
  font-size: 16px;
  cursor: pointer;
}

.chat-messages {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.msg-row {
  display: flex;
}
.msg-row.user {
  justify-content: flex-end;
}
.msg-row.assistant {
  justify-content: flex-start;
}
.msg-bubble {
  max-width: 80%;
  padding: 10px 14px;
  border-radius: 12px;
  font-size: 13px;
  line-height: 1.4;
}
.msg-row.user .msg-bubble {
  background: #3B82F6;
  color: #ffffff;
  border-bottom-right-radius: 2px;
}
.msg-row.assistant .msg-bubble {
  background: #1E293B;
  color: #F1F5F9;
  border-bottom-left-radius: 2px;
}

.msg-bubble.typing {
  display: flex;
  gap: 4px;
  align-items: center;
  padding: 10px 16px;
}
.dot {
  width: 6px;
  height: 6px;
  background: #94A3B8;
  border-radius: 50%;
  animation: pulse 1.4s infinite;
}
.dot:nth-child(2) { animation-delay: 0.2s; }
.dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes pulse {
  0%, 100% { opacity: 0.3; transform: scale(0.8); }
  50% { opacity: 1; transform: scale(1.2); }
}

.escalation-banner {
  background: rgba(59, 130, 246, 0.12);
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: 10px;
  padding: 12px;
  margin-top: 10px;
  font-size: 12px;
  color: #E2E8F0;
}
.banner-title {
  font-weight: 700;
  color: #60A5FA;
  margin-bottom: 4px;
}
.phone-input {
  width: 100%;
  padding: 8px 10px;
  background: #0F172A;
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 6px;
  color: #F8FAFC;
  font-size: 12px;
  margin-bottom: 6px;
  box-sizing: border-box;
}
.call-btn {
  width: 100%;
  padding: 8px;
  background: #10B981;
  color: #ffffff;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  font-size: 12px;
  cursor: pointer;
}

.chat-input-bar {
  padding: 12px;
  background: #1E293B;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  gap: 8px;
}
.chat-input-bar input {
  flex: 1;
  background: #0F172A;
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 8px;
  padding: 8px 12px;
  color: #F8FAFC;
  font-size: 13px;
}
.chat-input-bar button {
  background: #3B82F6;
  color: #ffffff;
  border: none;
  border-radius: 8px;
  padding: 8px 14px;
  font-weight: 600;
  font-size: 13px;
  cursor: pointer;
}
.chat-input-bar button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
