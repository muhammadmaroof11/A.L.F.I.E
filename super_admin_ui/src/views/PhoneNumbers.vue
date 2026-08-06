<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
      <div class="flex flex-col space-y-1">
        <h2 class="text-2xl font-semibold tracking-tight">SIP & Phone Number Router</h2>
        <p class="text-sm text-muted-foreground">Map inbound DID phone numbers directly to client tenants and niche agent personas.</p>
      </div>
      <button @click="openModal" class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground shadow hover:bg-primary/90 h-9 px-4 py-2 shrink-0">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="mr-2 h-4 w-4"><path d="M5 12h14"/><path d="M12 5v14"/></svg>
        Map New Phone Number
      </button>
    </div>

    <div v-if="loading" class="flex items-center justify-center h-32 text-muted-foreground">
      Loading phone numbers...
    </div>

    <!-- Data Table -->
    <div v-else class="rounded-md border bg-card shadow-sm">
      <div class="w-full overflow-auto">
        <table class="w-full caption-bottom text-sm">
          <thead class="[&_tr]:border-b bg-muted/50">
            <tr class="border-b transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted">
              <th class="h-10 px-4 text-left align-middle font-medium text-muted-foreground w-[25%]">Phone Number (DID)</th>
              <th class="h-10 px-4 text-left align-middle font-medium text-muted-foreground w-[25%]">Assigned Tenant</th>
              <th class="h-10 px-4 text-left align-middle font-medium text-muted-foreground">Niche Persona</th>
              <th class="h-10 px-4 text-left align-middle font-medium text-muted-foreground">SIP Provider</th>
              <th class="h-10 px-4 text-right align-middle font-medium text-muted-foreground">Actions</th>
            </tr>
          </thead>
          <tbody class="[&_tr:last-child]:border-0">
            <tr v-if="phoneNumbers.length === 0">
              <td colspan="5" class="p-8 text-center text-muted-foreground">No phone numbers mapped yet. Click above to bind a phone number to a tenant.</td>
            </tr>
            <tr v-for="item in phoneNumbers" :key="item.id" class="border-b transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted">
              <td class="p-4 align-middle">
                <span class="font-mono text-sm font-semibold text-amber-500 tracking-wide">{{ item.phone_number }}</span>
              </td>
              <td class="p-4 align-middle">
                <span class="font-medium text-foreground truncate block max-w-[200px]" :title="item.tenant_id">{{ item.tenant_id }}</span>
              </td>
              <td class="p-4 align-middle">
                <span class="inline-flex items-center rounded-full border border-transparent bg-secondary px-2.5 py-0.5 text-xs font-semibold text-secondary-foreground transition-colors hover:bg-secondary/80">
                  {{ item.niche }}
                </span>
              </td>
              <td class="p-4 align-middle text-muted-foreground text-xs">
                {{ item.provider || 'LiveKit SIP Trunk' }}
              </td>
              <td class="p-4 align-middle text-right">
                <button @click="deleteNumber(item.id)" class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-xs font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 hover:bg-rose-500/10 text-rose-500 h-8 w-8 px-0" title="Unbind Number">
                  <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/></svg>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Modal Form -->
    <div v-if="showModal" class="fixed inset-0 z-50 bg-background/80 backdrop-blur-sm flex items-center justify-center">
      <div class="fixed left-[50%] top-[50%] z-50 grid w-full max-w-md translate-x-[-50%] translate-y-[-50%] gap-4 border bg-background p-6 shadow-lg sm:rounded-lg">
        <div class="flex flex-col space-y-1.5 sm:text-left">
          <h2 class="text-lg font-semibold leading-none tracking-tight">Map Inbound Phone Number</h2>
          <p class="text-sm text-muted-foreground">Route calls from a specific DID to a client workspace.</p>
        </div>

        <form @submit.prevent="savePhoneNumber" class="space-y-4 py-4">
          <div class="space-y-2">
            <label class="text-sm font-medium leading-none">Phone Number</label>
            <input type="text" class="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring font-mono" v-model="form.phone_number" placeholder="+18005550199" required />
            <p class="text-[11px] text-muted-foreground">Use E.164 format (e.g., +18005550199)</p>
          </div>

          <div class="space-y-2">
            <label class="text-sm font-medium leading-none">Assign to Tenant Workspace</label>
            <select class="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring" v-model="form.tenant_id" required>
              <option value="" disabled>Select tenant</option>
              <option v-for="tenant in tenants" :key="tenant.tenant_id" :value="tenant.tenant_id">
                {{ tenant.name }} ({{ tenant.tenant_id }})
              </option>
            </select>
          </div>

          <div class="space-y-2">
            <label class="text-sm font-medium leading-none">Niche Persona</label>
            <select class="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring" v-model="form.niche" required>
              <option value="real_estate">Real Estate (real_estate)</option>
              <option value="car_rental">Car Rental (car_rental)</option>
              <option v-for="p in personas" :key="p.id" :value="p.niche_name">{{ p.niche_name }}</option>
            </select>
          </div>

          <div class="flex items-center justify-end gap-2 pt-4 border-t border-border mt-6">
            <button type="button" class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 border border-input bg-background shadow-sm hover:bg-accent hover:text-accent-foreground h-9 px-4 py-2" @click="showModal = false">Cancel</button>
            <button type="submit" class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground shadow hover:bg-primary/90 h-9 px-4 py-2">Save Mapping</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '../services/api';

const phoneNumbers = ref([]);
const tenants = ref([]);
const personas = ref([]);
const loading = ref(true);
const showModal = ref(false);

const form = ref({
  phone_number: '',
  tenant_id: '',
  niche: 'real_estate',
  provider: 'LiveKit SIP Trunk'
});

const fetchData = async () => {
  loading.value = true;
  try {
    const [numRes, tenRes, perRes] = await Promise.all([
      api.get('/api/super/phone-numbers'),
      api.get('/api/super/tenants'),
      api.get('/api/super/personas')
    ]);
    phoneNumbers.value = numRes.data || [];
    tenants.value = tenRes.data || [];
    personas.value = perRes.data || [];
    if (tenants.value.length > 0) form.value.tenant_id = tenants.value[0].tenant_id;
  } catch (err) {
    console.warn('Could not fetch phone numbers:', err);
  } finally {
    loading.value = false;
  }
};

const openModal = () => {
  if (tenants.value.length > 0) form.value.tenant_id = tenants.value[0].tenant_id;
  showModal.value = true;
};

const savePhoneNumber = async () => {
  try {
    await api.post('/api/super/phone-numbers', form.value);
    showModal.value = false;
    form.value.phone_number = '';
    fetchData();
  } catch (err) {
    alert(err.response?.data?.detail || 'Failed to map phone number.');
  }
};

const deleteNumber = async (id) => {
  if (!confirm('Are you sure you want to unbind this phone number?')) return;
  try {
    await api.delete(`/api/super/phone-numbers/${id}`);
    fetchData();
  } catch (err) {
    alert('Failed to delete number.');
  }
};

onMounted(() => {
  fetchData();
});
</script>
