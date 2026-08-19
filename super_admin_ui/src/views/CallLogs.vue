<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
      <div class="flex flex-col space-y-1">
        <h2 class="text-2xl font-semibold tracking-tight">Telemetry & System Call Logs</h2>
        <p class="text-sm text-muted-foreground">Technical latency metrics, billing consumption, and AI engine telemetry logs per tenant.</p>
      </div>
      <div class="flex items-center gap-3 w-full sm:w-auto">
        <select class="flex h-9 w-full sm:w-48 rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring" v-model="selectedTenantFilter" @change="fetchCalls">
          <option value="">All Tenants</option>
          <option v-for="t in tenantsList" :key="t.tenant_id" :value="t.tenant_id">
            {{ t.name }}
          </option>
        </select>
        <div class="relative w-full sm:w-64">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
          <input type="text" class="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring pl-9" placeholder="Search call ID or phone..." v-model="searchQuery" />
        </div>
      </div>
    </div>

    <!-- Privacy Banner -->
    <div class="rounded-lg border border-primary/20 bg-primary/5 p-4 flex items-center justify-between">
      <div class="flex items-start sm:items-center gap-3">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-primary mt-0.5 sm:mt-0 shrink-0"><rect width="18" height="11" x="3" y="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
        <p class="text-sm text-foreground">
          <strong class="font-semibold">Strict Tenant Data Privacy Enforced</strong> — Private customer transcripts and audio recordings are strictly isolated to the Client Admin Portal. Super Admin displays technical latency, financial cost, and model metrics only.
        </p>
      </div>
      <span class="hidden sm:inline-flex items-center rounded-full border border-transparent bg-primary/10 px-2.5 py-0.5 text-xs font-semibold text-primary transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 shrink-0 ml-4">
        Privacy Mode Active
      </span>
    </div>

    <!-- Stats strip -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="rounded-xl border bg-card text-card-foreground shadow-sm p-6 flex flex-col justify-between">
        <h3 class="tracking-tight text-sm font-medium text-muted-foreground">Total Logged Calls</h3>
        <div class="text-2xl font-bold mt-2 font-mono">{{ calls.length }}</div>
      </div>
      <div class="rounded-xl border bg-card text-card-foreground shadow-sm p-6 flex flex-col justify-between">
        <h3 class="tracking-tight text-sm font-medium text-muted-foreground">Credits Consumed</h3>
        <div class="text-2xl font-bold mt-2 text-emerald-500 font-mono">${{ totalCreditsConsumed.toFixed(2) }}</div>
      </div>
      <div class="rounded-xl border bg-card text-card-foreground shadow-sm p-6 flex flex-col justify-between">
        <h3 class="tracking-tight text-sm font-medium text-muted-foreground">Avg End-to-End Latency</h3>
        <div class="text-2xl font-bold mt-2 text-primary font-mono">{{ avgLatency }}<span class="text-sm font-sans text-muted-foreground">ms</span></div>
      </div>
      <div class="rounded-xl border bg-card text-card-foreground shadow-sm p-6 flex flex-col justify-between">
        <h3 class="tracking-tight text-sm font-medium text-muted-foreground">Estimated Gross Revenue</h3>
        <div class="text-2xl font-bold mt-2 text-amber-500 font-mono">${{ totalBilledAmount.toFixed(2) }}</div>
      </div>
    </div>

    <div v-if="loading" class="flex items-center justify-center h-32 text-muted-foreground">
      Loading telemetry logs...
    </div>

    <!-- Data Table -->
    <div v-else class="rounded-md border bg-card shadow-sm">
      <div class="w-full overflow-auto">
        <table class="w-full caption-bottom text-sm">
          <thead class="[&_tr]:border-b bg-muted/50">
            <tr class="border-b transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted">
              <th class="h-10 px-4 text-left align-middle font-medium text-muted-foreground w-[25%]">Call ID / Tenant</th>
              <th class="h-10 px-4 text-left align-middle font-medium text-muted-foreground">Caller Phone</th>
              <th class="h-10 px-4 text-left align-middle font-medium text-muted-foreground">Duration</th>
              <th class="h-10 px-4 text-left align-middle font-medium text-muted-foreground">AI Model & Latency</th>
              <th class="h-10 px-4 text-left align-middle font-medium text-muted-foreground">Cost / Billed</th>
              <th class="h-10 px-4 text-right align-middle font-medium text-muted-foreground">Action</th>
            </tr>
          </thead>
          <tbody class="[&_tr:last-child]:border-0">
            <tr v-if="filteredCalls.length === 0">
              <td colspan="6" class="p-8 text-center text-muted-foreground">No call logs found matching your criteria.</td>
            </tr>
            <tr v-for="call in filteredCalls" :key="call.call_id" class="border-b transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted cursor-pointer" @click="selectCall(call)">
              <td class="p-4 align-middle">
                <div class="flex flex-col space-y-1">
                  <span class="font-mono text-xs font-semibold text-foreground truncate" :title="call.call_id">{{ call.call_id }}</span>
                  <span class="text-xs text-muted-foreground truncate" :title="call.tenant_id">{{ call.tenant_id }}</span>
                </div>
              </td>
              <td class="p-4 align-middle">
                <div class="flex flex-col items-start gap-1">
                  <span class="font-mono text-xs">{{ call.caller_number || '+18005550199' }}</span>
                  <span class="inline-flex items-center rounded-full border border-transparent bg-secondary px-2 py-0.5 text-[10px] font-semibold text-secondary-foreground transition-colors hover:bg-secondary/80">
                    {{ call.niche }}
                  </span>
                </div>
              </td>
              <td class="p-4 align-middle">
                <span class="font-mono font-medium">{{ formatDuration(call.duration_seconds) }}</span>
              </td>
              <td class="p-4 align-middle">
                <div class="flex flex-col space-y-1">
                  <span class="font-mono text-[11px] text-accent font-semibold">{{ call.ai_model || 'llama-3.3-70b-instruct' }}</span>
                  <span class="text-[10px] text-muted-foreground font-mono">
                    STT: {{ call.stt_ms || 180 }}ms | LLM: {{ call.llm_ttft_ms || 420 }}ms | TTS: {{ call.tts_ms || 210 }}ms
                  </span>
                </div>
              </td>
              <td class="p-4 align-middle">
                <div class="flex flex-col space-y-0.5">
                  <div class="text-[11px] text-muted-foreground">
                    Raw: <span class="font-mono text-rose-500 font-medium">${{ (call.raw_cost_usd || 0.08).toFixed(3) }}</span>
                  </div>
                  <div class="text-[11px] font-medium text-emerald-500">
                    Billed: <span class="font-mono">${{ (call.billed_amount_usd || 0.20).toFixed(2) }}</span>
                  </div>
                </div>
              </td>
              <td class="p-4 align-middle text-right">
                <button class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-xs font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring hover:bg-accent hover:text-accent-foreground h-8 px-3 text-muted-foreground hover:text-foreground">
                  Metrics
                  <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="ml-1"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Technical Metrics Drawer -->
    <div v-if="selectedCall" class="fixed inset-0 z-50 bg-background/80 backdrop-blur-sm flex justify-end">
      <div class="fixed inset-y-0 right-0 z-50 w-full max-w-lg border-l bg-background shadow-lg transition-transform duration-300 sm:max-w-md md:max-w-lg flex flex-col">
        <div class="flex items-center justify-between border-b px-6 py-4 shrink-0">
          <div class="flex flex-col space-y-1">
            <h2 class="text-lg font-semibold tracking-tight">Telemetry Breakdown</h2>
            <p class="text-xs text-muted-foreground font-mono truncate w-64">{{ selectedCall.call_id }}</p>
          </div>
          <button @click="selectedCall = null" class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring hover:bg-muted text-muted-foreground h-8 w-8">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
            <span class="sr-only">Close</span>
          </button>
        </div>

        <div class="flex-1 overflow-y-auto p-6 space-y-6">
          
          <!-- Latency Waterfall Breakdown -->
          <div class="rounded-lg border bg-card text-card-foreground shadow-sm">
            <div class="flex flex-col space-y-1.5 p-4 border-b">
              <h3 class="font-semibold leading-none tracking-tight flex items-center gap-2">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-primary"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
                Latency Waterfall
              </h3>
            </div>
            <div class="p-4 space-y-3 font-mono text-xs">
              <div class="flex items-center justify-between">
                <span class="text-muted-foreground">1. STT Streaming (Deepgram)</span>
                <span class="text-cyan-500 font-medium">{{ selectedCall.stt_ms || 180 }} ms</span>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-muted-foreground">2. LLM Time-To-First-Token</span>
                <span class="text-accent font-medium">{{ selectedCall.llm_ttft_ms || 420 }} ms</span>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-muted-foreground">3. TTS Synthesis (Fish Audio)</span>
                <span class="text-amber-500 font-medium">{{ selectedCall.tts_ms || 210 }} ms</span>
              </div>
            </div>
            <div class="px-4 py-3 bg-muted/50 border-t flex items-center justify-between font-medium text-sm">
              <span>Total Turnaround Latency</span>
              <span class="text-emerald-500 font-mono">{{ selectedCall.total_ms || 810 }} ms</span>
            </div>
          </div>

          <!-- Financial Calculation Breakdown -->
          <div class="rounded-lg border bg-card text-card-foreground shadow-sm">
            <div class="flex flex-col space-y-1.5 p-4 border-b">
              <h3 class="font-semibold leading-none tracking-tight flex items-center gap-2">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-amber-500"><rect width="20" height="14" x="2" y="5" rx="2"/><line x1="2" y1="10" x2="22" y2="10"/></svg>
                Financial Breakdown
              </h3>
            </div>
            <div class="p-4 space-y-3 text-sm">
              <div class="flex items-center justify-between">
                <span class="text-muted-foreground">Call Duration</span>
                <span class="font-mono">{{ formatDuration(selectedCall.duration_seconds) }} ({{ selectedCall.duration_seconds }}s)</span>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-muted-foreground">Raw Provider Cost</span>
                <span class="font-mono text-rose-500">${{ (selectedCall.raw_cost_usd || 0.08).toFixed(3) }}</span>
              </div>
              <div class="flex items-center justify-between font-medium">
                <span class="text-foreground">Billed Credit Amount (Markup)</span>
                <span class="font-mono text-emerald-500">${{ (selectedCall.billed_amount_usd || 0.20).toFixed(2) }}</span>
              </div>
            </div>
            <div class="px-4 py-3 bg-muted/50 border-t flex items-center justify-between font-medium text-sm">
              <span>Estimated Net Margin</span>
              <span class="text-primary font-mono">+${{ ((selectedCall.billed_amount_usd || 0.20) - (selectedCall.raw_cost_usd || 0.08)).toFixed(3) }}</span>
            </div>
          </div>

          <!-- Privacy Notice -->
          <div class="rounded-lg border border-rose-500/20 bg-rose-500/5 p-4 text-xs text-muted-foreground flex items-start gap-3">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-rose-500 shrink-0 mt-0.5"><rect width="18" height="11" x="3" y="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
            <p>Private conversation transcripts and audio recordings are excluded from Super Admin views to protect client data privacy. Access is restricted to the tenant's Client Admin Portal.</p>
          </div>

        </div>

        <div class="border-t p-4 flex justify-end bg-background shrink-0">
          <button @click="selectedCall = null" class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring border border-input bg-background shadow-sm hover:bg-accent hover:text-accent-foreground h-9 px-4 py-2">
            Close Drawer
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import api from '../services/api';

