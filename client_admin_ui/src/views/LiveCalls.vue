<template>
  <div class="space-y-6">
    <!-- Header Strip -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
      <div>
        <div class="flex items-center gap-3">
          <h2 class="text-2xl font-bold tracking-tight text-foreground">Live Calling Console</h2>
          <BadgePill :variant="liveCallsStore.wsConnected ? 'emerald' : 'amber'" :pulse="true">
            {{ liveCallsStore.wsConnected ? 'Live Gateway Connected' : 'Reconnecting...' }}
          </BadgePill>
        </div>
        <p class="text-xs text-muted-foreground mt-1">
          Sub-second inbound call monitoring, real-time voice transcripts, and supervisor controls.
        </p>
      </div>

      <!-- Quick Metrics Strip -->
      <div class="flex items-center gap-3">
        <div class="glass-panel px-3.5 py-1.5 rounded-lg border border-border/50 text-right">
          <span class="text-[10px] uppercase font-mono text-muted-foreground block">Active Channels</span>
          <span class="text-base font-bold font-mono text-primary">{{ liveCallsStore.activeCallCount }}</span>
        </div>
        <button
          @click="liveCallsStore.simulateDemoCall"
          :disabled="liveCallsStore.isSimulating"
          class="px-3.5 py-2 rounded-lg bg-primary/15 hover:bg-primary/25 border border-primary/30 text-primary text-xs font-semibold flex items-center gap-2 transition-all cursor-pointer shadow-sm"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path>
          </svg>
          {{ liveCallsStore.isSimulating ? 'Simulating...' : 'Simulate Inbound Call' }}
        </button>
      </div>
    </div>

    <!-- Main Workspace Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 min-h-[560px]">
      <!-- Left Column: Active Call Channels (5 Cols) -->
      <div class="lg:col-span-5 flex flex-col gap-3">
        <div class="flex items-center justify-between px-1">
          <span class="text-xs uppercase font-mono font-semibold text-muted-foreground tracking-wider">
            Active Call Channels ({{ liveCallsStore.activeCallCount }})
          </span>
          <span v-if="liveCallsStore.activeCallCount > 0" class="text-[11px] font-mono text-emerald-400 flex items-center gap-1">
            <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
            Real-Time Stream
          </span>
        </div>

        <!-- Empty State with Radar Sweep -->
        <div
          v-if="liveCallsStore.activeCallCount === 0"
          class="glass-panel p-8 rounded-xl border border-border/50 text-center flex flex-col items-center justify-center flex-1 min-h-[380px]"
        >
          <div class="relative w-20 h-20 mb-4 flex items-center justify-center">
            <div class="absolute inset-0 rounded-full border border-primary/20 animate-ping opacity-40"></div>
            <div class="absolute inset-2 rounded-full border border-primary/40"></div>
            <div class="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center text-primary">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 2a10 10 0 1 0 10 10A10 10 0 0 0 12 2zm0 18a8 8 0 1 1 8-8 8 8 0 0 1-8 8z"></path>
                <path d="M12 6v6l4 2"></path>
              </svg>
            </div>
          </div>
          <h3 class="text-sm font-semibold text-foreground">Listening for Inbound Calls</h3>
          <p class="text-xs text-muted-foreground max-w-xs mt-1">
            Incoming PSTN and WebRTC calls for this tenant will automatically attach here with zero latency.
          </p>
          <button
            @click="liveCallsStore.simulateDemoCall"
            class="mt-4 px-3 py-1.5 rounded-md bg-muted hover:bg-muted/80 text-foreground text-xs font-mono font-medium border border-border transition-colors cursor-pointer"
          >
            Launch Live Test Demo
          </button>
        </div>

        <!-- Active Cards List -->
        <div v-else class="flex flex-col gap-2.5 overflow-y-auto max-h-[640px] pr-1 custom-scrollbar">
          <div
            v-for="call in liveCallsStore.activeCalls"
            :key="call.call_id"
            @click="liveCallsStore.selectedCallId = call.call_id"
            class="glass-panel p-4 rounded-xl border transition-all duration-200 cursor-pointer relative overflow-hidden"
            :class="liveCallsStore.selectedCallId === call.call_id
              ? 'border-primary/80 bg-primary/5 shadow-[0_0_15px_hsl(var(--primary)/0.15)] ring-1 ring-primary/40'
              : 'border-border/60 hover:border-border hover:bg-muted/30'"
          >
            <div class="flex items-center justify-between mb-2.5">
              <div class="flex items-center gap-2">
                <BadgePill :variant="call.state === 'supervisor_takeover' ? 'rose' : (call.speaker_state === 'caller_speaking' ? 'sky' : 'emerald')" :pulse="true">
                  {{ call.state === 'supervisor_takeover' ? 'HUMAN LIVE' : (call.speaker_state === 'caller_speaking' ? 'CALLER SPEAKING' : 'AGENT ACTIVE') }}
                </BadgePill>
              </div>
              <span class="text-xs font-mono text-muted-foreground font-semibold">
                {{ formatElapsed(call.started_at) }}
              </span>
            </div>

            <div class="flex items-center justify-between">
              <div>
                <h4 class="text-sm font-bold text-foreground font-mono">{{ call.caller_phone || 'Caller' }}</h4>
                <p class="text-[11px] text-muted-foreground mt-0.5 flex items-center gap-1.5">
                  <span>{{ call.agent_name || 'AI Agent' }}</span>
                  <span class="text-muted-foreground/40">•</span>
                  <span class="capitalize">{{ call.niche || 'General' }}</span>
                </p>
              </div>

              <div v-if="call.frustration_score > 0.4" class="text-right">
                <span class="text-[10px] font-mono text-rose-400 bg-rose-500/10 border border-rose-500/20 px-1.5 py-0.5 rounded">
                  Frustration Alert
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Column: Selected Call Detail Workspace (7 Cols) -->
      <div class="lg:col-span-7 flex flex-col gap-4">
        <template v-if="selectedCall">
          <!-- Selected Call Workspace Header -->
          <div class="glass-panel p-5 rounded-xl border border-border/60 space-y-4">
            <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
              <div>
                <div class="flex items-center gap-2.5">
                  <h3 class="text-lg font-bold font-mono text-foreground">{{ selectedCall.caller_phone }}</h3>
                  <BadgePill :variant="selectedCall.state === 'supervisor_takeover' ? 'rose' : 'emerald'" :pulse="true">
                    {{ selectedCall.state === 'supervisor_takeover' ? 'HUMAN TAKEOVER' : 'ACTIVE AI CALL' }}
                  </BadgePill>
                </div>
                <p class="text-xs text-muted-foreground mt-0.5">
                  Agent: <span class="text-foreground font-medium">{{ selectedCall.agent_name }}</span> | Node: <span class="font-mono text-primary">{{ selectedCall.current_node || 'Greeting' }}</span>
                </p>
              </div>

              <!-- Audio Waveform Visualizer -->
              <div class="w-full sm:w-48">
                <WaveformVisualizer :speaker-state="selectedCall.speaker_state" :height="36" />
              </div>
            </div>

            <!-- Supervisor Takeover Control Bar -->
            <TakeoverControlBar
              :is-taken-over="selectedCall.state === 'supervisor_takeover'"
              :is-mic-muted="audioControl.isMicMuted.value"
              @takeover="handleTakeover"
              @release="handleReleaseTakeover"
              @toggle-mic="audioControl.toggleMuteMic"
            />
          </div>

          <!-- Real-Time Transcript Stream -->
          <div class="glass-panel p-5 rounded-xl border border-border/60 flex flex-col flex-1 min-h-[340px]">
            <div class="flex items-center justify-between pb-3 mb-3 border-b border-border/40">
              <span class="text-xs uppercase font-mono font-semibold text-muted-foreground">Live Transcript Stream</span>
              <div class="flex items-center gap-2">
                <button
                  @click="showWhisperModal = true"
                  class="px-2.5 py-1 rounded-md bg-indigo-500/10 hover:bg-indigo-500/20 text-indigo-400 border border-indigo-500/30 text-[11px] font-medium flex items-center gap-1.5 transition-colors cursor-pointer"
                >
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                  </svg>
                  <span>Ghost Whisper</span>
                </button>
                <button
                  @click="showDTMFModal = true"
                  class="px-2.5 py-1 rounded-md bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 text-[11px] font-medium flex items-center gap-1.5 transition-colors cursor-pointer"
                >
                  <span>DTMF Keypad</span>
                </button>
                <button
                  @click="showSMSModal = true"
                  class="px-2.5 py-1 rounded-md bg-sky-500/10 hover:bg-sky-500/20 text-sky-400 border border-sky-500/30 text-[11px] font-medium flex items-center gap-1.5 transition-colors cursor-pointer"
                >
                  <span>Instant SMS</span>
                </button>
              </div>
            </div>

            <!-- Scrollable Turns Waterfall -->
            <div class="flex-1 overflow-y-auto space-y-3 max-h-[380px] pr-1 custom-scrollbar">
              <div v-if="!selectedCall.transcripts || selectedCall.transcripts.length === 0" class="text-center py-12 text-muted-foreground text-xs">
                Awaiting first spoken utterance...
              </div>
              <div
                v-for="turn in selectedCall.transcripts"
                :key="turn.turn_id"
                class="flex gap-2.5 text-xs"
                :class="turn.role === 'user' ? 'justify-start' : 'justify-end'"
              >
                <div
                  class="max-w-[85%] rounded-xl p-3 border leading-relaxed space-y-1"
                  :class="turn.role === 'user' ? 'bg-muted/40 border-border text-foreground' : 'bg-primary/10 border-primary/20 text-foreground'"
                >
                  <div class="flex items-center justify-between text-[10px] font-mono text-muted-foreground gap-4">
                    <span class="font-bold uppercase" :class="turn.role === 'user' ? 'text-sky-400' : 'text-emerald-400'">
                      {{ turn.role === 'user' ? 'Caller' : (selectedCall.agent_name || 'Agent') }}
                    </span>
                    <span>+{{ (turn.offset_ms / 1000).toFixed(1) }}s</span>
                  </div>
                  <p>{{ turn.text }}</p>
                </div>
              </div>
            </div>
          </div>
        </template>

        <!-- No Call Selected Placeholder -->
        <div v-else class="glass-panel p-8 rounded-xl border border-border/50 text-center flex flex-col items-center justify-center flex-1 min-h-[480px]">
          <p class="text-xs text-muted-foreground">Select an active call channel on the left to monitor live audio and supervisor controls.</p>
        </div>
      </div>
    </div>

    <!-- Modals -->
    <GhostWhisperModal
      v-model="showWhisperModal"
      :call-id="selectedCall ? selectedCall.call_id : null"
      @dispatch="handleDispatchWhisper"
    />
    <DTMFDialpadModal
      v-model="showDTMFModal"
      :call-id="selectedCall ? selectedCall.call_id : null"
      @transmit="handleTransmitDTMF"
    />
    <InstantSMSModal
      v-model="showSMSModal"
      :call-id="selectedCall ? selectedCall.call_id : null"
      :default-phone="selectedCall ? selectedCall.caller_phone : ''"
      @send="handleSendSMS"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useLiveCallsStore } from '../stores/liveCalls';
