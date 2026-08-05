<template>
  <div class="flex h-screen overflow-hidden bg-background text-textPrimary">
    
    <!-- Sidebar -->
    <div class="w-64 glass border-r border-border flex flex-col z-10">
      <div class="h-16 flex items-center px-6 border-b border-border">
        <span class="font-display font-bold tracking-wider text-lg text-white flex items-center gap-2">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="url(#gradient-accent)" stroke-width="2"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>
          A.L.F.I.E
        </span>
      </div>
      <div class="p-4">
        <div class="text-xs font-mono text-textMuted uppercase tracking-widest mb-4 mt-2">Platform</div>
        <nav class="space-y-1">
          <router-link to="/" class="flex items-center gap-3 px-3 py-2 text-sm rounded-md transition-colors" exact-active-class="bg-surfaceHover text-white border-l-2 border-accent" active-class="text-textSecondary hover:bg-surface hover:text-white">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect></svg>
            Dashboard
          </router-link>
          <router-link to="/tenants" class="flex items-center gap-3 px-3 py-2 text-sm rounded-md transition-colors text-textSecondary hover:bg-surface hover:text-white" active-class="bg-surfaceHover text-white border-l-2 border-accent">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>
            Tenants & Billing
          </router-link>
        </nav>
        
        <div class="text-xs font-mono text-textMuted uppercase tracking-widest mb-4 mt-8">System</div>
        <nav class="space-y-1">
          <router-link to="/metrics" class="flex items-center gap-3 px-3 py-2 text-sm rounded-md transition-colors text-textSecondary hover:bg-surface hover:text-white" active-class="bg-surfaceHover text-white border-l-2 border-accent">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/></svg>
            Global Metrics
          </router-link>
          <router-link to="/debug" class="flex items-center gap-3 px-3 py-2 text-sm rounded-md transition-colors text-textSecondary hover:bg-surface hover:text-white" active-class="bg-surfaceHover text-white border-l-2 border-accent">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="4 17 10 11 4 5"></polyline><line x1="12" y1="19" x2="20" y2="19"></line></svg>
            Debug Logs
          </router-link>
        </nav>
      </div>

      <div class="mt-auto p-4 border-t border-border">
        <button @click="logout" class="flex items-center gap-3 px-3 py-2 text-sm text-red hover:bg-red/10 rounded-md transition-colors w-full">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path><polyline points="16 17 21 12 16 7"></polyline><line x1="21" y1="12" x2="9" y2="12"></line></svg>
          Logout
        </button>
      </div>
    </div>

    <!-- Main Content -->
    <div class="flex-1 flex flex-col overflow-hidden relative mesh-bg">
      <svg style="width:0;height:0;position:absolute;" aria-hidden="true" focusable="false">
        <linearGradient id="gradient-accent" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#6366f1" />
          <stop offset="100%" stop-color="#8b5cf6" />
        </linearGradient>
      </svg>
      <!-- Topbar -->
      <header class="h-16 flex items-center justify-between px-8 border-b border-border glass z-10">
        <div class="flex items-center gap-2 text-sm font-mono text-textSecondary">
          <span>A.L.F.I.E</span>
          <span class="text-textMuted">/</span>
          <span class="text-white">{{ $route.name }}</span>
        </div>
        <div class="flex items-center gap-4">
          <div class="flex items-center gap-2">
            <div class="w-2 h-2 rounded-full bg-green animate-pulse"></div>
            <span class="text-xs font-mono text-green">System Online</span>
          </div>
        </div>
      </header>

      <!-- Scrollable Main -->
      <main class="flex-1 overflow-y-auto p-8">
        <router-view />
      </main>
    </div>
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
