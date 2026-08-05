<template>
  <div class="min-h-screen flex items-center justify-center bg-clientBg bg-[url('/bg-gradient.svg')] bg-cover">
    <div class="glass-panel p-10 w-full max-w-md relative overflow-hidden">
      <!-- Glow effect -->
      <div class="absolute -top-20 -right-20 w-40 h-40 bg-clientPrimary/20 rounded-full blur-3xl"></div>
      
      <div class="relative z-10">
        <h1 class="text-3xl font-bold mb-2 text-white">Welcome back</h1>
        <p class="text-textMuted mb-8">Enter your credentials to access your workspace.</p>
        
        <form @submit.prevent="handleLogin" class="space-y-5">
          <div>
            <label class="block text-sm font-medium text-textSecondary mb-2">Email Address</label>
            <input 
              v-model="email"
              type="email" 
              class="w-full bg-background/50 border border-border rounded-xl px-4 py-3 text-white focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent transition-all placeholder:text-textMuted"
              placeholder="admin@company.com"
              required
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-textSecondary mb-2">Password</label>
            <input 
              v-model="password"
              type="password" 
              class="w-full bg-background/50 border border-border rounded-xl px-4 py-3 text-white focus:outline-none focus:border-accent focus:ring-1 focus:ring-accent transition-all placeholder:text-textMuted"
              placeholder="Enter your password"
              required
            />
          </div>
          
          <div v-if="error" class="text-red-400 text-sm bg-red-400/10 border border-red-400/20 px-4 py-2 rounded-lg">
            {{ error }}
          </div>
          
          <button 
            type="submit"
            class="w-full bg-clientPrimary hover:bg-clientPrimary/90 text-white font-medium py-3 px-4 rounded-xl transition-all shadow-[0_0_15px_rgba(99,102,241,0.4)]"
            :disabled="loading"
          >
            {{ loading ? 'Authenticating...' : 'Access Workspace' }}
          </button>
        </form>
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
