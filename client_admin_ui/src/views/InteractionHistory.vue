<template>
  <div class="max-w-4xl mx-auto space-y-6">
    
    <!-- Interaction Card -->
    <div v-for="interaction in interactions" :key="interaction.id" class="glass-panel group hover-glow p-6 transition-all duration-300 rounded-xl relative overflow-hidden">
      <div class="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
      <div class="relative">
      <div class="flex items-center justify-between mb-6">
        <div class="flex items-center gap-4">
          <div class="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center text-primary shadow-sm transition-transform group-hover:scale-105">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg>
          </div>
          <div>
            <h3 class="font-semibold text-lg text-foreground group-hover:text-primary transition-colors">{{ interaction.caller }}</h3>
            <p class="text-xs font-mono text-muted-foreground">{{ interaction.date }} • {{ interaction.duration }}</p>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <span class="px-3 py-1.5 rounded-md text-xs font-semibold uppercase tracking-wider bg-background border border-border text-muted-foreground flex items-center gap-1.5">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
            {{ interaction.agent_name }}
          </span>
          <span class="px-3 py-1.5 rounded-md text-xs font-semibold uppercase tracking-wider bg-accent text-accent-foreground border border-accent">
            Score: {{ interaction.score }}/10
          </span>
        </div>
      </div>

      <!-- Audio Player Mock -->
      <div class="bg-muted border border-border rounded-xl p-4 flex items-center gap-4 mb-6 transition-colors group-hover:border-primary/30">
        <button class="w-10 h-10 rounded-full bg-primary text-primary-foreground flex items-center justify-center hover:bg-primary/90 hover:scale-105 transition-transform shadow-sm">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
        </button>
        <div class="flex-1 h-1.5 bg-background rounded-full overflow-hidden border border-border">
          <div class="h-full bg-primary w-1/3 relative">
            <div class="absolute right-0 top-1/2 -translate-y-1/2 w-2 h-2 bg-background rounded-full border border-primary"></div>
          </div>
        </div>
        <span class="text-xs text-muted-foreground font-mono bg-card px-2 py-1 rounded border border-border">01:24 / 04:12</span>
      </div>

      <!-- Transcript snippet -->
      <div class="bg-background rounded-xl p-5 border border-border text-sm text-muted-foreground space-y-4 font-mono shadow-sm">
        <div class="flex gap-4">
          <span class="text-foreground font-semibold min-w-[60px] flex items-center gap-1">
            <div class="w-1.5 h-1.5 bg-accent rounded-full"></div> {{ interaction.agent_name.split(' ')[0] }}
          </span>
          <p class="leading-relaxed">Hello! This is {{ interaction.agent_name.split(' ')[0] }} from the leasing office. How can I help you today?</p>
        </div>
        <div class="flex gap-4">
          <span class="text-primary font-semibold min-w-[60px] flex items-center gap-1">
            <div class="w-1.5 h-1.5 bg-primary rounded-full"></div> Caller
          </span>
          <p class="leading-relaxed text-foreground">Hi, I was looking at the 2-bedroom on 5th avenue. Is it still available?</p>
        </div>
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
    score: 8,
    agent_name: 'Alfie (Support)'
  },
  {
    id: 2,
    caller: '+1 (555) 998-1122',
    date: 'Oct 24, 2026 11:30 AM',
    duration: '2m 05s',
    score: 4,
    agent_name: 'Sarah (Sales)'
  }
]);
</script>
