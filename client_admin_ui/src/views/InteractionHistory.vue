<template>
  <div class="max-w-4xl mx-auto space-y-6">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold tracking-tight text-foreground">Interaction History</h1>
        <p class="text-xs text-muted-foreground mt-0.5">Recorded phone calls, AI transcripts, and conversational QA scores.</p>
      </div>
      
      <!-- Search Input -->
      <div class="flex items-center gap-2">
        <div class="relative">
          <svg class="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
          <input 
            v-model="searchQuery" 
            @input="debouncedSearch" 
            type="text" 
            placeholder="Search transcripts, phones..." 
            class="h-9 pl-9 pr-3 rounded-lg border border-border bg-background/50 text-xs w-64 focus:outline-none focus:ring-1 focus:ring-primary"
          />
        </div>
        <button @click="fetchInteractions" class="glass-button text-xs px-3 py-2 flex items-center gap-1.5 hover:bg-muted/50">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" :class="{ 'animate-spin': loading }"><path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"/></svg>
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center p-12">
      <div class="animate-pulse flex flex-col items-center gap-4">
        <div class="h-10 w-10 rounded-full border-4 border-primary border-t-transparent animate-spin"></div>
        <p class="text-muted-foreground text-xs font-medium">Loading call interactions...</p>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="interactions.length === 0" class="glass-panel p-16 flex flex-col items-center justify-center text-center rounded-xl border border-border/50">
      <div class="w-14 h-14 rounded-full bg-primary/10 flex items-center justify-center mb-3 text-primary">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg>
      </div>
      <h3 class="text-lg font-semibold text-foreground mb-1">No Interactions Found</h3>
      <p class="text-xs text-muted-foreground max-w-sm">No call recordings matching your query exist for this workspace yet.</p>
    </div>
    
    <!-- Interaction Cards -->
    <div v-else class="space-y-6">
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
              <span :class="interaction.score >= 8 ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 'bg-amber-500/10 text-amber-400 border-amber-500/20'" class="px-3 py-1.5 rounded-md text-xs font-semibold uppercase tracking-wider border">
                Score: {{ interaction.score }}/10
              </span>
            </div>
          </div>

          <!-- Transcript Section -->
          <div v-if="interaction.transcript && interaction.transcript.length > 0" class="bg-background/80 rounded-xl p-5 border border-border text-xs text-muted-foreground space-y-3 font-mono shadow-sm max-h-60 overflow-y-auto">
            <div v-for="(msg, idx) in interaction.transcript" :key="idx" class="flex gap-3">
              <span :class="msg.role === 'assistant' ? 'text-primary' : 'text-emerald-400'" class="font-semibold min-w-[70px] flex items-center gap-1.5 uppercase text-[10px]">
                <div class="w-1.5 h-1.5 rounded-full" :class="msg.role === 'assistant' ? 'bg-primary' : 'bg-emerald-400'"></div>
                {{ msg.role === 'assistant' ? 'Alfie' : 'Caller' }}
              </span>
              <p class="leading-relaxed text-foreground/90 flex-1">{{ msg.content }}</p>
            </div>
          </div>
          <div v-else class="bg-background/40 rounded-xl p-4 border border-border text-xs text-muted-foreground italic font-mono">
            No audio transcript captured for this call session.
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '../services/api';
import { useAuthStore } from '../stores/auth';

const auth = useAuthStore();
const interactions = ref([]);
const loading = ref(true);
const searchQuery = ref('');
let searchTimer = null;

const fetchInteractions = async () => {
  loading.value = true;
  try {
    const tenantId = auth.tenantId || localStorage.getItem('alfie_tenant_id');
    const res = await api.get('/api/client/interactions', {
      params: {
        tenant_id: tenantId,
        search: searchQuery.value || undefined
      }
    });
    interactions.value = res.data || [];
  } catch (err) {
    console.error("Failed to load interactions:", err);
  } finally {
    loading.value = false;
  }
};

const debouncedSearch = () => {
  if (searchTimer) clearTimeout(searchTimer);
  searchTimer = setTimeout(() => {
    fetchInteractions();
  }, 300);
};

onMounted(() => {
  fetchInteractions();
});
</script>

