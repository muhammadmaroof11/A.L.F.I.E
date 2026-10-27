<template>
  <div class="space-y-6">
    <!-- Top Stats -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
      <div class="glass-panel group hover-glow p-6 flex flex-col justify-between rounded-xl relative overflow-hidden">
        <div class="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
        <div class="relative">
          <h3 class="text-sm font-medium text-muted-foreground mb-1 group-hover:text-primary transition-colors">Total Call Minutes</h3>
          <div class="text-3xl font-bold text-foreground">{{ totalDuration }}</div>
        </div>
      </div>
      
      <div class="glass-panel group hover-glow p-6 flex flex-col justify-between rounded-xl relative overflow-hidden">
        <div class="absolute inset-0 bg-gradient-to-br from-emerald-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
        <div class="relative">
          <h3 class="text-sm font-medium text-muted-foreground mb-1 group-hover:text-emerald-500 transition-colors">Calls Handled</h3>
          <div class="text-3xl font-bold text-foreground">{{ totalCalls }}</div>
        </div>
      </div>
      
      <div class="glass-panel group hover-glow p-6 flex flex-col justify-between rounded-xl relative overflow-hidden">
        <div class="absolute inset-0 bg-gradient-to-br from-amber-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
        <div class="relative">
          <h3 class="text-sm font-medium text-muted-foreground mb-1 group-hover:text-amber-500 transition-colors">Credits Consumed</h3>
          <div class="text-3xl font-bold text-foreground">${{ totalCost.toFixed(2) }}</div>
          <div class="text-xs text-muted-foreground mt-1">This cycle</div>
        </div>
      </div>

      <!-- Triage Metric Card -->
      <div class="glass-panel group hover-glow p-6 flex flex-col justify-between rounded-xl relative overflow-hidden">
        <div class="absolute inset-0 bg-gradient-to-br from-rose-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
        <div class="relative">
          <h3 class="text-sm font-medium text-muted-foreground mb-1 group-hover:text-rose-400 transition-colors">Lost Revenue Triage</h3>
          <div class="text-3xl font-bold" :class="triageData.total_at_risk > 0 ? 'text-rose-400' : 'text-foreground'">{{ triageData.total_at_risk }}</div>
          <div class="text-xs text-muted-foreground mt-1">{{ triageData.critical_risk_count }} critical · {{ triageData.lost_opportunity_count }} lost</div>
        </div>
      </div>
    </div>

    <!-- Lost Revenue Triage & Recovery Widget -->
    <div class="glass-panel p-6 rounded-xl border border-border/60 relative overflow-hidden">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
        <div>
          <div class="flex items-center gap-2">
            <h3 class="text-base font-bold text-foreground">Lost Revenue Triage & Recovery</h3>
            <span v-if="triageData.total_at_risk > 0" class="text-xs font-mono font-semibold bg-rose-500/15 text-rose-400 border border-rose-500/30 px-2 py-0.5 rounded-full animate-pulse">
              {{ triageData.total_at_risk }} Attention Required
            </span>
            <span v-else class="text-xs font-mono bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 px-2 py-0.5 rounded-full">
              Pipeline Healthy
            </span>
          </div>
          <p class="text-xs text-muted-foreground mt-0.5">Calls flagged by automated LLM QA scoring with high dissatisfaction risk or lost opportunities requiring outreach.</p>
        </div>
        <button 
          @click="router.push('/interactions')"
          class="text-xs text-primary hover:underline flex items-center gap-1 font-medium whitespace-nowrap"
        >
          <span>View All Interactions</span>
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"></polyline></svg>
        </button>
      </div>

      <!-- Triage Items List -->
      <div v-if="triageData.triage_calls && triageData.triage_calls.length > 0" class="space-y-3">
        <div 
          v-for="call in triageData.triage_calls.slice(0, 3)" 
          :key="call.id"
          class="p-3.5 rounded-lg bg-background/50 border border-border/50 hover:border-primary/40 transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-3"
        >
          <div class="space-y-1">
            <div class="flex items-center gap-2">
              <span class="font-semibold text-xs text-foreground">{{ call.caller }}</span>
              <span 
                :class="call.risk_flag ? 'bg-rose-500/15 text-rose-400 border-rose-500/30' : 'bg-amber-500/15 text-amber-400 border-amber-500/30'"
                class="text-[10px] font-medium px-2 py-0.5 rounded-full border uppercase"
              >
                {{ call.risk_flag ? 'Critical Risk' : 'Lost Opportunity' }}
              </span>
              <span class="text-[10px] font-mono text-muted-foreground">{{ call.date }}</span>
            </div>
            <p class="text-xs text-muted-foreground">{{ call.risk_reason || 'Caller showed signs of dissatisfaction or abandoned booking.' }}</p>
          </div>
          <div class="flex items-center gap-2 flex-shrink-0">
            <button 
              @click="router.push(`/interactions?search=${encodeURIComponent(call.caller)}`)"
              class="px-3 py-1.5 rounded-lg bg-primary/10 hover:bg-primary/20 text-primary text-xs font-medium border border-primary/20 transition-colors"
            >
              Review Audio
            </button>
            <button 
              @click="scheduleCallback(call)"
              class="px-3 py-1.5 rounded-lg bg-background border border-border hover:bg-muted text-xs font-medium text-foreground transition-colors"
            >
              Recover Lead
            </button>
          </div>
        </div>
      </div>
      <div v-else class="p-6 rounded-lg bg-background/30 border border-border/30 text-center">
        <div class="w-8 h-8 rounded-full bg-emerald-500/10 text-emerald-400 mx-auto flex items-center justify-center mb-2">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg>
        </div>
        <p class="text-xs font-medium text-foreground">Pipeline In Good Standing</p>
        <p class="text-[11px] text-muted-foreground mt-0.5">No critical risks or unrecovered lost opportunities detected across your call flows.</p>
      </div>
    </div>

    <!-- Main Chart Area -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div class="glass-panel group p-6 h-[400px] flex flex-col rounded-xl relative overflow-hidden">
        <div class="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
        <h3 class="text-lg font-semibold mb-6 relative">Call Volume Overview</h3>
        <div class="flex-1 w-full h-full relative">
          <Line :data="chartData" :options="chartOptions" />
        </div>
      </div>

      <div class="glass-panel group p-6 h-[400px] flex flex-col rounded-xl relative overflow-hidden">
        <div class="absolute inset-0 bg-gradient-to-br from-emerald-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
        <h3 class="text-lg font-semibold mb-6 relative">Per-Agent Analytics</h3>
        <div class="flex-1 w-full h-full relative" v-if="agentChartData.labels.length > 0">
          <Bar :data="agentChartData" :options="agentChartOptions" />
        </div>
        <div v-else class="flex-1 w-full h-full flex items-center justify-center text-muted-foreground">
          No agent data available yet.
        </div>
      </div>
    </div>

    <!-- System Telemetry Status Bar (Centered & Equally Spaced) -->
    <div class="glass-panel p-5 rounded-xl border border-border/60 relative overflow-hidden">
      <h3 class="text-xs font-mono font-bold uppercase tracking-wider text-muted-foreground mb-4">
        System Telemetry Status
      </h3>
      <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4 items-center justify-items-center text-center">
        <div class="flex items-center gap-2.5">
          <span class="relative flex h-2 w-2">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span class="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
          </span>
          <div class="text-left">
            <div class="text-xs font-semibold text-foreground">AI Agent</div>
            <div class="text-[10px] text-emerald-500 font-mono">Active</div>
          </div>
        </div>

        <div class="flex items-center gap-2.5">
          <span class="relative flex h-2 w-2">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span class="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
          </span>
          <div class="text-left">
            <div class="text-xs font-semibold text-foreground">OpenAI</div>
            <div class="text-[10px] text-emerald-500 font-mono">Active</div>
          </div>
        </div>

        <div class="flex items-center gap-2.5">
          <span class="relative flex h-2 w-2">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span class="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
          </span>
          <div class="text-left">
            <div class="text-xs font-semibold text-foreground">VAPI Core</div>
            <div class="text-[10px] text-emerald-500 font-mono">Active</div>
          </div>
        </div>

        <div class="flex items-center gap-2.5">
          <span class="relative flex h-2 w-2">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span class="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
          </span>
          <div class="text-left">
            <div class="text-xs font-semibold text-foreground">Database</div>
            <div class="text-[10px] text-emerald-500 font-mono">Active</div>
          </div>
        </div>

        <div class="flex items-center gap-2.5">
          <span class="relative flex h-2 w-2">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span class="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
          </span>
          <div class="text-left">
            <div class="text-xs font-semibold text-foreground">WebSocket</div>
            <div class="text-[10px] text-emerald-500 font-mono">Active</div>
          </div>
        </div>

        <div class="flex items-center gap-2.5">
          <span class="relative flex h-2 w-2">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span class="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
          </span>
          <div class="text-left">
            <div class="text-xs font-semibold text-foreground">Webhooks</div>
            <div class="text-[10px] text-emerald-500 font-mono">Active</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { Line, Bar } from 'vue-chartjs';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Filler,
  Legend
} from 'chart.js';
import api from '../services/api';
import { useAuthStore } from '../stores/auth';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Filler,
  Legend
);

