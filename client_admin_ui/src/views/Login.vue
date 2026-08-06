<template>
  <div class="min-h-screen flex items-center justify-center bg-muted/30 px-4">
    <div class="w-full max-w-[400px]">
      <div class="rounded-xl border bg-card text-card-foreground shadow flex flex-col items-center p-8 space-y-6">
        
        <div class="flex flex-col items-center space-y-2 text-center">
          <div class="w-12 h-12 bg-primary rounded-xl flex items-center justify-center mb-2 shadow-sm">
            <span class="text-primary-foreground font-bold text-2xl font-sans">A</span>
          </div>
          <h1 class="text-2xl font-semibold tracking-tight">Client Portal</h1>
          <p class="text-sm text-muted-foreground">Sign in to your workspace</p>
        </div>
        
        <form @submit.prevent="handleLogin" class="w-full space-y-4">
          <div class="space-y-2">
            <label class="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">Email Address</label>
            <input 
              v-model="email"
              type="email" 
              class="flex h-10 w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
              placeholder="admin@company.com"
              required
            />
          </div>

          <div class="space-y-2">
            <div class="flex items-center justify-between">
              <label class="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">Password</label>
            </div>
            <input 
              v-model="password"
              type="password" 
              class="flex h-10 w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
              placeholder="••••••••"
              required
            />
          </div>
          
          <div v-if="error" class="text-[13px] font-medium text-destructive">
            {{ error }}
          </div>
          
          <button 
            type="submit"
            class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground shadow hover:bg-primary/90 h-10 w-full mt-2"
            :disabled="loading"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="mr-2 h-4 w-4 animate-spin" v-if="loading"><path d="M21 12a9 9 0 1 1-6.219-8.56"/></svg>
            {{ loading ? 'Authenticating...' : 'Sign In' }}
          </button>
        </form>

      </div>
      <div class="mt-8 text-center text-xs text-muted-foreground">
        &copy; 2026 A.L.F.I.E Enterprise Voice Intelligence
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';

const router = useRouter();
const authStore = useAuthStore();

const email = ref('');
const password = ref('');
const error = ref('');
const loading = ref(false);

const handleLogin = async () => {
  loading.value = true;
  error.value = '';
  
  const success = await authStore.login(email.value, password.value);
  if (success) {
    router.push('/');
  } else {
    error.value = 'Invalid email or password';
  }
  loading.value = false;
};
</script>
