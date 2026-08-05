<template>
  <div class="space-y-6">
    <div class="grid grid-cols-2 gap-6">
      
      <!-- Chart 1: Call Outcomes -->
      <div class="glass-elevated rounded-2xl p-6 h-[400px] flex flex-col relative border border-border">
        <h3 class="text-white font-display font-bold text-lg mb-6">Call Outcomes</h3>
        <div class="flex-1 flex items-center justify-center relative w-full h-full">
          <Doughnut :data="doughnutData" :options="doughnutOptions" />
          <div class="absolute inset-0 flex flex-col items-center justify-center pointer-events-none mt-2">
            <span class="text-4xl font-display font-bold text-white drop-shadow-[0_0_10px_rgba(20,184,166,0.3)]">42%</span>
            <span class="text-xs font-mono text-textMuted uppercase tracking-widest mt-1">Converted</span>
          </div>
        </div>
      </div>

      <!-- Chart 2: Lead Scores -->
      <div class="glass-elevated rounded-2xl p-6 h-[400px] flex flex-col border border-border">
        <h3 class="text-white font-display font-bold text-lg mb-6">Average Lead Score by Week</h3>
        <div class="flex-1 w-full h-full relative">
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
      backgroundColor: ['#14b8a6', '#f43f5e', '#64748b', '#fbbf24'],
      borderColor: '#070a0f',
      borderWidth: 2,
      hoverOffset: 4,
      cutout: '75%'
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
        color: 'rgba(240, 244, 248, 0.65)',
        padding: 20,
        font: {
          family: 'Inter',
          size: 12
        },
        usePointStyle: true,
        pointStyle: 'circle'
      }
    },
    tooltip: {
      backgroundColor: 'rgba(255, 255, 255, 0.03)',
      titleColor: '#fff',
      bodyColor: 'rgba(240, 244, 248, 0.65)',
      borderColor: 'rgba(255, 255, 255, 0.08)',
      borderWidth: 1,
      padding: 12,
      boxPadding: 6,
      usePointStyle: true
    }
  }
});

const barData = ref({
  labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
  datasets: [
    {
      label: 'Avg Score',
      data: [4.2, 5.8, 7.1, 8.4],
      backgroundColor: 'rgba(20, 184, 166, 0.8)',
      hoverBackgroundColor: 'rgba(20, 184, 166, 1)',
      borderRadius: 6,
      borderSkipped: false
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
        drawBorder: false
      },
      ticks: { 
        color: 'rgba(240, 244, 248, 0.4)',
        font: { family: 'Fira Code', size: 11 },
        padding: 10
      }
    },
    x: {
      grid: { display: false, drawBorder: false },
      ticks: { 
        color: 'rgba(240, 244, 248, 0.4)',
        font: { family: 'Fira Code', size: 11 },
        padding: 10
      }
    }
  },
  plugins: {
    legend: { display: false },
    tooltip: {
      backgroundColor: 'rgba(255, 255, 255, 0.03)',
      titleColor: '#fff',
      bodyColor: 'rgba(240, 244, 248, 0.65)',
      borderColor: 'rgba(255, 255, 255, 0.08)',
      borderWidth: 1,
      padding: 12,
      displayColors: false
    }
  }
});
</script>