import { useSupervisorControl } from '../composables/useSupervisorControl';
import { useLiveCallAudio } from '../composables/useLiveCallAudio';
import { useAuthStore } from '../stores/auth';

import BadgePill from '../components/common/BadgePill.vue';
import WaveformVisualizer from '../components/common/WaveformVisualizer.vue';
import TakeoverControlBar from '../components/live/TakeoverControlBar.vue';
import GhostWhisperModal from '../components/live/GhostWhisperModal.vue';
import DTMFDialpadModal from '../components/live/DTMFDialpadModal.vue';
import InstantSMSModal from '../components/live/InstantSMSModal.vue';

const liveCallsStore = useLiveCallsStore();
const supervisorControl = useSupervisorControl();
const audioControl = useLiveCallAudio();
const authStore = useAuthStore();

const showWhisperModal = ref(false);
const showDTMFModal = ref(false);
const showSMSModal = ref(false);

const selectedCall = computed(() => liveCallsStore.selectedCall);

function formatElapsed(startedAt) {
  if (!startedAt) return '00:00';
  const sec = Math.floor((Date.now() - startedAt) / 1000);
  const m = Math.floor(sec / 60).toString().padStart(2, '0');
  const s = (sec % 60).toString().padStart(2, '0');
  return `${m}:${s}`;
}

async function handleTakeover() {
  if (!selectedCall.value) return;
  const ok = await supervisorControl.takeOverCall(selectedCall.value.call_id, 'Supervisor');
  if (ok) {
    selectedCall.value.state = 'supervisor_takeover';
  }
}

async function handleReleaseTakeover() {
  if (!selectedCall.value) return;
  const ok = await supervisorControl.releaseTakeover(selectedCall.value.call_id);
  if (ok) {
    selectedCall.value.state = 'active';
  }
}

async function handleDispatchWhisper(prompt) {
  if (!selectedCall.value) return;
  await supervisorControl.sendGhostWhisper(selectedCall.value.call_id, prompt);
}

async function handleTransmitDTMF(digits) {
  if (!selectedCall.value) return;
  await supervisorControl.sendDTMFTones(selectedCall.value.call_id, digits);
}

async function handleSendSMS({ phone, message }) {
  if (!selectedCall.value) return;
  await supervisorControl.sendInstantSMS(selectedCall.value.call_id, phone, message);
}

onMounted(() => {
  liveCallsStore.connectWebSocket(authStore.token);
});

onUnmounted(() => {
  liveCallsStore.disconnectWebSocket();
});
</script>
