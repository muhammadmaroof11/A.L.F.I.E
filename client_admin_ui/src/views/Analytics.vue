<template>
  <div class="space-y-6">
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      
      <!-- Chart 1: Call Outcomes -->
      <div class="glass-panel group p-6 h-[400px] flex flex-col relative rounded-xl overflow-hidden">
        <div class="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
        <h3 class="font-semibold text-lg mb-6 relative">Call Outcomes</h3>
        <div class="flex-1 flex items-center justify-center relative w-full h-full">
          <Doughnut :data="doughnutData" :options="doughnutOptions" />
          <div class="absolute inset-0 flex flex-col items-center justify-center pointer-events-none mt-2">
            <span class="text-4xl font-bold text-foreground drop-shadow-[0_0_10px_hsl(var(--primary)/0.3)]">42%</span>
            <span class="text-xs font-mono text-muted-foreground uppercase tracking-widest mt-1">Converted</span>
          </div>
        </div>
      </div>

      <!-- Chart 2: Lead Scores -->
      <div class="glass-panel group p-6 h-[400px] flex flex-col relative rounded-xl overflow-hidden">
        <div class="absolute inset-0 bg-gradient-to-br from-emerald-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
        <h3 class="font-semibold text-lg mb-6 relative">Average Lead Score by Week</h3>
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
      backgroundColor: ['hsl(217.2 91.2% 59.8%)', 'hsl(0 62.8% 30.6%)', 'hsl(215 20.2% 65.1%)', 'hsl(35 91.7% 53.5%)'],
      borderColor: 'hsl(222.2 84% 4.9%)',
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
        color: 'hsl(215 20.2% 65.1%)', // muted-foreground
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
      backgroundColor: 'hsl(222.2 84% 4.9%)',
      titleColor: 'hsl(210 20% 98%)',
      bodyColor: 'hsl(215 20.2% 65.1%)',
      borderColor: 'hsl(217.2 32.6% 17.5%)',
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
      backgroundColor: 'hsla(217.2, 91.2%, 59.8%, 0.8)',
      hoverBackgroundColor: 'hsla(217.2, 91.2%, 59.8%, 1)',
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
      grid: { display: false, drawBorder: false },
      ticks: { 
        color: 'hsl(215 20.2% 65.1%)',
        font: { family: 'Inter', size: 11 },
        padding: 10
      }
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
      displayColors: false
    }
  }
});
</script>
