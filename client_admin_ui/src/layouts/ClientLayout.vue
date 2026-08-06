<template>
  <div class="flex h-screen w-full overflow-hidden bg-background/95 transition-colors duration-300">
    
    <!-- Sidebar (Glassmorphism) -->
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
        <span class="relative ml-2 text-[9px] bg-primary/20 text-primary px-2 py-0.5 rounded-full font-mono uppercase tracking-widest border border-primary/20 shadow-[0_0_10px_hsl(var(--primary)/0.2)]">Client</span>
      </div>

      <!-- Navigation -->
      <nav class="flex-1 overflow-y-auto p-4 space-y-1">
        <div class="mb-2 px-4 text-xs font-semibold text-muted-foreground uppercase tracking-wider">Workspace</div>
        
        <router-link to="/" class="flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-medium transition-all hover:bg-muted/50 text-muted-foreground hover:text-foreground" active-class="bg-primary/10 text-primary hover:bg-primary/15 border-l-2 border-primary shadow-[inset_0_0_20px_hsl(var(--primary)/0.05)]" exact>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect></svg>
          Dashboard
        </router-link>
        
        <router-link to="/leads" class="flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-medium transition-all hover:bg-muted/50 text-muted-foreground hover:text-foreground" active-class="bg-primary/10 text-primary hover:bg-primary/15 border-l-2 border-primary shadow-[inset_0_0_20px_hsl(var(--primary)/0.05)]">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>
          Leads Pipeline
        </router-link>
        
        <router-link to="/interactions" class="flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-medium transition-all hover:bg-muted/50 text-muted-foreground hover:text-foreground" active-class="bg-primary/10 text-primary hover:bg-primary/15 border-l-2 border-primary shadow-[inset_0_0_20px_hsl(var(--primary)/0.05)]">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
          Interactions
        </router-link>

        <router-link to="/analytics" class="flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-medium transition-all hover:bg-muted/50 text-muted-foreground hover:text-foreground" active-class="bg-primary/10 text-primary hover:bg-primary/15 border-l-2 border-primary shadow-[inset_0_0_20px_hsl(var(--primary)/0.05)]">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line></svg>
          Analytics
        </router-link>

        <div class="text-[10px] uppercase tracking-widest font-semibold text-muted-foreground px-3 py-2 mt-6">Settings</div>

        <router-link to="/agent" class="flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-medium transition-all hover:bg-muted/50 text-muted-foreground hover:text-foreground" active-class="bg-primary/10 text-primary hover:bg-primary/15 border-l-2 border-primary shadow-[inset_0_0_20px_hsl(var(--primary)/0.05)]">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v20"></path><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>
          Agent Config
        </router-link>
      </nav>

      <!-- Profile Footer -->
      <div class="p-4 border-t border-border/40">
        <div @click="logout" class="flex items-center gap-3 px-3 py-2 rounded-md hover:bg-muted cursor-pointer transition-colors group">
          <div class="w-8 h-8 rounded-full bg-gradient-to-tr from-primary to-accent flex items-center justify-center text-primary-foreground font-bold text-xs shrink-0">
            CA
          </div>
          <div class="flex-1 min-w-0">
            <div class="text-sm font-medium text-foreground truncate">Client Admin</div>
            <div class="text-[11px] text-muted-foreground truncate group-hover:text-destructive transition-colors">Workspace · Logout</div>
          </div>
        </div>
      </div>
    </aside>

    <!-- Main View -->
    <main class="flex-1 flex flex-col relative overflow-hidden bg-background/40">
      
      <!-- Topbar (Glassmorphism) -->
      <header class="h-16 glass-panel border-b border-border/40 flex items-center justify-between px-6 shrink-0 z-10 sticky top-0 rounded-bl-xl shadow-sm">
        <div class="flex items-center gap-2 text-muted-foreground text-sm font-mono tracking-wide">
          <span class="text-primary font-bold">/</span>
          {{ $route.name || 'Dashboard' }}
        </div>
        
        <div class="flex items-center gap-4">
          <!-- Theme Toggle -->
          <button @click="toggleTheme" class="inline-flex items-center justify-center w-8 h-8 rounded-full transition-colors hover:bg-muted text-foreground border border-border/50 bg-background/50 backdrop-blur-sm">
            <svg v-if="isDark" xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
          </button>

          <div class="flex items-center gap-2 px-3 py-1.5 bg-emerald-500/10 border border-emerald-500/20 rounded-full text-[11px] font-mono font-medium text-emerald-500 shadow-[0_0_10px_hsl(var(--emerald-500)/0.2)]">
            <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse shadow-[0_0_5px_hsl(var(--emerald-500)/0.8)]"></span>
            AGENT ONLINE
          </div>
          
          <button class="inline-flex items-center justify-center w-8 h-8 rounded-full transition-colors border border-border/50 bg-background/50 backdrop-blur-sm hover:bg-muted text-foreground relative">
             <!-- Notification Dot -->
            <span class="absolute top-1.5 right-2 w-1.5 h-1.5 rounded-full bg-primary shadow-[0_0_5px_hsl(var(--primary))] animate-pulse"></span>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path><path d="M13.73 21a2 2 0 0 1-3.46 0"></path></svg>
          </button>
        </div>
      </header>

      <!-- Page Content -->
      <div class="flex-1 overflow-y-auto p-8 custom-scrollbar">
        <div class="mx-auto max-w-7xl">
          <router-view />
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useAuthStore } from '../stores/auth';
import { useRouter } from 'vue-router';

const authStore = useAuthStore();
const router = useRouter();
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

<style>
/* Scoped scrollbar inherited from base style.css but defined here specifically for custom-scrollbar class if needed */
</style>
