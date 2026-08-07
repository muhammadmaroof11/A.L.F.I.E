<template>
  <div class="space-y-6">
    <!-- KPI Stats Row -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="rounded-xl glass-panel text-card-foreground hover-glow relative overflow-hidden group">
        <div class="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
        <div class="p-6 flex flex-row items-center justify-between space-y-0 pb-2 relative z-10">
          <h3 class="tracking-tight text-sm font-medium">Total Calls Today</h3>
          <div class="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-primary"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg>
          </div>
        </div>
        <div class="p-6 pt-0 relative z-10">
          <div class="text-3xl font-bold font-mono tracking-tight">{{ animatedCalls }}</div>
          <p class="text-xs text-muted-foreground mt-1 flex items-center gap-1">
            <span class="text-emerald-500 font-medium flex items-center"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 19V5M5 12l7-7 7 7"/></svg> 12.4%</span> from yesterday
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
            <span class="text-emerald-500 font-medium flex items-center"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 19V5M5 12l7-7 7 7"/></svg> 3</span> new this month
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
            <span class="text-emerald-500 font-medium flex items-center"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 19V5M5 12l7-7 7 7"/></svg> 8.1%</span> from last month
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
            <span class="text-rose-500 font-medium flex items-center"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 5v14M5 12l7 7 7-7"/></svg> ${{ animatedCost }}</span> raw operational cost
          </p>
        </div>
      </div>
    </div>

    <!-- Charts Row -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
      <div class="col-span-2 rounded-xl glass-panel text-card-foreground">
        <div class="flex flex-col space-y-1.5 p-6 pb-2">
          <h3 class="font-semibold leading-none tracking-tight">Call Volume (7 Days)</h3>
          <p class="text-sm text-muted-foreground">Aggregated across all active tenants</p>
        </div>
        <div class="p-6 pt-0">
          <div class="flex items-end gap-3 h-32 mt-4 px-2">
            <!-- Simulated Bar Chart -->
            <div class="flex-1 flex flex-col items-center gap-2 group cursor-pointer" v-for="(day, idx) in [45, 60, 35, 80, 55, 90, 75]" :key="idx">
              <div class="w-full relative flex justify-center items-end" style="height: 100%;">
                <div class="text-[10px] font-mono text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity absolute -top-5">{{ day }}%</div>
                <div class="w-full bg-primary/20 rounded-t-sm group-hover:bg-primary transition-all duration-300 group-hover:shadow-[0_0_15px_hsl(var(--primary)/0.6)]" :style="`height: ${day}%;`"></div>
              </div>
              <span class="text-[10px] font-mono text-muted-foreground group-hover:text-primary transition-colors">D-{{7-idx}}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="rounded-xl glass-panel text-card-foreground">
        <div class="flex flex-col space-y-1.5 p-6 pb-2">
          <h3 class="font-semibold leading-none tracking-tight">Tenant Distribution</h3>
          <p class="text-sm text-muted-foreground">Active personas by niche</p>
        </div>
        <div class="relative flex items-center justify-center p-4">
          <svg viewBox="0 0 120 120" class="w-24 h-24 transform -rotate-90 drop-shadow-[0_0_10px_hsl(var(--primary)/0.2)]">
            <circle cx="60" cy="60" r="50" fill="none" stroke="currentColor" stroke-width="8" class="text-muted/20" />
            <circle cx="60" cy="60" r="45" fill="none" class="stroke-primary" stroke-width="12"
              stroke-dasharray="190 314" stroke-linecap="round"/>
            <circle cx="60" cy="60" r="45" fill="none" class="stroke-accent" stroke-width="12"
              stroke-dasharray="70 314" stroke-dashoffset="-190" stroke-linecap="round"/>
            <circle cx="60" cy="60" r="45" fill="none" stroke="#06B6D4" stroke-width="12"
              stroke-dasharray="54 314" stroke-dashoffset="-260" stroke-linecap="round"/>
            <text x="-60" y="65" transform="rotate(90)" text-anchor="middle" font-size="14" font-weight="700" fill="currentColor" font-family="Inter">67%</text>
          </svg>
          <div class="space-y-3">
            <div class="flex items-center gap-2 text-xs text-foreground font-medium"><div class="w-2.5 h-2.5 rounded-full bg-primary shadow-[0_0_8px_hsl(var(--primary)/0.8)]"></div> Real Estate</div>
            <div class="flex items-center gap-2 text-xs text-foreground font-medium"><div class="w-2.5 h-2.5 rounded-full bg-accent shadow-[0_0_8px_hsl(var(--accent)/0.8)]"></div> Car Rental</div>
            <div class="flex items-center gap-2 text-xs text-foreground font-medium"><div class="w-2.5 h-2.5 rounded-full bg-muted-foreground"></div> Medical</div>
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
            <p class="text-sm text-muted-foreground">Active WebRTC connections</p>
          </div>
          <div class="inline-flex items-center gap-2 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-500 border border-emerald-500/20 shadow-[0_0_10px_rgba(16,185,129,0.15)]">
            <span class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse shadow-[0_0_5px_rgba(16,185,129,0.8)]"></span>
            LIVE
          </div>
        </div>
        <div class="p-6 pt-0 flex-1 relative z-10">
          <div v-if="liveCalls.length === 0" class="flex flex-col items-center justify-center h-40 text-muted-foreground border-2 border-dashed border-border/50 rounded-xl bg-muted/10">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="mb-2 opacity-20"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg>
            <span class="text-sm font-mono">Waiting for live call telemetry...</span>
          </div>
          
          <div v-else class="space-y-3">
            <div v-for="call in liveCalls" :key="call.call_id" class="flex items-center gap-4 p-3 rounded-lg border border-white/5 bg-background/50 hover:bg-background/80 transition-colors shadow-sm">
              <div class="w-2 h-2 bg-emerald-500 rounded-full animate-pulse shadow-[0_0_8px_rgba(16,185,129,0.8)]"></div>
              <div class="flex-1 min-w-0">
                <div class="text-sm font-semibold text-foreground truncate">{{ call.tenant_id }}</div>
                <div class="text-xs text-muted-foreground truncate font-mono">{{ call.event_type }}</div>
              </div>
              <div class="text-[10px] font-mono font-bold text-primary bg-primary/10 border border-primary/20 px-2 py-1 rounded-sm shadow-[0_0_8px_hsl(var(--primary)/0.2)]">Active</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Alerts -->
      <div class="rounded-xl glass-panel text-card-foreground flex flex-col relative">
        <div class="flex flex-col space-y-1.5 p-6 pb-4 relative z-10">
          <h3 class="font-semibold leading-none tracking-tight">System Alerts</h3>
          <p class="text-sm text-muted-foreground">Actionable items from the last 6 hours</p>
        </div>
        <div class="p-6 pt-0 flex-1 relative z-10">
          <div class="space-y-3">
            
            <div class="flex items-start gap-4 p-3 rounded-lg border-l-2 border-l-rose-500 bg-background/40 hover:bg-background/60 transition-colors border border-white/5 shadow-sm">
              <div class="w-8 h-8 rounded-full bg-rose-500/10 flex items-center justify-center shrink-0 mt-0.5 shadow-[0_0_10px_rgba(244,63,94,0.2)]">
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-rose-500"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
              </div>
              <div class="flex-1 min-w-0">
                <div class="text-sm font-semibold text-foreground">STT Latency Spike</div>
                <div class="text-xs text-muted-foreground mt-0.5">Deepgram P99 → 1840ms on tenant <code class="text-rose-400 bg-rose-400/10 px-1 py-0.5 rounded font-mono">drivefast_ae</code></div>
              </div>
              <div class="text-[10px] text-muted-foreground whitespace-nowrap font-mono">2m ago</div>
            </div>

            <div class="flex items-start gap-4 p-3 rounded-lg border-l-2 border-l-amber-500 bg-background/40 hover:bg-background/60 transition-colors border border-white/5 shadow-sm">
              <div class="w-8 h-8 rounded-full bg-amber-500/10 flex items-center justify-center shrink-0 mt-0.5 shadow-[0_0_10px_rgba(245,158,11,0.2)]">
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-amber-500"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
              </div>
              <div class="flex-1 min-w-0">
                <div class="text-sm font-semibold text-foreground">Credit Threshold</div>
                <div class="text-xs text-muted-foreground mt-0.5">HomeFinders Ltd at 87% of monthly limit</div>
              </div>
              <div class="text-[10px] text-muted-foreground whitespace-nowrap font-mono">14m ago</div>
            </div>

            <div class="flex gap-4 p-3 rounded-lg hover:bg-muted/30 transition-colors group">
              <div class="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center shrink-0 mt-0.5 shadow-[0_0_10px_hsl(var(--primary)/0.2)]">
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-primary"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>
              </div>
              <div class="flex-1 min-w-0">
                <div class="text-sm font-semibold text-foreground">New Tenant Signup</div>
                <div class="text-xs text-muted-foreground mt-0.5">PropertyBridge UAE provisioned successfully</div>
              </div>
              <div class="text-[10px] text-muted-foreground whitespace-nowrap font-mono">3h ago</div>
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

const animatedCalls = ref("0");
const animatedTenants = ref("0");
const animatedRevenue = ref("0");
const animatedMargin = ref("0");
const animatedCost = ref("0");
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
  try {
    const res = await api.get('/api/super/dashboard/stats');
    const data = res.data || {};
    
    animateValue(animatedTenants, 0, data.active_tenants || 0, 800);
    animateValue(animatedCalls, 0, data.total_calls || 0, 1200);
    animateValue(animatedRevenue, 0, data.total_revenue || 0, 900);
    animateValue(animatedMargin, 0, data.gross_margin || 0, 1000);
    
    // Convert float to string with 2 decimal places for raw cost without animation
    animatedCost.value = (data.total_cost || 0).toFixed(2);
  } catch (e) {
    console.warn('Could not fetch dashboard stats:', e);
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
