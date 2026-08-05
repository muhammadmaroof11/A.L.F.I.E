<template>
  <div class="h-full flex flex-col">
    <div class="flex items-center justify-between mb-4 flex-shrink-0">
      <div>
        <h2 class="text-3xl font-display font-bold text-white mb-2">Live Telemetry</h2>
        <p class="text-sm text-textSecondary">WebSocket event stream from core agent instances</p>
      </div>
      <div class="flex items-center gap-4">
        <button @click="logs = []" class="text-sm font-medium text-textSecondary hover:text-white transition-colors bg-surface hover:bg-surfaceHover px-4 py-2 rounded-lg border border-border">Clear Logs</button>
        <div class="flex items-center gap-2 px-4 py-2 glass rounded-lg">
          <div :class="['w-2.5 h-2.5 rounded-full shadow-[0_0_8px_currentColor]', connected ? 'bg-green text-green animate-pulse' : 'bg-red text-red']"></div>
          <span class="text-xs font-mono uppercase tracking-wider" :class="connected ? 'text-green' : 'text-red'">
            {{ connected ? 'Connected' : 'Disconnected' }}
          </span>
        </div>
      </div>
    </div>

    <!-- Terminal Viewer -->
    <div class="flex-1 bg-[#05050A] border border-border font-mono text-[13px] leading-relaxed p-6 overflow-y-auto flex flex-col gap-3 rounded-xl shadow-inner scroll-smooth" ref="terminalBox">
      <div v-for="(log, idx) in logs" :key="idx" class="border-b border-border/50 pb-3 mb-1 last:border-0 hover:bg-white/[0.02] p-2 rounded transition-colors -mx-2">
        <div class="flex gap-4 mb-2 items-center">
          <span class="text-textMuted w-20 flex-shrink-0 select-none">[{{ formatTime(log.timestamp) }}]</span>
          <span class="text-accentSecondary w-40 flex-shrink-0 truncate font-semibold" :title="log.tenant_id">{{ log.tenant_id || 'System' }}</span>
          <span class="px-2 py-0.5 rounded text-[11px] uppercase tracking-wider bg-accent/10 text-accent border border-accent/20">{{ log.event_type }}</span>
        </div>
        <div class="pl-[104px] pr-4">
          <pre class="text-[#a5b4fc] whitespace-pre-wrap break-all">{{ formatJson(log.data || log.metrics) }}</pre>
        </div>
      </div>
      
      <div v-if="logs.length === 0" class="text-textMuted italic flex items-center justify-center h-full gap-3">
        <svg class="animate-spin h-5 w-5 text-accent" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
        Listening for telemetry events on port 8000...
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue';
import { useAuthStore } from '../stores/auth';

const authStore = useAuthStore();
const logs = ref([]);
const connected = ref(false);
const terminalBox = ref(null);
let ws = null;

const formatTime = (ts) => {
  const d = ts ? new Date(ts) : new Date();
  return d.toISOString().split('T')[1].substring(0, 8); // HH:mm:ss
};

const formatJson = (obj) => {
  try {
    return JSON.stringify(obj, null, 2);
  } catch (e) {
    return obj;
  }
};

const connectWs = () => {
  const token = authStore.token;
  const wsUrl = `ws://localhost:8000/api/super/telemetry/ws?token=${token}`;
  ws = new WebSocket(wsUrl);

  ws.onopen = () => {
    connected.value = true;
  };

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      logs.value.push(data);
      // Keep only last 100 logs
      if (logs.value.length > 100) {
        logs.value.shift();
      }
      // Scroll to bottom
      nextTick(() => {
        if (terminalBox.value) {
          terminalBox.value.scrollTop = terminalBox.value.scrollHeight;
        }
      });
    } catch (e) {
      console.error(e);
    }
  };

  ws.onclose = () => {
    connected.value = false;
    // Auto-reconnect after 3s
    setTimeout(connectWs, 3000);
  };
  
  ws.onerror = () => {
    connected.value = false;
  };
};

onMounted(() => {
  connectWs();
});

onUnmounted(() => {
  if (ws) {
    ws.onclose = null; // Prevent reconnect
    ws.close();
  }
});
</script>
