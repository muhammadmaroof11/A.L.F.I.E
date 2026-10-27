<template>
  <div class="h-full flex flex-col p-8 overflow-y-auto w-full max-w-6xl mx-auto space-y-8">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-3xl font-bold tracking-tight text-foreground flex items-center gap-3">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-primary"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg>
          Callbacks & Timezone-Gated Queue
        </h1>
        <p class="text-muted-foreground mt-1 text-sm">
          Intelligent 3-touch retry cadence with automated Federal & State TCPA legal calling hours enforcement (8:00 AM - 9:00 PM).
        </p>
      </div>
      <div class="flex items-center gap-3">
        <button @click="fetchCallbacks" class="glass-button text-xs px-3.5 py-2 flex items-center gap-1.5 hover:bg-muted/50 transition-colors">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" :class="{ 'animate-spin': loading }"><path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"/></svg>
          Refresh Queue
        </button>
      </div>
    </div>

    <!-- Summary KPI Cards -->
    <div class="grid grid-cols-2 md:grid-cols-5 gap-4">
      <div class="glass-panel p-4 rounded-xl border border-border/50">
        <div class="text-xs text-muted-foreground font-medium">In Cadence</div>
        <div class="text-2xl font-bold text-foreground mt-1">{{ summary.in_cadence }}</div>
        <div class="text-[10px] text-muted-foreground mt-0.5">Active automated retry</div>
      </div>
      <div class="glass-panel p-4 rounded-xl border border-emerald-500/20 bg-emerald-500/5">
        <div class="text-xs text-emerald-400 font-medium flex items-center gap-1.5">
          <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
          Ready Now
        </div>
        <div class="text-2xl font-bold text-emerald-400 mt-1">{{ summary.ready_now }}</div>
        <div class="text-[10px] text-emerald-400/80 mt-0.5">Inside legal calling hours</div>
      </div>
      <div class="glass-panel p-4 rounded-xl border border-amber-500/20 bg-amber-500/5">
        <div class="text-xs text-amber-400 font-medium flex items-center gap-1.5">
          <span class="w-1.5 h-1.5 rounded-full bg-amber-400"></span>
          Quiet Hours
        </div>
        <div class="text-2xl font-bold text-amber-400 mt-1">{{ summary.quiet_hours_postponed }}</div>
        <div class="text-[10px] text-amber-400/80 mt-0.5">Postponed to 8:05 AM</div>
      </div>
      <div class="glass-panel p-4 rounded-xl border border-border/50">
        <div class="text-xs text-muted-foreground font-medium">Completed</div>
        <div class="text-2xl font-bold text-foreground mt-1">{{ summary.completed }}</div>
        <div class="text-[10px] text-muted-foreground mt-0.5">Successfully connected</div>
      </div>
      <div class="glass-panel p-4 rounded-xl border border-border/50">
        <div class="text-xs text-muted-foreground font-medium">Exhausted</div>
        <div class="text-2xl font-bold text-foreground mt-1">{{ summary.exhausted }}</div>
        <div class="text-[10px] text-muted-foreground mt-0.5">3 touches complete</div>
      </div>
    </div>

    <!-- Error/Loading states -->
    <div v-if="loading" class="flex justify-center p-12">
      <div class="animate-pulse flex flex-col items-center gap-4">
        <div class="h-12 w-12 rounded-full border-4 border-primary border-t-transparent animate-spin"></div>
        <p class="text-muted-foreground text-sm font-medium">Loading callback queue & timezone guardrails...</p>
      </div>
    </div>
    
    <div v-else-if="error" class="glass-panel p-6 border-red-500/20 bg-red-500/5 text-red-400 rounded-xl">
      <p>{{ error }}</p>
    </div>

    <div v-else-if="callbacks.length === 0" class="glass-panel p-16 flex flex-col items-center justify-center text-center rounded-xl border border-border/50">
      <div class="w-16 h-16 rounded-full bg-emerald-500/10 flex items-center justify-center mb-4 text-emerald-500">
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg>
      </div>
      <h3 class="text-xl font-semibold text-foreground mb-2">No Callbacks in Queue</h3>
      <p class="text-muted-foreground max-w-md">All scheduled callbacks, hot-transfer fallbacks, and cadence retries are currently up to date.</p>
    </div>

    <!-- Callbacks List -->
    <div v-else class="space-y-4">
      <div 
        v-for="item in callbacks" 
        :key="item.id" 
        class="glass-panel p-6 rounded-xl border transition-all space-y-4"
        :class="item.cadence_status === 'exhausted' ? 'opacity-70 border-border/40' : 'border-border/60 hover:border-primary/40'"
      >
        <!-- Header row -->
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-3">
          <div class="space-y-1.5">
            <div class="flex flex-wrap items-center gap-2.5">
              <h3 class="text-lg font-bold text-foreground">{{ item.caller_name }}</h3>
              <span class="text-xs font-mono bg-primary/10 text-primary px-2.5 py-0.5 rounded-full border border-primary/20">
                {{ item.caller_phone }}
              </span>

              <!-- Timezone & Local Time Badge -->
              <span class="text-xs px-2.5 py-0.5 rounded-full border flex items-center gap-1.5 font-mono bg-muted/40 text-foreground/80 border-border/60">
                <span>📍 {{ item.recipient_state || 'US' }} ({{ item.recipient_timezone }})</span>
                <span v-if="item.recipient_local_time" class="font-bold text-foreground">
                  · {{ item.recipient_local_time }} {{ item.recipient_local_tz_abbr }}
                </span>
              </span>

              <!-- TCPA Legal Calling Hours Pill -->
              <span 
                v-if="item.is_legal_now"
                class="text-xs font-semibold px-2.5 py-0.5 rounded-full border bg-emerald-500/10 text-emerald-400 border-emerald-500/20 flex items-center gap-1"
              >
                <span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                Legal Hours Active
              </span>
              <span 
                v-else
                class="text-xs font-semibold px-2.5 py-0.5 rounded-full border bg-amber-500/10 text-amber-400 border-amber-500/20 flex items-center gap-1"
                :title="item.tcpa_status_reason"
              >
                <span>🌙</span>
                Quiet Hours Postponed
              </span>

              <!-- Status Pill -->
              <span 
                :class="getStatusBadgeClass(item)"
                class="text-xs font-semibold px-2.5 py-0.5 rounded-full border capitalize"
              >
                {{ item.cadence_status || item.status }}
              </span>
            </div>

            <!-- Details subtitle -->
            <div class="text-xs text-muted-foreground flex flex-wrap items-center gap-4 pt-1">
              <span class="flex items-center gap-1.5 text-foreground/90 font-medium">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="text-primary"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
                Requested Time: {{ item.preferred_time || 'Immediate' }}
              </span>
              <span class="flex items-center gap-1.5">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle></svg>
                Department: {{ item.target_department || 'General' }}
              </span>
              <span v-if="item.next_attempt_at" class="flex items-center gap-1.5 text-primary font-mono font-medium">
                <span>⏰ Next Attempt:</span> {{ formatDate(item.next_attempt_at) }}
              </span>
            </div>
          </div>

          <!-- Action buttons -->
          <div class="flex items-center gap-2 self-end md:self-center flex-shrink-0">
            <button 
              v-if="item.cadence_status !== 'completed' && item.cadence_status !== 'cancelled'"
              @click="triggerRetry(item)" 
              :disabled="triggeringId === item.id"
              class="glass-button bg-primary/10 text-primary hover:bg-primary/20 text-xs px-3 py-1.5 flex items-center gap-1.5 transition-colors disabled:opacity-50"
            >
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg>
              {{ item.is_legal_now ? 'Dispatch Call Now' : 'Force Call' }}
            </button>

            <button 
              v-if="item.cadence_status !== 'completed'" 
              @click="markCompleted(item.id)" 
              class="glass-button bg-emerald-500/10 text-emerald-400 hover:bg-emerald-500/20 text-xs px-3 py-1.5 flex items-center gap-1.5 transition-colors"
            >
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg>
              Mark Done
            </button>

            <button 
              v-if="item.cadence_status !== 'completed' && item.cadence_status !== 'cancelled' && item.cadence_status !== 'exhausted'" 
              @click="cancelCadence(item.id)" 
              class="glass-button text-muted-foreground hover:text-red-400 hover:bg-red-500/10 text-xs px-2.5 py-1.5 transition-colors"
              title="Cancel Automated Cadence"
            >
              Cancel
            </button>
          </div>
        </div>

        <!-- 3-Touch Cadence Progress Stepper -->
        <div class="bg-muted/15 p-3 rounded-lg border border-border/30 space-y-2">
          <div class="flex items-center justify-between text-xs">
            <span class="font-medium text-foreground/90 flex items-center gap-2">
              <span>3-Touch Cadence Progress:</span>
              <span class="font-mono text-primary font-bold">Touch {{ Math.min(item.attempt_count || 0, 3) }}/3</span>
            </span>
            <span v-if="item.sms_notice_sent" class="text-[11px] font-mono text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 rounded-full flex items-center gap-1">
              <span>💬</span> Touch 3 SMS Sent
            </span>
          </div>

          <!-- Stepper Visual -->
          <div class="grid grid-cols-3 gap-2 text-[11px]">
            <div 
              class="p-2 rounded border flex flex-col gap-0.5"
              :class="getStepClass(1, item.attempt_count)"
            >
              <span class="font-semibold flex items-center justify-between">
                <span>1. Initial Touch</span>
                <span v-if="(item.attempt_count || 0) >= 1">✓</span>
              </span>
              <span class="text-[10px] opacity-75">Immediate / Preferred</span>
            </div>

            <div 
              class="p-2 rounded border flex flex-col gap-0.5"
              :class="getStepClass(2, item.attempt_count)"
            >
              <span class="font-semibold flex items-center justify-between">
                <span>2. Follow-Up Touch</span>
                <span v-if="(item.attempt_count || 0) >= 2">✓</span>
              </span>
              <span class="text-[10px] opacity-75">+2 Hours Cadence</span>
            </div>

            <div 
              class="p-2 rounded border flex flex-col gap-0.5"
              :class="getStepClass(3, item.attempt_count)"
            >
              <span class="font-semibold flex items-center justify-between">
                <span>3. Final + SMS</span>
                <span v-if="(item.attempt_count || 0) >= 3">✓</span>
              </span>
              <span class="text-[10px] opacity-75">+24 Hours + SMS Link</span>
            </div>
          </div>
        </div>

        <!-- Notes / Topic Snippet -->
        <p v-if="item.reason || item.notes" class="text-xs text-muted-foreground/90 bg-muted/20 p-2.5 rounded-lg border border-border/30">
          <strong class="text-foreground">Inquiry Topic:</strong> {{ item.reason }} <span v-if="item.notes">— {{ item.notes }}</span>
        </p>

        <!-- Expandable Attempt History Audit -->
        <div v-if="item.attempt_history && item.attempt_history.length > 0">
          <button 
            @click="toggleHistory(item.id)" 
            class="text-[11px] text-muted-foreground hover:text-foreground flex items-center gap-1 font-medium transition-colors"
          >
            <span>{{ expandedHistory[item.id] ? 'Hide' : 'Show' }} Touch History ({{ item.attempt_history.length }})</span>
            <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" :class="{ 'rotate-180': expandedHistory[item.id] }"><polyline points="6 9 12 15 18 9"></polyline></svg>
          </button>

          <div v-if="expandedHistory[item.id]" class="mt-2 space-y-1.5 pl-2 border-l-2 border-primary/30">
            <div 
              v-for="(h, idx) in item.attempt_history" 
              :key="idx" 
              class="text-[11px] font-mono text-muted-foreground flex flex-wrap items-center gap-2"
            >
              <span class="text-foreground font-semibold">Touch {{ h.touch }}:</span>
              <span :class="h.action === 'call_dispatched' ? 'text-primary' : (h.action === 'sms_notice_sent' ? 'text-emerald-400' : 'text-amber-400')">
                {{ h.action }}
              </span>
              <span v-if="h.reason">({{ h.reason }})</span>
              <span class="text-muted-foreground/60">@ {{ formatDate(h.timestamp) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useAuthStore } from '../stores/auth';
import api from '../services/api';

const authStore = useAuthStore();
const loading = ref(true);
const error = ref('');
const callbacks = ref([]);
const triggeringId = ref(null);
const expandedHistory = ref({});

const summary = ref({
  total_callbacks: 0,
  in_cadence: 0,
  ready_now: 0,
  quiet_hours_postponed: 0,
  completed: 0,
  exhausted: 0,
});

const fetchSummary = async () => {
  try {
    const tenantId = authStore.tenantId || localStorage.getItem('alfie_tenant_id');
    const res = await api.get(`/api/client/callbacks/summary?tenant_id=${tenantId}`);
    if (res.data) {
      summary.value = res.data;
    }
  } catch (err) {
    console.warn("Could not fetch callback cadence summary:", err);
  }
};

const fetchCallbacks = async () => {
  loading.value = true;
  error.value = '';
  try {
    const tenantId = authStore.tenantId || localStorage.getItem('alfie_tenant_id') || localStorage.getItem('tenant_id');
    const res = await api.get(`/api/client/callbacks?tenant_id=${tenantId}`);
    callbacks.value = Array.isArray(res.data) ? res.data : (res.data?.items || []);
    await fetchSummary();
  } catch (err) {
    console.error(err);
    error.value = 'Failed to load scheduled callbacks.';
  } finally {
    loading.value = false;
  }
};

const markCompleted = async (id) => {
  try {
    await api.patch(`/api/client/callbacks/${id}`, { status: 'completed' });
    const target = callbacks.value.find(c => c.id === id);
    if (target) {
      target.status = 'completed';
      target.cadence_status = 'completed';
    }
    await fetchSummary();
  } catch (err) {
    console.error("Failed to mark callback completed:", err);
  }
};

const cancelCadence = async (id) => {
  try {
    await api.post(`/api/client/callbacks/${id}/cancel`);
    const target = callbacks.value.find(c => c.id === id);
    if (target) {
      target.cadence_status = 'cancelled';
      target.status = 'cancelled';
      target.next_attempt_at = null;
    }
    await fetchSummary();
  } catch (err) {
    console.error("Failed to cancel cadence:", err);
  }
};

const triggerRetry = async (item) => {
  triggeringId.value = item.id;
  try {
    const forceParam = !item.is_legal_now ? '?force=true' : '';
    await api.post(`/api/client/callbacks/${item.id}/retry${forceParam}`);
    await fetchCallbacks();
  } catch (err) {
    console.error("Failed to trigger callback retry:", err);
  } finally {
    triggeringId.value = null;
  }
};

const toggleHistory = (id) => {
  expandedHistory.value[id] = !expandedHistory.value[id];
};

const getStatusBadgeClass = (item) => {
  const st = item.cadence_status || item.status;
  switch (st) {
    case 'completed':
      return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20';
    case 'rescheduled_legal_hours':
      return 'bg-amber-500/10 text-amber-400 border-amber-500/20';
    case 'exhausted':
      return 'bg-rose-500/10 text-rose-400 border-rose-500/20';
    case 'cancelled':
      return 'bg-muted/30 text-muted-foreground border-border/50';
    case 'in_progress':
      return 'bg-primary/10 text-primary border-primary/20';
    default:
      return 'bg-sky-500/10 text-sky-400 border-sky-500/20';
  }
};

const getStepClass = (stepNumber, attemptCount) => {
  const currentAttempts = attemptCount || 0;
  if (currentAttempts >= stepNumber) {
    return 'bg-primary/10 border-primary/30 text-primary';
  }
  if (currentAttempts === stepNumber - 1) {
    return 'bg-muted/40 border-border/60 text-foreground font-medium';
  }
  return 'bg-muted/10 border-border/30 text-muted-foreground/60';
};

const formatDate = (isoString) => {
  if (!isoString) return '-';
  try {
    const d = new Date(isoString);
    return d.toLocaleString([], { 
      month: 'short', 
      day: 'numeric', 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  } catch {
    return isoString;
  }
};

onMounted(() => {
  fetchCallbacks();
});
</script>
