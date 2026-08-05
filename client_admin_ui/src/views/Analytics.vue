<template>
  <div class="space-y-6">
    <div class="grid grid-cols-2 gap-6">
      
      <!-- Chart 1: Call Outcomes -->
      <div class="glass-panel p-6 h-[400px]">
        <h3 class="text-white font-medium mb-6">Call Outcomes</h3>
        <div class="h-64 flex items-center justify-center relative">
          <!-- Mocking a donut chart using Chart.js or just SVG if preferred. We'll use Chart.js Doughnut -->
          <Doughnut :data="doughnutData" :options="doughnutOptions" />
          <div class="absolute inset-0 flex flex-col items-center justify-center pointer-events-none mt-2">
            <span class="text-3xl font-bold text-white">42%</span>
            <span class="text-xs text-clientMuted">Converted</span>
          </div>
        </div>
      </div>

      <!-- Chart 2: Lead Scores -->
      <div class="glass-panel p-6 h-[400px]">
        <h3 class="text-white font-medium mb-6">Average Lead Score by Week</h3>
        <div class="h-72">
          <Bar :data="barData" :options="barOptions" />
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { Doughnut, Bar } from 'vue-chartjs';
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
  Title
} from 'chart.js';

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, Title);

const doughnutData = ref({
  labels: ['Booked Viewing', 'Not Interested', 'Voicemail', 'Follow Up Needed'],
  datasets: [
    {
      data: [42, 15, 25, 18],
      backgroundColor: ['#34d399', '#ef4444', '#94a3b8', '#fbbf24'],
      borderWidth: 0,
      cutout: '80%'
    }
  ]
});

const doughnutOptions = ref({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom',
      labels: {
        color: '#94a3b8',
        padding: 20,
        usePointStyle: true,
        pointStyle: 'circle'
      }
    }
  }
});

const barData = ref({
  labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
  datasets: [
    {
      label: 'Avg Score',
      data: [4.2, 5.8, 7.1, 8.4],
      backgroundColor: 'rgba(99, 102, 241, 0.8)',
      borderRadius: 4
    }
  ]
});

const barOptions = ref({
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    y: {
      beginAtZero: true,
      max: 10,
      grid: {
        color: 'rgba(255, 255, 255, 0.05)',
      },
      ticks: { color: 'rgba(255, 255, 255, 0.5)' }
    },
    x: {
      grid: { display: false },
      ticks: { color: 'rgba(255, 255, 255, 0.5)' }
    }
  },
  plugins: {
    legend: { display: false }
  }
});
</script>
