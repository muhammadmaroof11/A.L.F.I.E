<template>
  <div class="space-y-6">
    <!-- Top Stats -->
    <div class="grid grid-cols-3 gap-6">
      <div class="glass-panel p-6">
        <h3 class="text-clientMuted text-sm font-medium mb-1">Active Leads</h3>
        <div class="text-3xl font-bold text-white mb-2">24</div>
        <div class="flex items-center text-emerald-400 text-sm font-medium">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="mr-1"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline><polyline points="17 6 23 6 23 12"></polyline></svg>
          12% from last week
        </div>
      </div>
      <div class="glass-panel p-6">
        <h3 class="text-clientMuted text-sm font-medium mb-1">Calls Handled</h3>
        <div class="text-3xl font-bold text-white mb-2">142</div>
        <div class="flex items-center text-emerald-400 text-sm font-medium">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="mr-1"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline><polyline points="17 6 23 6 23 12"></polyline></svg>
          4% from last week
        </div>
      </div>
      <div class="glass-panel p-6 relative overflow-hidden group cursor-pointer">
        <div class="absolute inset-0 bg-gradient-to-br from-clientPrimary/20 to-purple-500/20 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
        <div class="relative z-10">
          <h3 class="text-clientMuted text-sm font-medium mb-1">Conversion Rate</h3>
          <div class="text-3xl font-bold text-white mb-2">18.5%</div>
          <div class="text-clientMuted text-sm font-medium">Lead to Appointment</div>
        </div>
      </div>
    </div>

    <!-- Main Chart Area -->
    <div class="glass-panel p-6 h-[400px]">
      <h3 class="text-white font-medium mb-6">Call Volume Overview</h3>
      <div class="h-72">
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

const chartData = ref({
  labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
  datasets: [
    {
      label: 'Calls',
      data: [12, 19, 15, 25, 22, 10, 8],
      borderColor: '#6366f1',
      backgroundColor: 'rgba(99, 102, 241, 0.2)',
      fill: true,
      tension: 0.4,
      pointBackgroundColor: '#fff',
      pointBorderColor: '#6366f1',
      pointBorderWidth: 2,
      pointRadius: 4,
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
        color: 'rgba(255, 255, 255, 0.05)',
      },
      ticks: {
        color: 'rgba(255, 255, 255, 0.5)'
      }
    },
    x: {
      grid: {
        display: false
      },
      ticks: {
        color: 'rgba(255, 255, 255, 0.5)'
      }
    }
  },
  plugins: {
    legend: {
      display: false
    },
    tooltip: {
      backgroundColor: 'rgba(15, 23, 42, 0.9)',
      titleColor: '#fff',
      bodyColor: '#fff',
      borderColor: 'rgba(255, 255, 255, 0.1)',
      borderWidth: 1,
      padding: 12,
      displayColors: false,
    }
  }
});
</script>
