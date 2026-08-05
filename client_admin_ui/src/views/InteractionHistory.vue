<template>
  <div class="max-w-4xl mx-auto space-y-6">
    
    <!-- Interaction Card -->
    <div v-for="interaction in interactions" :key="interaction.id" class="glass-panel p-6">
      <div class="flex items-center justify-between mb-4">
        <div class="flex items-center gap-4">
          <div class="w-10 h-10 rounded-full bg-clientPrimary/20 flex items-center justify-center text-clientPrimary">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg>
          </div>
          <div>
            <h3 class="font-semibold text-white">{{ interaction.caller }}</h3>
            <p class="text-xs text-clientMuted">{{ interaction.date }} • {{ interaction.duration }}</p>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <span class="px-3 py-1 rounded-full text-xs font-medium bg-emerald-400/10 text-emerald-400 border border-emerald-400/20">
            Score: {{ interaction.score }}/10
          </span>
        </div>
      </div>

      <!-- Audio Player Mock -->
      <div class="bg-clientSurface border border-white/5 rounded-xl p-4 flex items-center gap-4 mb-4">
        <button class="w-8 h-8 rounded-full bg-white text-clientBg flex items-center justify-center hover:bg-white/90">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
        </button>
        <div class="flex-1 h-1 bg-white/10 rounded-full overflow-hidden">
          <div class="h-full bg-clientPrimary w-1/3"></div>
        </div>
        <span class="text-xs text-clientMuted font-mono">01:24 / 04:12</span>
      </div>

      <!-- Transcript snippet -->
      <div class="bg-clientBg rounded-xl p-4 border border-white/5 text-sm text-clientMuted space-y-3">
        <div class="flex gap-3">
          <span class="text-white font-medium min-w-[50px]">Alfie</span>
          <p>Hello! This is Alfie from the leasing office. How can I help you today?</p>
        </div>
        <div class="flex gap-3">
          <span class="text-clientPrimary font-medium min-w-[50px]">Caller</span>
          <p>Hi, I was looking at the 2-bedroom on 5th avenue. Is it still available?</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const interactions = ref([
  {
    id: 1,
    caller: '+1 (555) 019-2834',
    date: 'Oct 24, 2026 2:14 PM',
    duration: '4m 12s',
    score: 8
  },
  {
    id: 2,
    caller: '+1 (555) 998-1122',
    date: 'Oct 24, 2026 11:30 AM',
    duration: '2m 05s',
    score: 4
  }
]);
</script>
