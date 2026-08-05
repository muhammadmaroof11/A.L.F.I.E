<template>
  <div>
    <div class="flex items-center justify-between mb-8">
      <div>
        <h2 class="text-3xl font-display font-bold text-white mb-2">Tenants & Provisioning</h2>
        <p class="text-sm text-textSecondary">Manage client instances and billing limits</p>
      </div>
      <button @click="showModal = true" class="btn-glow px-5 py-2.5 rounded-lg flex items-center gap-2 text-white font-medium text-sm transition-all">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
        Provision Tenant
      </button>
    </div>

    <!-- Tenants Table -->
    <div class="glass overflow-hidden rounded-xl">
      <table class="w-full text-left text-sm">
        <thead class="border-b border-border bg-surface">
          <tr>
            <th class="px-6 py-4 text-textMuted font-medium tracking-wider">Tenant Name</th>
            <th class="px-6 py-4 text-textMuted font-medium tracking-wider">Email</th>
            <th class="px-6 py-4 text-textMuted font-medium tracking-wider">Niche</th>
            <th class="px-6 py-4 text-textMuted font-medium tracking-wider">Limit (USD)</th>
            <th class="px-6 py-4 text-textMuted font-medium tracking-wider">Status</th>
            <th class="px-6 py-4 text-textMuted font-medium tracking-wider">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="t in tenants" :key="t.tenant_id" class="border-b border-border hover:bg-surfaceHover transition-colors">
            <td class="px-6 py-4 font-medium text-white">{{ t.name }}</td>
            <td class="px-6 py-4 text-textSecondary">{{ t.email || 'N/A' }}</td>
            <td class="px-6 py-4 text-accentSecondary">{{ t.niche }}</td>
            <td class="px-6 py-4 text-textSecondary font-mono">${{ t.credit_limit_usd }}</td>
            <td class="px-6 py-4">
              <span class="px-3 py-1 text-xs bg-green/10 text-green rounded-full font-medium border border-green/20">{{ t.status }}</span>
            </td>
            <td class="px-6 py-4">
              <button class="text-textMuted hover:text-white transition-colors">Edit</button>
            </td>
          </tr>
          <tr v-if="tenants.length === 0 && !loading">
            <td colspan="5" class="px-6 py-8 text-center text-textMuted">No tenants found.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Provisioning Modal -->
    <div v-if="showModal" class="fixed inset-0 bg-background/80 backdrop-blur-sm flex items-center justify-center z-50 animate-in">
      <div class="glass-elevated rounded-2xl p-8 max-w-lg w-full m-4">
        <h3 class="text-2xl font-display font-bold text-white mb-6">Provision New Tenant</h3>
        
        <form @submit.prevent="submitProvision" class="space-y-5">
          <div>
            <label class="block text-sm font-medium text-textSecondary mb-2">Company Name</label>
            <input v-model="form.name" required class="w-full bg-background/50 border border-border rounded-lg px-4 py-2.5 text-white text-sm focus:border-accent focus:ring-1 focus:ring-accent outline-none transition-all" placeholder="Enter company name" />
          </div>

          <div>
            <label class="block text-sm font-medium text-textSecondary mb-2">Email Address</label>
            <input v-model="form.email" type="email" required class="w-full bg-background/50 border border-border rounded-lg px-4 py-2.5 text-white text-sm focus:border-accent focus:ring-1 focus:ring-accent outline-none transition-all" placeholder="admin@client.com" />
          </div>

          <div>
            <label class="block text-sm font-medium text-textSecondary mb-2">Password</label>
            <input v-model="form.password" type="password" required class="w-full bg-background/50 border border-border rounded-lg px-4 py-2.5 text-white text-sm focus:border-accent focus:ring-1 focus:ring-accent outline-none transition-all" placeholder="Secure password" />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-textSecondary mb-2">Niche</label>
            <select v-model="form.niche" required class="w-full bg-background/50 border border-border rounded-lg px-4 py-2.5 text-white text-sm focus:border-accent focus:ring-1 focus:ring-accent outline-none transition-all appearance-none">
              <option value="real_estate">Real Estate</option>
              <option value="car_rental">Car Rental</option>
            </select>
          </div>

          <div>
            <label class="block text-sm font-medium text-textSecondary mb-2">Credit Limit (USD)</label>
            <input v-model="form.credit_limit_usd" type="number" step="0.01" required class="w-full bg-background/50 border border-border rounded-lg px-4 py-2.5 text-white text-sm font-mono focus:border-accent focus:ring-1 focus:ring-accent outline-none transition-all" />
          </div>

          <div v-if="successData" class="mt-6 p-5 border border-green/30 bg-green/10 rounded-xl">
            <div class="text-green font-medium mb-3 flex items-center gap-2">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
              Successfully provisioned!
            </div>
            <div class="space-y-2">
              <div class="text-sm text-textSecondary">API KEY:</div>
              <div class="bg-background/80 border border-border p-3 rounded-lg text-white font-mono text-sm break-all select-all">{{ successData.api_key }}</div>
              <div class="text-red text-sm mt-2 flex items-center gap-2">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>
                Copy this key now. It cannot be recovered.
              </div>
            </div>
          </div>

          <div class="flex justify-end gap-3 mt-8">
            <button type="button" @click="closeModal" class="px-5 py-2.5 rounded-lg text-sm font-medium text-textSecondary hover:bg-surfaceHover transition-colors">Cancel</button>
            <button type="submit" class="btn-glow px-5 py-2.5 rounded-lg text-sm font-medium text-white transition-all" :disabled="submitting">
              {{ submitting ? 'Provisioning...' : 'Provision' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '../services/api';

const tenants = ref([]);
const loading = ref(true);
const showModal = ref(false);
const submitting = ref(false);
const successData = ref(null);

const form = ref({
  name: '',
  email: '',
  password: '',
  niche: 'real_estate',
  credit_limit_usd: 50.00
});

const loadTenants = async () => {
  loading.value = true;
  try {
    const res = await api.get('/api/super/tenants');
    tenants.value = res.data;
  } catch(e) {
    console.error(e);
  }
  loading.value = false;
};

const submitProvision = async () => {
  submitting.value = true;
  successData.value = null;
  try {
    const res = await api.post('/api/super/provision', form.value);
    successData.value = res.data;
    loadTenants(); // refresh list
    form.value.name = '';
    form.value.email = '';
    form.value.password = '';
  } catch(e) {
    console.error(e);
  }
  submitting.value = false;
};

const closeModal = () => {
  showModal.value = false;
  successData.value = null;
};

onMounted(() => {
  loadTenants();
});
</script>
