<template>
  <div class="flex h-screen w-full overflow-hidden bg-background/95 transition-colors duration-300">
    <!-- SIDEBAR (Glassmorphism) -->
    <aside class="w-64 flex flex-col glass-panel border-r border-border/40 shrink-0 z-20">
      <!-- Logo -->
      <div class="h-16 flex items-center px-6 border-b border-border/40 relative overflow-hidden group cursor-pointer">
        <!-- Animated Background Glow -->
        <div class="absolute inset-0 bg-gradient-to-r from-primary/10 to-accent/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
        
        <div class="relative w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-accent flex items-center justify-center text-primary-foreground font-bold font-mono text-sm mr-3 shadow-[0_0_15px_hsl(var(--primary)/0.5)]">
          <div class="absolute inset-0 bg-white/20 rounded-lg blur-[2px]"></div>
          AL
        </div>
        <div class="relative font-mono font-semibold tracking-wide text-foreground">
          <span class="font-semibold tracking-tight text-foreground">A.L.F.I.E</span>
        </div>
        <span class="relative ml-2 text-[9px] bg-accent/20 text-accent px-2 py-0.5 rounded-full font-mono uppercase tracking-widest border border-accent/20 shadow-[0_0_10px_hsl(var(--accent)/0.2)]">Super</span>
      </div>

      <!-- Navigation -->
      <nav class="flex-1 overflow-y-auto p-4 space-y-1">
        <div class="mb-2 px-4 text-xs font-semibold text-muted-foreground uppercase tracking-wider">Platform</div>
        
        <router-link to="/" class="flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-medium transition-all hover:bg-muted/50 text-muted-foreground hover:text-foreground" active-class="bg-primary/10 text-primary hover:bg-primary/15 border-l-2 border-primary shadow-[inset_0_0_20px_hsl(var(--primary)/0.05)]" exact>
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="7" height="9" x="3" y="3" rx="1"/><rect width="7" height="5" x="14" y="3" rx="1"/><rect width="7" height="9" x="14" y="12" rx="1"/><rect width="7" height="5" x="3" y="16" rx="1"/></svg>
          Overview
        </router-link>

        <router-link to="/tenants" class="flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-medium transition-all hover:bg-muted/50 text-muted-foreground hover:text-foreground" active-class="bg-primary/10 text-primary hover:bg-primary/15 border-l-2 border-primary shadow-[inset_0_0_20px_hsl(var(--primary)/0.05)]">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
          Tenants
        </router-link>

        <router-link to="/personas" class="flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-medium transition-colors hover:bg-muted text-muted-foreground" active-class="bg-primary/10 text-primary hover:bg-primary/10 border-l-2 border-primary">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
          Niches & Personas
        </router-link>

        <router-link to="/calls" class="flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-medium transition-colors hover:bg-muted text-muted-foreground" active-class="bg-primary/10 text-primary hover:bg-primary/10 border-l-2 border-primary">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg>
          Call Logs & QA
        </router-link>

        <router-link to="/tools-registry" class="flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-medium transition-colors hover:bg-muted text-muted-foreground" active-class="bg-primary/10 text-primary hover:bg-primary/10 border-l-2 border-primary">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></svg>
          Tool Registry
        </router-link>

        <router-link to="/phone-numbers" class="flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-medium transition-colors hover:bg-muted text-muted-foreground" active-class="bg-primary/10 text-primary hover:bg-primary/10 border-l-2 border-primary">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="14" height="20" x="5" y="2" rx="2" ry="2"/><path d="M12 18h.01"/></svg>
          Phone Numbers
        </router-link>

        <router-link to="/debug" class="flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-medium transition-colors hover:bg-muted text-muted-foreground" active-class="bg-primary/10 text-primary hover:bg-primary/10 border-l-2 border-primary">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="4 17 10 11 4 5"/><line x1="12" y1="19" x2="20" y2="19"/></svg>
          Debug Logs
        </router-link>

        <router-link to="/config" class="flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-medium transition-colors hover:bg-muted text-muted-foreground" active-class="bg-primary/10 text-primary hover:bg-primary/10 border-l-2 border-primary">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
          Agent Config
        </router-link>

        <div class="text-[10px] uppercase tracking-widest font-semibold text-muted-foreground px-3 py-2 mt-6">Billing</div>
        
        <router-link to="/revenue" class="flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-medium transition-colors hover:bg-muted text-muted-foreground" active-class="bg-primary/10 text-primary hover:bg-primary/10 border-l-2 border-primary">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
          Revenue
        </router-link>

        <router-link to="/credits" class="flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-medium transition-colors hover:bg-muted text-muted-foreground" active-class="bg-primary/10 text-primary hover:bg-primary/10 border-l-2 border-primary">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="20" height="14" x="2" y="5" rx="2"/><line x1="2" y1="10" x2="22" y2="10"/></svg>
          Credits
        </router-link>

        <router-link to="/vouchers" class="flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-medium transition-colors hover:bg-muted text-muted-foreground" active-class="bg-primary/10 text-primary hover:bg-primary/10 border-l-2 border-primary">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/><line x1="7" y1="7" x2="7.01" y2="7"/></svg>
          Vouchers
        </router-link>
      </nav>

      <!-- Profile Footer -->
      <div class="p-4 border-t border-border">
        <div @click="logout" class="flex items-center gap-3 px-3 py-2 rounded-md hover:bg-muted cursor-pointer transition-colors group">
          <div class="w-8 h-8 rounded-full bg-gradient-to-tr from-accent to-primary flex items-center justify-center text-primary-foreground font-bold text-xs shrink-0">
            SA
          </div>
          <div class="flex-1 min-w-0">
            <div class="text-sm font-medium text-foreground truncate">Super Admin</div>
            <div class="text-[11px] text-muted-foreground truncate group-hover:text-destructive transition-colors">Owner · Logout</div>
          </div>
        </div>
      </div>
    </aside>

    <!-- MAIN CONTENT -->
    <main class="flex-1 flex flex-col min-w-0 bg-background/40 relative">
      <!-- Topbar (Glassmorphism) -->
      <header class="h-16 glass-panel border-b border-border/40 flex items-center justify-between px-6 shrink-0 z-10 sticky top-0 rounded-bl-xl shadow-sm">
        <div class="flex items-center gap-2 text-muted-foreground text-sm font-mono tracking-wide">
          <span class="text-primary font-bold">/</span>
          {{ $route.meta.title || $route.name || 'Overview' }}
        </div>
        <div class="flex items-center gap-4">
          <!-- Theme Toggle -->
          <button @click="toggleTheme" class="inline-flex items-center justify-center w-8 h-8 rounded-full transition-colors hover:bg-muted text-foreground border border-border/50 bg-background/50 backdrop-blur-sm">
            <svg v-if="isDark" xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
          </button>

          <div class="flex items-center gap-2 px-3 py-1.5 bg-emerald-500/10 border border-emerald-500/20 rounded-full text-[11px] font-mono font-medium text-emerald-500 shadow-[0_0_10px_hsl(var(--emerald-500)/0.2)]">
            <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse shadow-[0_0_5px_hsl(var(--emerald-500)/0.8)]"></span>
            ALL SYSTEMS OPERATIONAL
          </div>
          <button class="inline-flex items-center gap-2 px-3 py-1.5 rounded-md text-sm font-medium transition-colors border border-border/50 bg-background/50 backdrop-blur-sm hover:bg-muted text-foreground">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/></svg>
            Alerts
          </button>
           <div class="flex items-center gap-4">
          <!-- Voice Simulator Action -->
          <button @click="isSimulatorOpen = true" class="inline-flex items-center gap-2 px-4 py-1.5 rounded-md text-sm font-medium transition-all bg-primary hover:bg-primary/90 text-primary-foreground shadow-[0_0_15px_hsl(var(--primary)/0.4)] hover:shadow-[0_0_25px_hsl(var(--primary)/0.6)]">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="animate-pulse"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" x2="12" y1="19" y2="22"/></svg>
            Test Simulator
          </button>
        </div>
        </div>
      </header>

      <!-- Page Content -->
      <div class="flex-1 overflow-y-auto p-6">
        <div class="mx-auto max-w-7xl">
          <router-view />
        </div>
      </div>
    </main>

    <!-- WebRTC Simulator Modal -->
    <SimulatorModal :isOpen="isSimulatorOpen" @close="isSimulatorOpen = false" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useAuthStore } from '../stores/auth';
import { useRouter } from 'vue-router';
import SimulatorModal from '../components/SimulatorModal.vue';

const authStore = useAuthStore();
const router = useRouter();
const isSimulatorOpen = ref(false);

const isDark = ref(true);

const toggleTheme = () => {
  isDark.value = !isDark.value;
  if (isDark.value) {
    document.documentElement.classList.add('dark');
  } else {
    document.documentElement.classList.remove('dark');
  }
};

onMounted(() => {
  // Check system preference or default to dark
  if (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches) {
    isDark.value = false;
  } else {
    document.documentElement.classList.add('dark');
  }
});

const logout = () => {
  authStore.logout();
  router.push('/login');
};
</script>