const router = useRouter();
const auth = useAuthStore();
const totalCalls = ref(0);
const totalDuration = ref(0);
const totalCost = ref(0);

const triageData = ref({
  total_at_risk: 0,
  critical_risk_count: 0,
  lost_opportunity_count: 0,
  triage_calls: []
});

const scheduleCallback = (call) => {
  router.push(`/callbacks?caller=${encodeURIComponent(call.caller)}`);
};

// We simulate a primary color var equivalent in JS for the chart
const chartData = ref({
  labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
  datasets: [
    {
      label: 'Calls',
      data: [12, 19, 15, 25, 22, 10, 8],
      borderColor: 'hsl(217.2 91.2% 59.8%)', // primary
      backgroundColor: 'hsla(217.2, 91.2%, 59.8%, 0.1)',
      fill: true,
      tension: 0.4,
      pointBackgroundColor: 'hsl(222.2 84% 4.9%)', // card bg
      pointBorderColor: 'hsl(217.2 91.2% 59.8%)',
      pointBorderWidth: 2,
      pointRadius: 4,
      pointHoverRadius: 6,
    }
  ]
});

const chartOptions = ref({
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    y: {
      beginAtZero: true,
      grid: {
        color: 'hsla(217.2, 32.6%, 17.5%, 0.5)', // border color
        drawBorder: false
      },
      ticks: {
        color: 'hsl(215 20.2% 65.1%)', // muted-foreground
        font: { family: 'Inter', size: 11 },
        padding: 10
      }
    },
    x: {
      grid: {
        display: false,
        drawBorder: false
      },
      ticks: {
        color: 'hsl(215 20.2% 65.1%)',
        font: { family: 'Inter', size: 11 },
        padding: 10
      }
    }
  },
  plugins: {
    legend: {
      display: false
    },
    tooltip: {
      backgroundColor: 'hsl(222.2 84% 4.9%)',
      borderColor: 'hsl(217.2 32.6% 17.5%)',
      borderWidth: 1,
      padding: 12,
      displayColors: false,
      titleFont: { family: 'Inter', size: 13, weight: 'bold' }
    }
  }
});

