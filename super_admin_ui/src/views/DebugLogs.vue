<template>
  <div class="h-full flex flex-col">
    <div class="flex items-center justify-between mb-4 flex-shrink-0">
      <div>
        <h2 class="text-xl font-mono text-white mb-1">Live Telemetry</h2>
        <p class="text-sm font-mono text-textMuted">WebSocket event stream from core agent instances</p>
      </div>
      <div class="flex items-center gap-4">
        <button @click="logs = []" class="text-sm font-mono text-textMuted hover:text-white transition-colors">Clear Logs</button>
        <div class="flex items-center gap-2 px-3 py-1 bg-bgBase border border-bgSurface">
          <div :class="['w-2 h-2 rounded-full', connected ? 'bg-green animate-pulse' : 'bg-red']"></div>
          <span class="text-xs font-mono uppercase" :class="connected ? 'text-green' : 'text-red'">
            {{ connected ? 'Connected' : 'Disconnected' }}
          </span>
        </div>
      </div>
    </div>

    <!-- Terminal Viewer -->
    <div class="flex-1 bg-[#01030B] border border-bgSurface font-mono text-sm p-4 overflow-y-auto flex flex-col gap-2 rounded shadow-inner" ref="terminalBox">
      <div v-for="(log, idx) in logs" :key="idx" class="border-b border-bgSurface/20 pb-2 mb-2 last:border-0">
        <div class="flex gap-4 mb-1">
          <span class="text-textMuted w-24 flex-shrink-0">{{ formatTime(log.timestamp) }}</span>
          <span class="text-blue w-48 flex-shrink-0 truncate" :title="log.tenant_id">{{ log.tenant_id }}</span>
          <span class="text-amber w-48 flex-shrink-0 truncate">{{ log.event_type }}</span>
        </div>
        <div class="pl-28 pr-4">
          <pre class="text-textSecondary text-xs whitespace-pre-wrap break-all">{{ formatJson(log.data || log.metrics) }}</pre>
        </div>
      </div>
      
      <div v-if="logs.length === 0" class="text-textMuted italic flex items-center justify-center h-full">
        Waiting for telemetry events...
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue';

const logs = ref([]);
const connected = ref(false);
const terminalBox = ref(null);
let ws = null;

const formatTime = (ts) => {
  const d = new Date(ts);
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
  const wsUrl = `ws://localhost:8000/api/super/telemetry/ws`;
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
