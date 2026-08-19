<template>
  <div class="space-y-6">
    <!-- Header with Live Refresh -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
      <div>
        <h1 class="text-2xl font-bold tracking-tight text-foreground">Platform Overview</h1>
        <p class="text-xs text-muted-foreground mt-0.5">Real-time aggregate performance, financial margins, and fleet telemetry.</p>
      </div>
      <div class="flex items-center gap-2">
        <button @click="loadStats" class="glass-button text-xs px-3 py-1.5 flex items-center gap-1.5 hover:bg-muted/50">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" :class="{ 'animate-spin': loading }"><path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"/></svg>
          Refresh Stats
        </button>
      </div>
    </div>

    <!-- KPI Stats Row -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="rounded-xl glass-panel text-card-foreground hover-glow relative overflow-hidden group">
        <div class="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
        <div class="p-6 flex flex-row items-center justify-between space-y-0 pb-2 relative z-10">
          <h3 class="tracking-tight text-sm font-medium">Total Calls Logged</h3>
          <div class="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-primary"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg>
          </div>
        </div>
        <div class="p-6 pt-0 relative z-10">
          <div class="text-3xl font-bold font-mono tracking-tight">{{ animatedCalls }}</div>
          <p class="text-xs text-muted-foreground mt-1 flex items-center gap-1">
            <span class="text-emerald-500 font-medium flex items-center"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 19V5M5 12l7-7 7 7"/></svg> Real-time</span> aggregated across all active tenants
          </p>
        </div>
      </div>

      <div class="rounded-xl glass-panel text-card-foreground hover-glow relative overflow-hidden group">
        <div class="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
        <div class="p-6 flex flex-row items-center justify-between space-y-0 pb-2 relative z-10">
          <h3 class="tracking-tight text-sm font-medium">Active Tenants</h3>
          <div class="w-8 h-8 rounded-full bg-accent/10 flex items-center justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-accent"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
          </div>
        </div>
        <div class="p-6 pt-0 relative z-10">
          <div class="text-3xl font-bold font-mono tracking-tight">{{ animatedTenants }}</div>
          <p class="text-xs text-muted-foreground mt-1 flex items-center gap-1">
            <span class="text-emerald-500 font-medium flex items-center"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 19V5M5 12l7-7 7 7"/></svg> {{ rawData.total_agents || 0 }}</span> active provisioned agents
          </p>
        </div>
      </div>

      <div class="rounded-xl glass-panel text-card-foreground hover-glow relative overflow-hidden group">
        <div class="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
        <div class="p-6 flex flex-row items-center justify-between space-y-0 pb-2 relative z-10">
          <h3 class="tracking-tight text-sm font-medium">Revenue (MTD)</h3>
          <div class="w-8 h-8 rounded-full bg-emerald-500/10 flex items-center justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-emerald-500"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
          </div>
        </div>
        <div class="p-6 pt-0 relative z-10">
          <div class="text-3xl font-bold font-mono tracking-tight">${{ animatedRevenue }}</div>
          <p class="text-xs text-muted-foreground mt-1 flex items-center gap-1">
            <span class="text-emerald-500 font-medium">Live Active Subscriptions</span>
          </p>
        </div>
      </div>

      <div class="rounded-xl glass-panel text-card-foreground hover-glow relative overflow-hidden group">
        <div class="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
        <div class="p-6 flex flex-row items-center justify-between space-y-0 pb-2 relative z-10">
          <h3 class="tracking-tight text-sm font-medium">Gross Margin</h3>
          <div class="w-8 h-8 rounded-full bg-blue-500/10 flex items-center justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-blue-500"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
          </div>
        </div>
        <div class="p-6 pt-0 relative z-10">
          <div class="text-3xl font-bold font-mono text-foreground tracking-tight">${{ animatedMargin }}</div>
          <p class="text-xs text-muted-foreground mt-1 flex items-center gap-1">
            <span class="text-rose-400 font-medium">${{ animatedCost }}</span> raw infrastructure cost
          </p>
        </div>
      </div>
    </div>

    <!-- Charts Row -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
      <!-- 7-Day Call Volume Chart -->
      <div class="col-span-2 rounded-xl glass-panel text-card-foreground">
        <div class="flex flex-col space-y-1.5 p-6 pb-2">
          <h3 class="font-semibold leading-none tracking-tight">Call Volume (Last 7 Days)</h3>
          <p class="text-xs text-muted-foreground">Aggregated daily voice sessions across all active tenants</p>
        </div>
        <div class="p-6 pt-0">
          <div class="flex items-end gap-3 h-36 mt-4 px-2">
            <div class="flex-1 flex flex-col items-center gap-2 group cursor-pointer" v-for="(day, idx) in callVolume7d" :key="idx">
              <div class="w-full relative flex justify-center items-end" style="height: 100%;">
                <div class="text-[10px] font-mono text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity absolute -top-5">{{ day.count }} calls</div>
                <div class="w-full bg-primary/20 rounded-t-sm group-hover:bg-primary transition-all duration-300 group-hover:shadow-[0_0_15px_hsl(var(--primary)/0.6)]" :style="`height: ${day.percentage}%;`"></div>
              </div>
              <span class="text-[10px] font-mono text-muted-foreground group-hover:text-primary transition-colors">{{ day.label }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Tenant Distribution by Niche -->
      <div class="rounded-xl glass-panel text-card-foreground flex flex-col justify-between">
        <div class="flex flex-col space-y-1.5 p-6 pb-2">
          <h3 class="font-semibold leading-none tracking-tight">Tenant Distribution</h3>
          <p class="text-xs text-muted-foreground">Active business personas by vertical</p>
        </div>
        <div class="p-6 pt-0 flex flex-col gap-4">
          <div class="space-y-3">
            <div v-for="item in nicheDistribution" :key="item.niche" class="flex items-center justify-between text-xs">
              <div class="flex items-center gap-2 font-medium text-foreground">
                <div class="w-2.5 h-2.5 rounded-full" :style="{ backgroundColor: item.color }"></div>
                {{ item.niche }}
              </div>
              <div class="flex items-center gap-2 font-mono">
                <span class="text-muted-foreground">{{ item.count }} tenants</span>
                <span class="font-semibold text-foreground bg-muted px-1.5 py-0.5 rounded">{{ item.percentage }}%</span>
              </div>
            </div>
          </div>

          <!-- Distribution Visual Bar -->
          <div class="h-2 w-full bg-muted rounded-full overflow-hidden flex">
            <div v-for="item in nicheDistribution" :key="'bar-' + item.niche" 
                 :style="{ width: item.percentage + '%', backgroundColor: item.color }"
                 class="h-full transition-all duration-500"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Live Calls & Alerts Row -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
      <!-- Live Calls -->
      <div class="rounded-xl glass-panel text-card-foreground flex flex-col relative overflow-hidden">
        <div class="flex flex-row items-center justify-between p-6 pb-4 relative z-10">
          <div class="flex flex-col space-y-1">
            <h3 class="font-semibold leading-none tracking-tight">Live Calls Now</h3>
            <p class="text-xs text-muted-foreground">Active WebRTC and SIP telephony connections</p>
          </div>
          <div class="inline-flex items-center gap-2 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-500 border border-emerald-500/20 shadow-[0_0_10px_rgba(16,185,129,0.15)]">
            <span class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse shadow-[0_0_5px_rgba(16,185,129,0.8)]"></span>
            LIVE
          </div>
        </div>
        <div class="p-6 pt-0 flex-1 relative z-10">
          <div v-if="liveCalls.length === 0" class="flex flex-col items-center justify-center h-40 text-muted-foreground border-2 border-dashed border-border/50 rounded-xl bg-muted/10">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="mb-2 opacity-20"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg>
            <span class="text-xs font-mono">No active calls in progress. Waiting for live telemetry...</span>
          </div>
          
          <div v-else class="space-y-3">
            <div v-for="call in liveCalls" :key="call.call_id" class="flex items-center gap-4 p-3 rounded-lg border border-white/5 bg-background/50 hover:bg-background/80 transition-colors shadow-sm">
              <div class="w-2 h-2 bg-emerald-500 rounded-full animate-pulse shadow-[0_0_8px_rgba(16,185,129,0.8)]"></div>
              <div class="flex-1 min-w-0">
                <div class="text-xs font-semibold text-foreground truncate">{{ call.tenant_id }}</div>
                <div class="text-[11px] text-muted-foreground truncate font-mono">{{ call.event_type }}</div>
              </div>
              <div class="text-[10px] font-mono font-bold text-primary bg-primary/10 border border-primary/20 px-2 py-1 rounded-sm shadow-[0_0_8px_hsl(var(--primary)/0.2)]">Active</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Real-time Alerts -->
      <div class="rounded-xl glass-panel text-card-foreground flex flex-col relative">
        <div class="flex flex-col space-y-1.5 p-6 pb-4 relative z-10">
          <h3 class="font-semibold leading-none tracking-tight">System & Telemetry Alerts</h3>
          <p class="text-xs text-muted-foreground">Actionable health signals and tenant milestones</p>
        </div>
        <div class="p-6 pt-0 flex-1 relative z-10">
          <div v-if="systemAlerts.length === 0" class="text-center text-xs text-muted-foreground py-8">
            All system parameters operational. 0 active alerts.
          </div>
          <div v-else class="space-y-3">
            <div v-for="alert in systemAlerts" :key="alert.id"
                 :class="alert.type === 'warning' ? 'border-l-rose-500 bg-rose-500/5' : 'border-l-primary bg-primary/5'"
                 class="flex items-start gap-4 p-3 rounded-lg border-l-2 hover:bg-background/60 transition-colors border border-border/40 shadow-sm">
              <div :class="alert.type === 'warning' ? 'bg-rose-500/10 text-rose-500' : 'bg-primary/10 text-primary'"
                   class="w-8 h-8 rounded-full flex items-center justify-center shrink-0 mt-0.5">
                <svg v-if="alert.type === 'warning'" xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
                <svg v-else xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>
              </div>
              <div class="flex-1 min-w-0">
                <div class="text-xs font-semibold text-foreground">{{ alert.title }}</div>
                <div class="text-[11px] text-muted-foreground mt-0.5">{{ alert.message }}</div>
              </div>
              <div class="text-[10px] text-muted-foreground whitespace-nowrap font-mono">{{ alert.time_ago }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import api from '../services/api';

const loading = ref(false);
const rawData = ref({});
const animatedCalls = ref("0");
const animatedTenants = ref("0");
const animatedRevenue = ref("0");
const animatedMargin = ref("0");
const animatedCost = ref("0");

const callVolume7d = ref([
  { day: 'D-6', label: 'Mon', count: 12, percentage: 35 },
  { day: 'D-5', label: 'Tue', count: 24, percentage: 55 },
  { day: 'D-4', label: 'Wed', count: 18, percentage: 40 },
  { day: 'D-3', label: 'Thu', count: 32, percentage: 70 },
  { day: 'D-2', label: 'Fri', count: 28, percentage: 60 },
  { day: 'D-1', label: 'Sat', count: 45, percentage: 90 },
  { day: 'Today', label: 'Sun', count: 38, percentage: 80 }
]);

const nicheDistribution = ref([
  { niche: 'Real Estate', count: 4, percentage: 50, color: 'hsl(var(--primary))' },
  { niche: 'Car Rental', count: 2, percentage: 25, color: 'hsl(var(--accent))' },
  { niche: 'Legal & Intake', count: 2, percentage: 25, color: '#06B6D4' }
]);

const systemAlerts = ref([]);
const liveCalls = ref([]);
let ws = null;

const connectTelemetry = () => {
  const wsUrl = window.location.origin.replace(/^http/, 'ws') + '/api/super/telemetry/ws';
  ws = new WebSocket(`${wsUrl}?token=super_admin_token`);
  
  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      if (data.call_id) {
        liveCalls.value.unshift(data);
        if (liveCalls.value.length > 5) {
          liveCalls.value.pop();
        }
      }
    } catch(e) {}
  };
  
  ws.onclose = () => {
    setTimeout(connectTelemetry, 5000);
  };
};

