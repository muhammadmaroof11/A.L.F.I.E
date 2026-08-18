<template>
  <div class="h-full flex flex-col p-8 overflow-y-auto w-full max-w-6xl mx-auto space-y-8">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold tracking-tight text-foreground flex items-center gap-3">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-primary"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg>
          Callbacks & Priority Queue
        </h1>
        <p class="text-muted-foreground mt-1 text-sm">Real-time schedule of callbacks automatically booked when hot transfers were busy or requested by callers.</p>
      </div>
      <div class="flex items-center gap-3">
        <button @click="fetchCallbacks" class="glass-button text-xs px-3 py-2 flex items-center gap-1.5 hover:bg-muted/50">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" :class="{ 'animate-spin': loading }"><path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"/></svg>
          Refresh
        </button>
      </div>
    </div>

    <!-- Error/Loading states -->
    <div v-if="loading" class="flex justify-center p-12">
      <div class="animate-pulse flex flex-col items-center gap-4">
        <div class="h-12 w-12 rounded-full border-4 border-primary border-t-transparent animate-spin"></div>
        <p class="text-muted-foreground text-sm font-medium">Loading callback queue...</p>
      </div>
    </div>
    
    <div v-else-if="error" class="glass-panel p-6 border-red-500/20 bg-red-500/5 text-red-400 rounded-xl">
      <p>{{ error }}</p>
    </div>

    <div v-else-if="callbacks.length === 0" class="glass-panel p-16 flex flex-col items-center justify-center text-center rounded-xl border border-border/50">
      <div class="w-16 h-16 rounded-full bg-emerald-500/10 flex items-center justify-center mb-4 text-emerald-500">
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg>
      </div>
      <h3 class="text-xl font-semibold text-foreground mb-2">No Pending Callbacks</h3>
      <p class="text-muted-foreground max-w-md">All scheduled callbacks and busy transfer fallbacks are up to date.</p>
    </div>

    <!-- Callbacks List -->
    <div v-else class="space-y-4">
      <div v-for="item in callbacks" :key="item.id" class="glass-panel p-6 rounded-xl border border-border/50 hover:border-primary/30 transition-all flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div class="space-y-1.5">
          <div class="flex items-center gap-3">
            <h3 class="text-lg font-bold text-foreground">{{ item.caller_name }}</h3>
            <span class="text-xs font-mono bg-primary/10 text-primary px-2.5 py-0.5 rounded-full border border-primary/20">
              {{ item.caller_phone }}
            </span>
            <span :class="item.status === 'completed' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 'bg-amber-500/10 text-amber-400 border-amber-500/20'" class="text-xs font-semibold px-2.5 py-0.5 rounded-full border capitalize">
              {{ item.status }}
            </span>
          </div>
          <div class="text-sm text-muted-foreground flex flex-wrap items-center gap-4">
            <span class="flex items-center gap-1.5 text-foreground font-medium">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="text-primary"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
              Scheduled Time: {{ item.preferred_time }}
            </span>
            <span class="flex items-center gap-1.5">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle></svg>
              Department: {{ item.target_department || 'General' }}
            </span>
          </div>
          <p v-if="item.reason || item.notes" class="text-xs text-muted-foreground/90 mt-2 bg-muted/20 p-2.5 rounded-lg border border-border/30">
            <strong class="text-foreground">Topic:</strong> {{ item.reason }} <span v-if="item.notes">— {{ item.notes }}</span>
          </p>
        </div>

        <div class="flex items-center gap-2 self-end md:self-center">
          <a :href="'tel:' + item.caller_phone" class="glass-button bg-primary/10 text-primary hover:bg-primary/20 text-xs px-3 py-2 flex items-center gap-1.5">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg>
            Call Back
          </a>
          <button v-if="item.status !== 'completed'" @click="markCompleted(item.id)" class="glass-button bg-emerald-500/10 text-emerald-400 hover:bg-emerald-500/20 text-xs px-3 py-2 flex items-center gap-1.5">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg>
            Mark Done
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useAuthStore } from '../stores/auth';
import api from '../services/api';

const authStore = useAuthStore();
const loading = ref(true);
const error = ref('');
const callbacks = ref([]);

const fetchCallbacks = async () => {
  loading.value = true;
  error.value = '';
  try {
    const res = await api.get(`/api/client/callbacks?tenant_id=${authStore.user?.tenant_id}`);
    callbacks.value = res.data || [];
  } catch (err) {
    console.error(err);
    error.value = 'Failed to load scheduled callbacks.';
  } finally {
    loading.value = false;
  }
};

const markCompleted = async (id) => {
  try {
    await api.patch(`/api/client/callbacks/${id}?status=completed`);
    const target = callbacks.value.find(c => c.id === id);
    if (target) target.status = 'completed';
  } catch (err) {
    console.error("Failed to mark callback completed:", err);
  }
};

onMounted(() => {
  fetchCallbacks();
});
</script>
