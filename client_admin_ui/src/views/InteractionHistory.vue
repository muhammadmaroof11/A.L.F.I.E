<template>
  <div class="max-w-4xl mx-auto space-y-6">
    
    <!-- Interaction Card -->
    <div v-for="interaction in interactions" :key="interaction.id" class="glass-elevated p-6 rounded-2xl border border-border group transition-all hover:bg-surface/50">
      <div class="flex items-center justify-between mb-6">
        <div class="flex items-center gap-4">
          <div class="w-12 h-12 rounded-xl bg-accent/10 flex items-center justify-center text-accent shadow-glow transition-transform group-hover:scale-105">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg>
          </div>
          <div>
            <h3 class="font-display font-bold text-lg text-white group-hover:text-accent transition-colors">{{ interaction.caller }}</h3>
            <p class="text-xs font-mono text-textMuted">{{ interaction.date }} • {{ interaction.duration }}</p>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <span class="px-3 py-1.5 rounded-lg text-xs font-bold uppercase tracking-wider bg-accentSecondary/10 text-accentSecondary border border-accentSecondary/20 shadow-[0_0_10px_rgba(16,185,129,0.1)]">
            Score: {{ interaction.score }}/10
          </span>
        </div>
      </div>

      <!-- Audio Player Mock -->
      <div class="bg-surface border border-border rounded-xl p-4 flex items-center gap-4 mb-6 transition-colors group-hover:border-accent/30">
        <button class="w-10 h-10 rounded-full bg-white text-background flex items-center justify-center hover:bg-white/90 hover:scale-105 transition-transform shadow-[0_0_15px_rgba(255,255,255,0.3)]">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
        </button>
        <div class="flex-1 h-1.5 bg-background rounded-full overflow-hidden border border-border">
          <div class="h-full bg-gradient-accent w-1/3 relative">
            <div class="absolute right-0 top-1/2 -translate-y-1/2 w-2 h-2 bg-white rounded-full shadow-[0_0_8px_white]"></div>
          </div>
        </div>
        <span class="text-xs text-textSecondary font-mono bg-surfaceHover px-2 py-1 rounded">01:24 / 04:12</span>
      </div>

      <!-- Transcript snippet -->
      <div class="bg-background/80 rounded-xl p-5 border border-border text-sm text-textSecondary space-y-4 font-mono shadow-inner">
        <div class="flex gap-4">
          <span class="text-white font-semibold min-w-[60px] flex items-center gap-1">
            <div class="w-1.5 h-1.5 bg-accentSecondary rounded-full"></div> Alfie
          </span>
          <p class="leading-relaxed">Hello! This is Alfie from the leasing office. How can I help you today?</p>
        </div>
        <div class="flex gap-4">
          <span class="text-accent font-semibold min-w-[60px] flex items-center gap-1">
            <div class="w-1.5 h-1.5 bg-accent rounded-full"></div> Caller
          </span>
          <p class="leading-relaxed text-textPrimary">Hi, I was looking at the 2-bedroom on 5th avenue. Is it still available?</p>
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
