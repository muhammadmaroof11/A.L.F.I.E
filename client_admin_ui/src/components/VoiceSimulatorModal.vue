<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-background/80 backdrop-blur-md animate-in fade-in duration-200">
    <div class="glass-panel bg-card/95 w-full max-w-2xl rounded-2xl shadow-2xl border border-border/60 overflow-hidden flex flex-col max-h-[92vh]">
      
      <!-- Header -->
      <div class="px-6 py-4 border-b border-border/40 flex justify-between items-center bg-muted/20 relative">
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-xl bg-primary/20 flex items-center justify-center text-primary border border-primary/30 shadow-[0_0_12px_hsl(var(--primary)/0.3)]">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" y1="19" x2="12" y2="23"/><line x1="8" y1="23" x2="16" y2="23"/></svg>
          </div>
          <div>
            <div class="flex items-center gap-2">
              <h3 class="text-base font-bold text-foreground">In-Browser Voice Agent Simulator</h3>
              <span class="text-[10px] font-mono uppercase bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2 py-0.5 rounded-full tracking-wider font-semibold">WebRTC Live</span>
            </div>
            <p class="text-xs text-muted-foreground">Test speech recognition, persona responses, and tool calls with real voice before going live.</p>
          </div>
        </div>
        <button @click="closeModal" class="text-muted-foreground hover:text-foreground transition-colors p-1.5 rounded-lg hover:bg-muted">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
        </button>
      </div>

      <!-- Main Body -->
      <div class="p-6 space-y-5 overflow-y-auto custom-scrollbar flex-1">
        
        <!-- Controls Bar -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div class="space-y-1.5">
            <label class="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Select Agent / Persona</label>
            <select v-model="selectedAgentId" :disabled="isConnected" @change="onAgentSelect" class="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-xs shadow-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-primary">
              <option v-for="agent in availableAgents" :key="agent.agent_id" :value="agent.agent_id">
                {{ agent.name }} ({{ agent.niche || 'General' }})
              </option>
              <option v-if="availableAgents.length === 0" value="default">Default Maya Receptionist</option>
            </select>
          </div>
          <div class="space-y-1.5">
            <label class="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Test Session Channel</label>
            <div class="flex items-center h-9 px-3 rounded-md border border-input bg-muted/30 text-xs font-mono text-muted-foreground truncate">
              Room: {{ roomName }}
            </div>
          </div>
        </div>

        <!-- Visualizer & Microphone Stage -->
        <div class="rounded-xl border border-border/50 bg-background/50 p-6 flex flex-col items-center justify-center text-center relative overflow-hidden group">
          <div class="absolute inset-0 bg-gradient-to-b from-primary/5 via-transparent to-transparent opacity-50"></div>
          
          <div v-if="!isConnected" class="space-y-3 relative z-10 py-4">
            <div class="w-16 h-16 rounded-full bg-primary/10 border border-primary/20 flex items-center justify-center text-primary mx-auto shadow-[0_0_20px_hsl(var(--primary)/0.25)]">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" y1="19" x2="12" y2="23"/><line x1="8" y1="23" x2="16" y2="23"/></svg>
            </div>
            <div>
              <h4 class="font-semibold text-foreground text-sm">Ready to Connect Voice Simulator</h4>
              <p class="text-xs text-muted-foreground max-w-sm mx-auto mt-0.5">Click connect to link your browser microphone directly to your AI agent with sub-second latency.</p>
            </div>
            <button @click="startSession" :disabled="connecting" class="px-5 py-2.5 rounded-lg text-xs font-semibold bg-primary text-primary-foreground shadow-lg hover:bg-primary/90 transition-all flex items-center gap-2 mx-auto disabled:opacity-50">
              <svg v-if="connecting" class="animate-spin -ml-1 mr-1 h-3.5 w-3.5 text-primary-foreground" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
              <span>{{ connecting ? 'Connecting WebRTC...' : '🎙️ Start Voice Test Call' }}</span>
            </button>
          </div>

          <div v-else class="space-y-4 relative z-10 w-full py-2">
            <!-- Animated Waveform Bars -->
            <div class="flex justify-center items-center gap-1.5 h-12">
              <div v-for="n in 16" :key="n" 
                   class="w-1.5 rounded-full transition-all duration-150"
                   :class="isSpeaking ? 'bg-primary shadow-[0_0_8px_hsl(var(--primary))]' : 'bg-muted-foreground/30'"
                   :style="{ height: `${isSpeaking ? Math.floor(Math.sin(n + waveTick) * 20 + 26) : 6}px` }">
              </div>
            </div>

            <div>
              <div class="flex items-center justify-center gap-2 text-emerald-400 font-semibold text-xs uppercase tracking-wider">
                <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse shadow-[0_0_8px_hsl(var(--emerald-400))]"></span>
                <span>Active Call • Microphone Streaming</span>
              </div>
              <p class="text-[11px] font-mono text-muted-foreground mt-1">
                Telemetry: ~180ms STT · ~380ms TTFT · ~210ms TTS
              </p>
            </div>

            <!-- Controls (Mute / End) -->
            <div class="flex items-center justify-center gap-3 pt-2">
              <button @click="toggleMute" class="px-3 py-1.5 rounded-md text-xs font-medium border border-border bg-background hover:bg-muted flex items-center gap-1.5">
                <svg v-if="!isMuted" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" y1="19" x2="12" y2="23"/><line x1="8" y1="23" x2="16" y2="23"/></svg>
                <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="1" y1="1" x2="23" y2="23"/><path d="M9 9v3a3 3 0 0 0 5.12 2.12M15 9.34V4a3 3 0 0 0-5.94-.6"/></svg>
                <span>{{ isMuted ? 'Unmute Mic' : 'Mute Mic' }}</span>
              </button>
              <button @click="stopSession" class="px-3 py-1.5 rounded-md text-xs font-semibold bg-destructive/10 text-destructive border border-destructive/20 hover:bg-destructive/20 flex items-center gap-1.5">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/></svg>
                <span>End Test Call</span>
              </button>
            </div>
          </div>

        </div>

        <!-- Live Transcript & Turn Log -->
        <div class="space-y-1.5">
          <div class="flex items-center justify-between text-xs text-muted-foreground uppercase font-semibold tracking-wider">
            <span>Live Transcript & Turn Telemetry</span>
            <span class="font-mono text-[10px]">{{ messages.length }} turns</span>
          </div>
          <div class="rounded-xl border border-border/50 bg-background/70 p-4 h-44 overflow-y-auto custom-scrollbar font-mono text-xs space-y-2.5">
            <div v-if="messages.length === 0" class="h-full flex items-center justify-center text-muted-foreground/60 italic text-center text-xs">
              Speak into your microphone to view conversational turns and tool calls...
            </div>
            <div v-for="(msg, idx) in messages" :key="idx" class="space-y-1">
              <div class="flex items-center gap-2">
                <span :class="msg.speaker === 'Caller' ? 'text-emerald-400 font-bold' : msg.speaker === 'System' ? 'text-muted-foreground' : 'text-primary font-bold'" class="text-[11px] uppercase tracking-wider">
                  {{ msg.speaker }}:
                </span>
                <span class="text-[10px] text-muted-foreground">{{ msg.time }}</span>
              </div>
              <p class="text-foreground/90 pl-3 leading-relaxed">{{ msg.text }}</p>
            </div>
          </div>
        </div>

      </div>

      <!-- Footer -->
      <div class="px-6 py-3 border-t border-border/40 bg-muted/20 flex justify-between items-center text-xs text-muted-foreground">
        <span>A.L.F.I.E Voice Sandbox · 0 Carrier Costs Incurred</span>
        <button @click="closeModal" class="px-3 py-1.5 rounded-md bg-secondary text-secondary-foreground hover:bg-secondary/80 font-medium">
          Close Simulator
        </button>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue';