const calls = ref([]);
const tenantsList = ref([]);
const selectedTenantFilter = ref('');
const loading = ref(true);
const searchQuery = ref('');
const selectedCall = ref(null);

const formatDuration = (secs) => {
  if (!secs) return '0:00';
  const m = Math.floor(secs / 60);
  const s = secs % 60;
  return `${m}:${s < 10 ? '0' : ''}${s}`;
};

const fetchTenants = async () => {
  try {
    const res = await api.get('/api/super/tenants');
    tenantsList.value = res.data || [];
  } catch (err) {
    console.warn('Could not fetch tenants list:', err);
  }
};

const fetchCalls = async () => {
  loading.value = true;
  try {
    const url = selectedTenantFilter.value ? `/api/super/calls?tenant_id=${selectedTenantFilter.value}` : '/api/super/calls';
    const res = await api.get(url);
    calls.value = res.data || [];
  } catch (err) {
    console.warn('Could not fetch calls:', err);
  } finally {
    loading.value = false;
  }
};

const totalCreditsConsumed = computed(() => {
  return calls.value.reduce((acc, c) => acc + (c.credits_consumed || 0), 0);
});

const totalBilledAmount = computed(() => {
  return calls.value.reduce((acc, c) => acc + (c.billed_amount_usd || 0), 0);
});

const avgLatency = computed(() => {
  if (!calls.value.length) return 0;
  const sum = calls.value.reduce((acc, c) => acc + (c.total_ms || ((c.stt_ms || 180) + (c.llm_ttft_ms || 420) + (c.tts_ms || 190))), 0);
  return Math.round(sum / calls.value.length);
});

const filteredCalls = computed(() => {
  if (!searchQuery.value.trim()) return calls.value;
  const q = searchQuery.value.toLowerCase();
  return calls.value.filter(c => 
    (c.call_id && c.call_id.toLowerCase().includes(q)) ||
    (c.tenant_id && c.tenant_id.toLowerCase().includes(q)) ||
    (c.caller_number && c.caller_number.toLowerCase().includes(q))
  );
});

const selectCall = (call) => {
  selectedCall.value = call;
};

onMounted(() => {
  fetchTenants();
  fetchCalls();
});
</script>
