<template>
  <div class="space-y-6">
    <!-- Top Stats -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
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
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
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

const auth = useAuthStore();
const totalCalls = ref(0);
const totalDuration = ref(0);
const totalCost = ref(0);

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
      titleColor: 'hsl(210 20% 98%)',
      bodyColor: 'hsl(215 20.2% 65.1%)',
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
      grid: { color: 'hsla(217.2, 32.6%, 17.5%, 0.5)', drawBorder: false },
      ticks: { color: 'hsl(215 20.2% 65.1%)', font: { family: 'Inter', size: 11 }, padding: 10 }
    },
    x: {
      grid: { display: false, drawBorder: false },
      ticks: { color: 'hsl(215 20.2% 65.1%)', font: { family: 'Inter', size: 11 }, padding: 10 }
    }
  },
  plugins: {
    legend: { display: false },
    tooltip: {
      backgroundColor: 'hsl(222.2 84% 4.9%)',
      titleColor: 'hsl(210 20% 98%)',
      bodyColor: 'hsl(215 20.2% 65.1%)',
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
  } catch (e) {
    console.error("Failed to fetch dashboard metrics", e);
  }
});
</script>