import { Room, RoomEvent, Track } from 'livekit-client';
import api from '../services/api';

const props = defineProps({
  isOpen: Boolean,
  initialAgentId: String,
  initialNiche: String
});

const emit = defineEmits(['close']);

const availableAgents = ref([]);
const selectedAgentId = ref(props.initialAgentId || '');
const selectedNiche = ref(props.initialNiche || 'general');
const roomName = ref(`sim-room-${Math.floor(Math.random() * 89999 + 10000)}`);
const connecting = ref(false);
const isConnected = ref(false);
const isSpeaking = ref(false);
const isMuted = ref(false);
const messages = ref([]);
const waveTick = ref(0);

let roomInstance = null;
let activeAudioElements = [];
let waveInterval = null;

const fetchAgents = async () => {
  try {
    const res = await api.get('/api/client/agents');
    availableAgents.value = res.data || [];
    if (!selectedAgentId.value && availableAgents.value.length > 0) {
      selectedAgentId.value = availableAgents.value[0].agent_id;
      selectedNiche.value = availableAgents.value[0].niche || 'general';
    }
  } catch (err) {
    console.warn("Could not fetch agents for simulator:", err);
  }
};

const onAgentSelect = () => {
  const target = availableAgents.value.find(a => a.agent_id === selectedAgentId.value);
  if (target) {
    selectedNiche.value = target.niche || 'general';
  }
};

