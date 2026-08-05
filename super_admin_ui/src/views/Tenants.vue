<template>
  <div>
    <div class="flex items-center justify-between mb-8">
      <div>
        <h2 class="text-xl font-mono text-white mb-1">Tenants & Provisioning</h2>
        <p class="text-sm font-mono text-textMuted">Manage client instances and billing limits</p>
      </div>
      <button @click="showModal = true" class="bg-blue hover:bg-blue/80 text-white font-mono text-sm px-4 py-2 flex items-center gap-2 transition-colors">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
        Provision Tenant
      </button>
    </div>

    <!-- Tenants Table -->
    <div class="bg-bgBase border border-bgSurface">
      <table class="w-full text-left font-mono text-sm">
        <thead class="border-b border-bgSurface bg-bgDeep/50">
          <tr>
            <th class="px-6 py-4 text-textMuted font-normal uppercase tracking-wider">Tenant Name</th>
            <th class="px-6 py-4 text-textMuted font-normal uppercase tracking-wider">Niche</th>
            <th class="px-6 py-4 text-textMuted font-normal uppercase tracking-wider">Limit (USD)</th>
            <th class="px-6 py-4 text-textMuted font-normal uppercase tracking-wider">Status</th>
            <th class="px-6 py-4 text-textMuted font-normal uppercase tracking-wider">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="t in tenants" :key="t.tenant_id" class="border-b border-bgSurface hover:bg-bgSurface/20 transition-colors">
            <td class="px-6 py-4 font-medium text-white">{{ t.name }}</td>
            <td class="px-6 py-4 text-blue">{{ t.niche }}</td>
            <td class="px-6 py-4 text-textSecondary">${{ t.credit_limit_usd }}</td>
            <td class="px-6 py-4">
              <span class="px-2 py-1 text-xs bg-green/10 text-green rounded-full">{{ t.status }}</span>
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
    <div v-if="showModal" class="fixed inset-0 bg-black/80 flex items-center justify-center z-50">
      <div class="bg-bgBase border border-bgSurface p-8 max-w-lg w-full">
        <h3 class="text-lg font-mono text-white mb-6">Provision New Tenant</h3>
        
        <form @submit.prevent="submitProvision" class="space-y-4">
          <div>
            <label class="block text-xs font-mono text-textMuted uppercase mb-1">Company Name</label>
            <input v-model="form.name" required class="w-full bg-bgDeep border border-bgSurface px-3 py-2 text-white font-mono text-sm focus:border-blue focus:outline-none" />
          </div>
          
          <div>
            <label class="block text-xs font-mono text-textMuted uppercase mb-1">Niche</label>
            <select v-model="form.niche" required class="w-full bg-bgDeep border border-bgSurface px-3 py-2 text-white font-mono text-sm focus:border-blue focus:outline-none">
              <option value="real_estate">Real Estate</option>
              <option value="car_rental">Car Rental</option>
            </select>
          </div>

          <div>
            <label class="block text-xs font-mono text-textMuted uppercase mb-1">Credit Limit (USD)</label>
            <input v-model="form.credit_limit_usd" type="number" step="0.01" required class="w-full bg-bgDeep border border-bgSurface px-3 py-2 text-white font-mono text-sm focus:border-blue focus:outline-none" />
          </div>

          <div v-if="successData" class="mt-4 p-4 border border-green/30 bg-green/5">
            <div class="text-green text-sm font-mono mb-2">Successfully provisioned!</div>
            <div class="text-xs text-textSecondary font-mono space-y-1">
              <div><span class="text-textMuted">API KEY:</span> <span class="text-white select-all">{{ successData.api_key }}</span></div>
              <div class="text-red mt-1">Make sure to copy this key now, it won't be shown again.</div>
            </div>
          </div>

          <div class="flex justify-end gap-4 mt-8">
            <button type="button" @click="closeModal" class="px-4 py-2 font-mono text-sm text-textMuted hover:text-white">Cancel</button>
            <button type="submit" class="px-4 py-2 font-mono text-sm bg-blue text-white hover:bg-blue/80" :disabled="submitting">
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
