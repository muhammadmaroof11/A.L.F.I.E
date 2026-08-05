<template>
  <div class="min-h-screen flex items-center justify-center bg-bgDeep">
    <div class="bg-bgBase border border-bgSurface p-8 rounded-lg shadow-xl w-full max-w-md">
      <h1 class="text-2xl font-semibold mb-6 text-center text-textPrimary">A.L.F.I.E Super Admin</h1>
      
      <form @submit.prevent="handleLogin" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-textSecondary mb-1">API Key</label>
          <input 
            v-model="apiKey"
            type="password" 
            class="w-full bg-bgElevated border border-bgSurface rounded px-4 py-2 text-textPrimary focus:outline-none focus:border-blue font-mono"
            placeholder="Enter admin key..."
            required
          />
        </div>
        
        <div v-if="error" class="text-red text-sm">
          {{ error }}
        </div>
        
        <button 
          type="submit"
          class="w-full bg-blue hover:bg-blue/80 text-white font-medium py-2 px-4 rounded transition-colors"
          :disabled="loading"
        >
          {{ loading ? 'Authenticating...' : 'Login' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';

const router = useRouter();
const authStore = useAuthStore();

const apiKey = ref('');
const error = ref('');
const loading = ref(false);

const handleLogin = async () => {
  loading.value = true;
  error.value = '';
  
  const success = await authStore.login(apiKey.value);
  if (success) {
    router.push('/');
  } else {
    error.value = 'Invalid API key';
  }
  loading.value = false;
};
</script>
