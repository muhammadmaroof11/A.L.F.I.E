<template>
  <div class="h-full flex flex-col gap-6">
    <div class="flex items-center justify-between flex-shrink-0">
      <div>
        <h2 class="text-3xl font-display font-bold text-foreground mb-1">Global Fleet Telemetry</h2>
        <p class="text-xs text-muted-foreground">Real-time system health, concurrent connections, and capacity overview</p>
      </div>
      <button @click="fetchMetrics" class="flex items-center gap-2 px-3 py-1.5 glass rounded-lg text-xs text-muted-foreground hover:text-foreground transition-colors">
        <svg :class="{ 'animate-spin': loading }" class="h-3.5 w-3.5 text-primary" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
        Live Sync Active
      </button>
    </div>

    <!-- Bento Grid -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      
      <div class="glass-elevated rounded-2xl p-6 flex flex-col justify-between group hover:-translate-y-1 transition-transform duration-300">
        <div class="flex justify-between items-start mb-4">
          <div class="p-3 bg-primary/10 text-primary rounded-xl">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg>
          </div>
          <span class="text-xs font-medium text-emerald-400 bg-emerald-500/10 px-2 py-1 rounded-full">{{ metrics.total_calls || 0 }} total calls</span>
        </div>
        <div>
          <div class="text-4xl font-display font-bold text-foreground mb-1 font-mono">{{ metrics.active_tenants || 0 }}</div>
          <div class="text-xs font-medium text-muted-foreground uppercase tracking-wider">Active Client Tenants</div>
        </div>
      </div>

      <div class="glass-elevated rounded-2xl p-6 flex flex-col justify-between group hover:-translate-y-1 transition-transform duration-300">
        <div class="flex justify-between items-start mb-4">
          <div class="p-3 bg-accent/10 text-accent rounded-xl">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>
          </div>
          <span class="text-xs font-medium text-emerald-400 bg-emerald-500/10 px-2 py-1 rounded-full font-mono">P95 ~520ms</span>
        </div>
        <div>
          <div class="text-4xl font-display font-bold text-foreground mb-1 font-mono">390<span class="text-lg text-muted-foreground ml-1">ms</span></div>
          <div class="text-xs font-medium text-muted-foreground uppercase tracking-wider">Median Voice Latency</div>
        </div>
      </div>

      <div class="glass-elevated rounded-2xl p-6 flex flex-col justify-between group hover:-translate-y-1 transition-transform duration-300">
        <div class="flex justify-between items-start mb-4">
          <div class="p-3 bg-amber-500/10 text-amber-500 rounded-xl">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="2" width="20" height="8" rx="2" ry="2"></rect><rect x="2" y="14" width="20" height="8" rx="2" ry="2"></rect><line x1="6" y1="6" x2="6.01" y2="6"></line><line x1="6" y1="18" x2="6.01" y2="18"></line></svg>
          </div>
          <span class="text-xs font-medium text-primary bg-primary/10 px-2 py-1 rounded-full font-mono">{{ metrics.total_agents || 0 }} provisioned</span>
        </div>
        <div>
          <div class="text-4xl font-display font-bold text-foreground mb-1 font-mono">${{ (metrics.total_revenue || 0).toFixed(0) }}</div>
          <div class="text-xs font-medium text-muted-foreground uppercase tracking-wider">Gross Platform Run Rate</div>
        </div>
      </div>

    </div>
    
    <!-- System Diagram -->
    <div class="glass rounded-2xl p-6 flex-1 relative overflow-hidden group">
      <div class="relative z-10 h-full flex flex-col">
        <h3 class="text-sm font-semibold text-foreground mb-6 uppercase tracking-wider">Core Cluster Services</h3>
        
        <div class="flex-1 flex items-center justify-center gap-12">
          
          <div class="flex flex-col gap-4">
            <div class="glass-elevated px-6 py-4 rounded-xl flex items-center gap-4 w-64 border-l-4 border-primary">
              <div class="w-3 h-3 rounded-full bg-primary animate-pulse"></div>
              <div>
                <div class="text-xs font-medium text-foreground">Traefik Ingress</div>
                <div class="text-[11px] font-mono text-muted-foreground">99.99% Uptime · SSL</div>
              </div>
            </div>
          </div>
          
          <div class="w-16 h-0.5 bg-border relative">
            <div class="absolute w-2 h-2 bg-primary rounded-full -top-[3px] animate-ping"></div>
          </div>
          
          <div class="flex flex-col gap-4">
            <div class="glass-elevated px-6 py-4 rounded-xl flex items-center gap-4 w-64 border-l-4 border-emerald-500">
              <div class="w-3 h-3 rounded-full bg-emerald-500 animate-pulse"></div>
              <div>
                <div class="text-xs font-medium text-foreground">LiveKit Voice Engine</div>
                <div class="text-[11px] font-mono text-muted-foreground">SIP & WebRTC Cluster</div>
              </div>
            </div>
            
            <div class="glass-elevated px-6 py-4 rounded-xl flex items-center gap-4 w-64 border-l-4 border-accent">
              <div class="w-3 h-3 rounded-full bg-accent"></div>
              <div>
                <div class="text-xs font-medium text-foreground">Redis Semantic Cache</div>
                <div class="text-[11px] font-mono text-muted-foreground">Sub-5ms TTFT Warm</div>
              </div>
            </div>
          </div>

          <div class="w-16 h-0.5 bg-border relative"></div>

          <div class="flex flex-col gap-4">
            <div class="glass-elevated px-6 py-4 rounded-xl flex items-center gap-4 w-64 border-l-4 border-amber-500">
              <div class="w-3 h-3 rounded-full bg-amber-500"></div>
              <div>
                <div class="text-xs font-medium text-foreground">PostgreSQL Multi-Tenant</div>
                <div class="text-[11px] font-mono text-muted-foreground">AsyncPG Pool: 2-20 Conns</div>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '../services/api';

const loading = ref(false);
const metrics = ref({});

const fetchMetrics = async () => {
  loading.value = true;
  try {
    const res = await api.get('/api/super/dashboard/stats');
    metrics.value = res.data || {};
  } catch (err) {
    console.error("Failed to load metrics:", err);
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchMetrics();
});
</script>