const agentChartData = ref({
  labels: [],
  datasets: []
});

const agentChartOptions = ref({
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    y: {
      beginAtZero: true,
      grid: {
        color: 'hsla(217.2, 32.6%, 17.5%, 0.5)',
        drawBorder: false
      },
      ticks: {
        color: 'hsl(215 20.2% 65.1%)',
        font: { family: 'Inter', size: 11 },
        padding: 10
      }
    },
    x: {
      grid: {
        display: false,
        drawBorder: false
      },
      ticks: {
        color: 'hsl(215 20.2% 65.1%)',
        font: { family: 'Inter', size: 11 },
        padding: 10
      }
    }
  },
  plugins: {
    legend: {
      display: false
    },
    tooltip: {
      backgroundColor: 'hsl(222.2 84% 4.9%)',
      borderColor: 'hsl(217.2 32.6% 17.5%)',
      borderWidth: 1,
      padding: 12,
      displayColors: false,
      titleFont: { family: 'Inter', size: 13, weight: 'bold' }
    }
  }
});

onMounted(async () => {
  try {
    const tenantId = auth.tenantId || localStorage.getItem('alfie_tenant_id');
    const res = await api.get('/api/client/metrics', { params: { tenant_id: tenantId } });
    totalCalls.value = res.data.total_calls || 0;
    totalDuration.value = Math.round((res.data.total_duration || 0) / 60);
    totalCost.value = res.data.total_credits || 0;

    if (res.data.weekly_volume) {
      chartData.value = {
        labels: res.data.weekly_volume.labels || ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        datasets: [
          {
            label: 'Calls',
            data: res.data.weekly_volume.data || [0, 0, 0, 0, 0, 0, 0],
            borderColor: 'hsl(217.2 91.2% 59.8%)',
            backgroundColor: 'hsla(217.2, 91.2%, 59.8%, 0.1)',
            fill: true,
            tension: 0.4,
            pointBackgroundColor: 'hsl(222.2 84% 4.9%)',
            pointBorderColor: 'hsl(217.2 91.2% 59.8%)',
            pointBorderWidth: 2,
            pointRadius: 4,
            pointHoverRadius: 6,
          }
        ]
      };
    }

    if (res.data.agents && res.data.agents.length > 0) {
      agentChartData.value = {
        labels: res.data.agents.map(a => a.agent_name),
        datasets: [{
          label: 'Calls Handled',
          data: res.data.agents.map(a => a.calls),
          backgroundColor: 'hsla(142.1, 76.2%, 36.3%, 0.8)',
          borderColor: 'hsl(142.1 76.2% 36.3%)',
          borderWidth: 1,
          borderRadius: 4
        }]
      };
    }

    // Fetch Lost Revenue Triage data
    try {
      const triageRes = await api.get('/api/client/qa/triage', { params: { tenant_id: tenantId } });
      if (triageRes.data) {
        triageData.value = triageRes.data;
      }
    } catch (err) {
      console.warn("Could not fetch triage metrics:", err);
    }
  } catch (e) {
    console.error("Failed to fetch dashboard metrics", e);
  }
});
</script>
