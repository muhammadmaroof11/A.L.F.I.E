<template>
  <div class="flex h-screen bg-background text-textPrimary overflow-hidden font-sans">
    <!-- Sidebar -->
    <aside class="w-64 glass m-5 rounded-2xl flex flex-col relative z-20 shadow-2xl">
      <div class="h-20 flex items-center px-8 border-b border-border/50">
        <div class="w-8 h-8 rounded-lg bg-gradient-accent flex items-center justify-center mr-3 shadow-glow">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>
        </div>
        <span class="font-display font-bold text-xl text-white tracking-wide">A.L.F.I.E</span>
      </div>

      <nav class="flex-1 px-4 mt-6 space-y-2">
        <div class="text-[10px] font-bold text-textMuted uppercase tracking-[0.2em] px-4 mb-4">Workspace</div>
        
        <router-link to="/" class="flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-300" active-class="bg-surfaceHover text-accent shadow-sm border border-border" exact-active-class="bg-surfaceHover text-accent shadow-sm border border-border">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect></svg>
          <span class="font-medium">Dashboard</span>
        </router-link>
        
        <router-link to="/leads" class="flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-300 text-textSecondary hover:bg-surface hover:text-white" active-class="bg-surfaceHover text-accent shadow-sm border border-border">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>
          <span class="font-medium">Leads Pipeline</span>
        </router-link>
        
        <router-link to="/interactions" class="flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-300 text-textSecondary hover:bg-surface hover:text-white" active-class="bg-surfaceHover text-accent shadow-sm border border-border">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
          <span class="font-medium">Interactions</span>
        </router-link>

        <router-link to="/analytics" class="flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-300 text-textSecondary hover:bg-surface hover:text-white" active-class="bg-surfaceHover text-accent shadow-sm border border-border">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line></svg>
          <span class="font-medium">Analytics</span>
        </router-link>

        <router-link to="/agent" class="flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-300 text-textSecondary hover:bg-surface hover:text-white" active-class="bg-surfaceHover text-accent shadow-sm border border-border">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v20"></path><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>
          <span class="font-medium">Agent Config</span>
        </router-link>
      </nav>

      <div class="p-4 mt-auto">
        <div class="bg-background/80 rounded-xl p-4 border border-border">
          <div class="flex items-center gap-3 mb-3">
            <div class="w-2.5 h-2.5 rounded-full bg-accentSecondary shadow-[0_0_8px_rgba(16,185,129,0.8)] animate-pulse"></div>
            <span class="text-sm font-medium text-white">Agent Online</span>
          </div>
          <button @click="logout" class="w-full text-left text-sm text-textMuted hover:text-white transition-colors">Sign Out</button>
        </div>
      </div>
    </aside>

    <!-- Main View -->
    <main class="flex-1 flex flex-col relative overflow-hidden z-10 py-5 pr-5">
      <!-- Glow ambient background -->
      <div class="absolute top-0 right-0 w-[500px] h-[500px] bg-accent/5 rounded-full blur-[120px] pointer-events-none"></div>
      
      <!-- Topbar -->
      <header class="h-16 flex items-center justify-between px-8 mb-4">
        <h1 class="text-3xl font-display font-bold text-white">{{ $route.name }}</h1>
        <div class="flex items-center gap-4">
          <button class="w-10 h-10 rounded-full glass flex items-center justify-center hover:bg-surfaceHover transition-colors border border-border text-textSecondary hover:text-white">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path><path d="M13.73 21a2 2 0 0 1-3.46 0"></path></svg>
          </button>
        </div>
      </header>

      <!-- Page Content -->
      <div class="flex-1 overflow-y-auto px-8 pb-8 custom-scrollbar">
        <router-view />
      </div>
    </main>
  </div>
</template>

<script setup>
import { useAuthStore } from '../stores/auth';
import { useRouter } from 'vue-router';

const authStore = useAuthStore();
const router = useRouter();

const logout = () => {
  authStore.logout();
  router.push('/login');
};
</script>

<style>
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.2);
}
</style>