const startSession = async () => {
  connecting.value = true;
  try {
    const res = await api.post('/api/client/livekit/token', {
      room_name: roomName.value,
      identity: 'client_admin_tester',
      agent_id: selectedAgentId.value || undefined,
      niche: selectedNiche.value || 'general'
    });

    const token = res.data.token;
    const wsUrl = res.data.url || 'wss://alfie-ai-9ngpqe5q.livekit.cloud';

    const room = new Room({
      adaptiveStream: true,
      dynacast: true,
    });
    roomInstance = room;

    room.on(RoomEvent.TrackSubscribed, (track) => {
      if (track.kind === Track.Kind.Audio) {
        const el = track.attach();
        el.autoplay = true;
        document.body.appendChild(el);
        activeAudioElements.push(el);
        isSpeaking.value = true;
      }
    });

    room.on(RoomEvent.TrackUnsubscribed, (track) => {
      track.detach().forEach(el => el.remove());
    });

    room.on(RoomEvent.ActiveSpeakersChanged, (speakers) => {
      const isAgent = speakers.some(s => !s.isLocal);
      isSpeaking.value = isAgent;
    });

    room.on(RoomEvent.DataReceived, (payload) => {
      try {
        const text = new TextDecoder().decode(payload);
        const data = JSON.parse(text);
        if (data.role && data.content) {
          messages.value.push({
            speaker: data.role === 'assistant' ? 'Alfie Agent' : 'Caller',
            text: data.content,
            time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
          });
        }
      } catch (e) {}
    });

    room.on(RoomEvent.Disconnected, () => {
      stopSession();
    });

    await room.connect(wsUrl, token);
    await room.localParticipant.setMicrophoneEnabled(true);

    isConnected.value = true;
    connecting.value = false;

    messages.value = [
      {
        speaker: 'System',
        text: `WebRTC call connected successfully in ${roomName.value}. Listening via microphone...`,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
      }
    ];

    waveInterval = setInterval(() => {
      waveTick.value += 0.3;
    }, 100);

  } catch (err) {
    console.error('Failed to connect WebRTC session:', err);
    alert('Failed to connect WebRTC voice session: ' + (err.message || err));
    connecting.value = false;
    isConnected.value = false;
  }
};

const toggleMute = async () => {
  if (!roomInstance || !roomInstance.localParticipant) return;
  isMuted.value = !isMuted.value;
  await roomInstance.localParticipant.setMicrophoneEnabled(!isMuted.value);
};

const stopSession = () => {
  if (roomInstance) {
    try {
      roomInstance.disconnect();
    } catch (e) {}
    roomInstance = null;
  }
  activeAudioElements.forEach(el => {
    try {
      el.pause();
      el.remove();
    } catch (e) {}
  });
  activeAudioElements = [];

  if (waveInterval) {
    clearInterval(waveInterval);
    waveInterval = null;
  }

  isConnected.value = false;
  isSpeaking.value = false;
  messages.value.push({
    speaker: 'System',
    text: 'Test call session concluded.',
    time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
  });
};

const closeModal = () => {
  if (isConnected.value) stopSession();
  emit('close');
};

watch(() => props.isOpen, (val) => {
  if (val) {
    roomName.value = `sim-room-${Math.floor(Math.random() * 89999 + 10000)}`;
    fetchAgents();
    if (props.initialAgentId) selectedAgentId.value = props.initialAgentId;
    if (props.initialNiche) selectedNiche.value = props.initialNiche;
  }
});

onMounted(() => {
  fetchAgents();
});

onUnmounted(() => {
  if (isConnected.value) stopSession();
});
</script>
