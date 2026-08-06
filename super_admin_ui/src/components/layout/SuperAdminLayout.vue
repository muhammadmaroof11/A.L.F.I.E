<template>
  <div class="flex h-screen overflow-hidden bg-background">
    <!-- Sidebar -->
    <aside class="w-64 flex flex-col bg-card border-r border-border shrink-0">
      <!-- Logo -->
      <div class="h-16 flex items-center px-6 border-b border-border">
        <div class="w-8 h-8 rounded bg-gradient-to-br from-primary to-accent flex items-center justify-center text-primary-foreground font-bold font-mono text-sm mr-3">
          AL
        </div>
        <div class="font-mono font-semibold tracking-wide text-foreground">
          A.L.F.I.E <span class="text-primary">OS</span>
        </div>
        <span class="ml-2 text-[9px] bg-accent/20 text-accent px-2 py-0.5 rounded-full font-mono uppercase tracking-widest border border-accent/20">Super</span>
      </div>

      <!-- Navigation -->
      <nav class="flex-1 overflow-y-auto p-4 space-y-1">
        <div class="text-[10px] uppercase tracking-widest font-semibold text-muted-foreground px-3 py-2 mt-2">Platform</div>
        
        <router-link to="/dashboard" class="flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-medium transition-colors hover:bg-muted text-muted-foreground" exact-active-class="bg-primary/10 text-primary hover:bg-primary/10 border-l-2 border-primary">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="7" height="9" x="3" y="3" rx="1"/><rect width="7" height="5" x="14" y="3" rx="1"/><rect width="7" height="9" x="14" y="12" rx="1"/><rect width="7" height="5" x="3" y="16" rx="1"/></svg>
          Dashboard
        </router-link>

        <router-link to="/tenants" class="flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-medium transition-colors hover:bg-muted text-muted-foreground" active-class="bg-primary/10 text-primary hover:bg-primary/10 border-l-2 border-primary">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
          Tenants
        </router-link>

        <router-link to="/calls" class="flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-medium transition-colors hover:bg-muted text-muted-foreground" active-class="bg-primary/10 text-primary hover:bg-primary/10 border-l-2 border-primary">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg>
          Call Logs
        </router-link>

        <router-link to="/vouchers" class="flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-medium transition-colors hover:bg-muted text-muted-foreground" active-class="bg-primary/10 text-primary hover:bg-primary/10 border-l-2 border-primary">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/><line x1="7" y1="7" x2="7.01" y2="7"/></svg>
          Vouchers
        </router-link>

        <div class="text-[10px] uppercase tracking-widest font-semibold text-muted-foreground px-3 py-2 mt-6">Configuration</div>

        <router-link to="/agent" class="flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-medium transition-colors hover:bg-muted text-muted-foreground" active-class="bg-primary/10 text-primary hover:bg-primary/10 border-l-2 border-primary">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
          Base Agent
        </router-link>
        
        <router-link to="/personas" class="flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-medium transition-colors hover:bg-muted text-muted-foreground" active-class="bg-primary/10 text-primary hover:bg-primary/10 border-l-2 border-primary">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
          Personas
        </router-link>

        <router-link to="/tools" class="flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-medium transition-colors hover:bg-muted text-muted-foreground" active-class="bg-primary/10 text-primary hover:bg-primary/10 border-l-2 border-primary">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></svg>
          Tool Registry
        </router-link>

        <router-link to="/debug" class="flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-medium transition-colors hover:bg-muted text-muted-foreground" active-class="bg-primary/10 text-primary hover:bg-primary/10 border-l-2 border-primary">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="4 17 10 11 4 5"/><line x1="12" y1="19" x2="20" y2="19"/></svg>
          Debug Logs
        </router-link>
      </nav>

      <!-- Profile Footer -->
      <div class="p-4 border-t border-border">
        <div class="flex items-center gap-3 px-3 py-2 rounded-md hover:bg-muted cursor-pointer transition-colors">
          <div class="w-8 h-8 rounded-full bg-gradient-to-tr from-accent to-primary flex items-center justify-center text-primary-foreground font-bold text-xs shrink-0">
            SA
          </div>
          <div class="flex-1 min-w-0">
            <div class="text-sm font-medium text-foreground truncate">Super Admin</div>
            <div class="text-[11px] text-muted-foreground truncate">Platform Root</div>
          </div>
        </div>
      </div>
    </aside>

    <!-- Main View Area -->
    <main class="flex-1 flex flex-col min-w-0">
      <!-- Topbar -->
      <header class="h-16 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 border-b border-border flex items-center justify-between px-6 shrink-0 z-10 sticky top-0">
        <h1 class="text-lg font-semibold tracking-tight">{{ routeName }}</h1>
        <div class="flex items-center gap-4">
          <div class="flex items-center gap-2 px-3 py-1.5 bg-green-500/10 border border-green-500/20 rounded-full text-xs font-mono text-green-500">
            <span class="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
            SYSTEM NORMAL
          </div>
        </div>
      </header>
      
      <!-- Content -->
      <div class="flex-1 overflow-y-auto p-6 bg-muted/20">
        <div class="mx-auto max-w-6xl">
          <router-view />
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();
const routeName = computed(() => route.meta.title || 'Super Admin');
</script>
