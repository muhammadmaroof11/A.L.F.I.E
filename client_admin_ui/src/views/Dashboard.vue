<template>
  <div class="space-y-6">
    <!-- Top Stats -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div class="glass-panel group hover-glow p-6 flex flex-col justify-between rounded-xl relative overflow-hidden">
        <div class="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
        <div class="relative">
          <h3 class="text-sm font-medium text-muted-foreground mb-1 group-hover:text-primary transition-colors">Active Leads</h3>
          <div class="text-3xl font-bold text-foreground">24</div>
        </div>
        <div class="mt-4 flex items-center text-xs font-medium text-primary relative">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="mr-1 drop-shadow-[0_0_5px_hsl(var(--primary))]"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline><polyline points="17 6 23 6 23 12"></polyline></svg>
          12% from last week
        </div>
      </div>
      
      <div class="glass-panel group hover-glow p-6 flex flex-col justify-between rounded-xl relative overflow-hidden">
        <div class="absolute inset-0 bg-gradient-to-br from-emerald-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
        <div class="relative">
          <h3 class="text-sm font-medium text-muted-foreground mb-1 group-hover:text-emerald-500 transition-colors">Calls Handled</h3>
          <div class="text-3xl font-bold text-foreground">142</div>
        </div>
        <div class="mt-4 flex items-center text-xs font-medium text-emerald-500 relative">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="mr-1 drop-shadow-[0_0_5px_hsl(var(--emerald-500))]"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline><polyline points="17 6 23 6 23 12"></polyline></svg>
          4% from last week
        </div>
      </div>
      
      <div class="glass-panel group hover-glow p-6 flex flex-col justify-between rounded-xl relative overflow-hidden">
        <div class="absolute inset-0 bg-gradient-to-br from-amber-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
        <div class="relative">
          <h3 class="text-sm font-medium text-muted-foreground mb-1 group-hover:text-amber-500 transition-colors">Conversion Rate</h3>
          <div class="text-3xl font-bold text-foreground">18.5%</div>
          <div class="text-xs text-muted-foreground mt-1">Lead to Appointment</div>
        </div>
      </div>
    </div>

    <!-- Main Chart Area -->
    <div class="glass-panel group p-6 h-[400px] flex flex-col rounded-xl relative overflow-hidden">
      <div class="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
      <h3 class="text-lg font-semibold mb-6 relative">Call Volume Overview</h3>
      <div class="flex-1 w-full h-full relative">
        <Line :data="chartData" :options="chartOptions" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { Line } from 'vue-chartjs';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Filler
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Filler
);

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
</script>