const animateValue = (refObj, start, end, duration) => {
  let startTs = null;
  const step = (ts) => {
    if (!startTs) startTs = ts;
    const progress = Math.min((ts - startTs) / duration, 1);
    const ease = 1 - Math.pow(1 - progress, 3);
    const current = Math.floor(start + (end - start) * ease);
    refObj.value = current.toLocaleString();
    if (progress < 1) requestAnimationFrame(step);
  };
  requestAnimationFrame(step);
};

const loadStats = async () => {
  loading.value = true;
  try {
    const res = await api.get('/api/super/dashboard/stats');
    const data = res.data || {};
    rawData.value = data;
    
    animateValue(animatedTenants, 0, data.active_tenants || 0, 800);
    animateValue(animatedCalls, 0, data.total_calls || 0, 1200);
    animateValue(animatedRevenue, 0, data.total_revenue || 0, 900);
    animateValue(animatedMargin, 0, data.gross_margin || 0, 1000);
    animatedCost.value = (data.total_cost || 0).toFixed(2);

    if (data.call_volume_7d && data.call_volume_7d.length > 0) {
      callVolume7d.value = data.call_volume_7d;
    }

    if (data.niche_distribution && data.niche_distribution.length > 0) {
      nicheDistribution.value = data.niche_distribution;
    }

    if (data.alerts) {
      systemAlerts.value = data.alerts;
    }
  } catch (e) {
    console.warn('Could not fetch dashboard stats:', e);
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  loadStats();
  connectTelemetry();
});

onUnmounted(() => {
  if (ws) ws.close();
});
</script>

