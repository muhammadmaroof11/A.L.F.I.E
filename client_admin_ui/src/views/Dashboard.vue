<template>
  <div class="space-y-6">
    <!-- Top Stats -->
    <div class="grid grid-cols-3 gap-6">
      <div class="glass-elevated rounded-2xl p-6 border border-border group hover:bg-surface/50 transition-colors">
        <h3 class="text-textSecondary text-xs font-bold uppercase tracking-wider mb-2">Active Leads</h3>
        <div class="text-4xl font-display font-bold text-white mb-3">24</div>
        <div class="flex items-center text-accentSecondary text-xs font-medium bg-accentSecondary/10 px-2 py-1 rounded w-fit">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="mr-1"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline><polyline points="17 6 23 6 23 12"></polyline></svg>
          12% from last week
        </div>
      </div>
      <div class="glass-elevated rounded-2xl p-6 border border-border group hover:bg-surface/50 transition-colors">
        <h3 class="text-textSecondary text-xs font-bold uppercase tracking-wider mb-2">Calls Handled</h3>
        <div class="text-4xl font-display font-bold text-white mb-3">142</div>
        <div class="flex items-center text-accentSecondary text-xs font-medium bg-accentSecondary/10 px-2 py-1 rounded w-fit">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="mr-1"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline><polyline points="17 6 23 6 23 12"></polyline></svg>
          4% from last week
        </div>
      </div>
      <div class="glass-elevated rounded-2xl p-6 border border-border relative overflow-hidden group cursor-pointer hover:bg-surface/50 transition-colors">
        <div class="absolute inset-0 bg-gradient-accent opacity-0 group-hover:opacity-10 transition-opacity duration-500"></div>
        <div class="relative z-10">
          <h3 class="text-textSecondary text-xs font-bold uppercase tracking-wider mb-2">Conversion Rate</h3>
          <div class="text-4xl font-display font-bold text-white mb-3">18.5%</div>
          <div class="text-textMuted text-xs font-medium">Lead to Appointment</div>
        </div>
      </div>
    </div>

    <!-- Main Chart Area -->
    <div class="glass-elevated rounded-2xl p-6 h-[400px] border border-border flex flex-col">
      <h3 class="text-white font-display font-bold text-lg mb-6">Call Volume Overview</h3>
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

const chartData = ref({
  labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
  datasets: [
    {
      label: 'Calls',
      data: [12, 19, 15, 25, 22, 10, 8],
      borderColor: '#14b8a6', // accent
      backgroundColor: 'rgba(20, 184, 166, 0.1)',
      fill: true,
      tension: 0.4,
      pointBackgroundColor: '#070a0f',
      pointBorderColor: '#14b8a6',
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
        color: 'rgba(255, 255, 255, 0.05)',
        drawBorder: false
      },
      ticks: {
        color: 'rgba(240, 244, 248, 0.4)',
        font: { family: 'Fira Code', size: 11 },
        padding: 10
      }
    },
    x: {
      grid: {
        display: false,
        drawBorder: false
      },
      ticks: {
        color: 'rgba(240, 244, 248, 0.4)',
        font: { family: 'Fira Code', size: 11 },
        padding: 10
      }
    }
  },
  plugins: {
    legend: {
      display: false
    },
    tooltip: {
      backgroundColor: 'rgba(255, 255, 255, 0.03)',
      titleColor: '#fff',
      bodyColor: 'rgba(240, 244, 248, 0.65)',
      borderColor: 'rgba(255, 255, 255, 0.08)',
      borderWidth: 1,
      padding: 12,
      displayColors: false,
      titleFont: { family: 'Outfit', size: 13, weight: 'bold' }
    }
  }
});
</script>
