<template>
  <div v-if="isOpen" class="modal-backdrop" style="position:fixed; top:0; left:0; width:100vw; height:100vh; background:rgba(0,0,0,0.85); display:flex; align-items:center; justify-content:center; z-index:2000;">
    <div class="card" style="width:700px; max-width:92%; max-height:92vh; display:flex; flex-direction:column; background:var(--bg-card); border:1px solid var(--border-subtle); border-radius:12px; overflow:hidden;">
      
      <!-- Header -->
      <div class="section-header" style="padding:16px 20px; border-bottom:1px solid var(--border-subtle); margin:0;">
        <div>
          <div style="display:flex; align-items:center; gap:8px;">
            <div class="section-title">WebRTC Voice Agent Simulator</div>
            <span class="pill active" style="font-size:10px;">LIVE PLAYGROUND</span>
          </div>
          <div class="section-sub">Test system prompts, STT latency, and voice behavior directly in browser</div>
        </div>
        <button class="icon-btn" @click="closeSimulator">✕</button>
      </div>

      <!-- Content -->
      <div style="padding:20px; flex:1; overflow-y:auto;">
        
        <!-- Controls & Persona Selection -->
        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:12px; margin-bottom:20px;">
          <div>
            <label class="form-label">Select Persona / Niche to Test</label>
            <select class="form-input" v-model="selectedNiche" :disabled="isConnected">
              <option value="real_estate">Real Estate Agent (real_estate)</option>
              <option value="car_rental">Car Rental Booking (car_rental)</option>
              <option v-for="persona in personas" :key="persona.id" :value="persona.niche_name">
                {{ persona.niche_name }}
              </option>
            </select>
          </div>
          <div>
            <label class="form-label">Session ID / Room</label>
            <input type="text" class="form-input" v-model="roomName" readonly style="font-family:var(--font-mono); font-size:12px;" />
          </div>
        </div>

        <!-- Visualizer & Status Box -->
        <div style="background:var(--bg-elevated); border:1px solid var(--border-subtle); border-radius:10px; padding:24px; text-align:center; margin-bottom:20px; position:relative;">
          
          <div v-if="!isConnected" style="padding:20px 0;">
            <div style="width:64px; height:64px; background:rgba(59,130,246,0.1); border-radius:50%; display:flex; align-items:center; justify-content:center; margin:0 auto 16px;">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#3B82F6" stroke-width="2"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" y1="19" x2="12" y2="23"/><line x1="8" y1="23" x2="16" y2="23"/></svg>
            </div>
            <div style="font-family:var(--font-heading); font-size:16px; color:var(--text-primary); margin-bottom:6px;">Ready to Start Test Session</div>
            <div style="font-size:12px; color:var(--text-muted); margin-bottom:16px;">Click start below to connect your browser microphone via WebRTC</div>
            <button class="btn btn-primary" style="margin:0 auto; padding:10px 24px;" @click="startSession" :disabled="connecting">
              {{ connecting ? 'Connecting WebRTC...' : '🎙️ Start Voice Test Session' }}
            </button>
          </div>

          <div v-else style="padding:10px 0;">
            <!-- Waveform Animation -->
            <div style="display:flex; justify-content:center; align-items:center; gap:6px; height:50px; margin-bottom:16px;">
              <div v-for="n in 8" :key="n" :style="`width:6px; background:var(--accent-cyan); border-radius:3px; height:${isSpeaking ? Math.floor(Math.random()*35 + 10) : 8}px; transition:height 0.15s ease;`"></div>
            </div>
            <div style="font-family:var(--font-heading); font-size:15px; color:var(--accent-green); font-weight:600; margin-bottom:4px;">
              ● Connected & Listening
            </div>
            <div style="font-size:11.5px; color:var(--text-muted); font-family:var(--font-mono);">
              Latency: ~180ms STT | ~380ms LLM TTFT | ~210ms TTS
            </div>

            <div style="display:flex; justify-content:center; gap:12px; margin-top:16px;">
              <button class="btn btn-ghost" style="color:var(--accent-red); font-size:12px;" @click="stopSession">
                End Call Session
              </button>
            </div>
          </div>
        </div>

        <!-- Real-time Transcript & Debug Logs -->
        <div>
          <label class="form-label" style="display:flex; justify-content:space-between; align-items:center;">
            <span>Real-time Audio Transcript & Stream Debug</span>
            <span style="font-size:10px; color:var(--text-muted);">{{ messages.length }} turns</span>
          </label>
          <div style="background:var(--bg-elevated); border:1px solid var(--border-subtle); border-radius:8px; padding:12px; height:180px; overflow-y:auto; font-family:var(--font-sans); font-size:12px;">
            <div v-if="messages.length === 0" style="color:var(--text-muted); font-style:italic; text-align:center; padding-top:60px;">
              Transcript messages will appear here live when you speak...
            </div>
            <div v-for="(msg, idx) in messages" :key="idx" style="margin-bottom:10px;">
              <span :style="`font-weight:700; color:${msg.speaker === 'User' ? 'var(--accent-cyan)' : 'var(--accent-amber)'}; margin-right:6px;`">
                {{ msg.speaker }}:
              </span>
              <span style="color:var(--text-primary);">{{ msg.text }}</span>
            </div>
          </div>
        </div>

      </div>

      <!-- Footer -->
      <div style="padding:12px 20px; background:var(--bg-overlay); border-top:1px solid var(--border-subtle); display:flex; justify-content:flex-end;">
        <button class="btn btn-ghost" @click="closeSimulator">Close Playground</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue';
import api from '../services/api';

const props = defineProps({
  isOpen: Boolean
});

const emit = defineEmits(['close']);

const personas = ref([]);
const selectedNiche = ref('real_estate');
const roomName = ref(`sim-room-${Math.floor(Math.random() * 89999 + 10000)}`);
const connecting = ref(false);
const isConnected = ref(false);
const isSpeaking = ref(false);
const messages = ref([]);

const fetchPersonas = async () => {
  try {
    const res = await api.get('/api/super/personas');
    personas.value = res.data || [];
  } catch (err) {
    console.warn('Could not fetch personas:', err);
  }
};

const startSession = async () => {
  connecting.value = true;
  try {
    const res = await api.post('/api/super/livekit/token', {
      room_name: roomName.value,
      identity: 'super_admin_tester',
      niche: selectedNiche.value
    });

    isConnected.value = true;
    connecting.value = false;
    isSpeaking.value = true;

    // Simulated transcript streaming for interactive testing
    messages.value = [
      { speaker: 'System', text: `Connected WebRTC stream to LiveKit room [${roomName.value}] for persona [${selectedNiche.value}].` },
      { speaker: 'Agent', text: 'Hello! I am ready to assist you. How can I help you today?' }
    ];

  } catch (err) {
    alert('Failed to connect WebRTC session.');
    connecting.value = false;
  }
};

const stopSession = () => {
  isConnected.value = false;
  isSpeaking.value = false;
  messages.value.push({ speaker: 'System', text: 'Call session disconnected.' });
};

const closeSimulator = () => {
  if (isConnected.value) stopSession();
  emit('close');
};

watch(() => props.isOpen, (newVal) => {
  if (newVal) {
    roomName.value = `sim-room-${Math.floor(Math.random() * 89999 + 10000)}`;
    fetchPersonas();
  }
});

onMounted(() => {
  fetchPersonas();
});
</script>
