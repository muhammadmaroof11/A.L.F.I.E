<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
      <div class="flex flex-col space-y-1">
        <h2 class="text-2xl font-semibold tracking-tight">Tenant Workspaces</h2>
        <p class="text-sm text-muted-foreground">Manage client accounts, personas, and custom configurations.</p>
      </div>
      <div class="flex items-center gap-3 w-full sm:w-auto">
        <div class="relative w-full sm:w-64">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
          <input type="text" class="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50 pl-9" placeholder="Search tenants..." v-model="searchQuery" />
        </div>
        <button @click="openProvisionModal" class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground shadow hover:bg-primary/90 h-9 px-4 py-2 shrink-0">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="mr-2 h-4 w-4"><path d="M5 12h14"/><path d="M12 5v14"/></svg>
          New Tenant
        </button>
      </div>
    </div>

    <!-- Stats strip -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="rounded-xl glass-panel text-card-foreground p-6 flex flex-col justify-between hover-glow group transition-all duration-300">
        <h3 class="tracking-tight text-sm font-medium text-muted-foreground group-hover:text-primary transition-colors">Total Tenants</h3>
        <div class="text-3xl font-bold font-mono mt-2">{{ totalCount }}</div>
      </div>
      <div class="rounded-xl glass-panel text-card-foreground p-6 flex flex-col justify-between hover-glow group transition-all duration-300">
        <h3 class="tracking-tight text-sm font-medium text-muted-foreground group-hover:text-emerald-500 transition-colors">Active</h3>
        <div class="text-3xl font-bold font-mono mt-2 text-emerald-500 drop-shadow-[0_0_10px_rgba(16,185,129,0.3)]">{{ activeCount }}</div>
      </div>
      <div class="rounded-xl glass-panel text-card-foreground p-6 flex flex-col justify-between hover-glow group transition-all duration-300">
        <h3 class="tracking-tight text-sm font-medium text-muted-foreground group-hover:text-primary transition-colors">Available Niches</h3>
        <div class="text-3xl font-bold font-mono mt-2 text-primary drop-shadow-[0_0_10px_rgba(var(--primary),0.3)]">{{ personas.length }}</div>
      </div>
      <div class="rounded-xl glass-panel text-card-foreground p-6 flex flex-col justify-between hover-glow group transition-all duration-300">
        <h3 class="tracking-tight text-sm font-medium text-muted-foreground group-hover:text-rose-500 transition-colors">Suspended</h3>
        <div class="text-3xl font-bold font-mono mt-2 text-rose-500 drop-shadow-[0_0_10px_rgba(244,63,94,0.3)]">{{ suspendedCount }}</div>
      </div>
    </div>

    <div v-if="loading" class="flex items-center justify-center h-32 text-muted-foreground">
      Loading tenants...
    </div>

    <!-- Data Table -->
    <div v-else class="rounded-xl glass-panel shadow-sm overflow-hidden">
      <div class="w-full overflow-auto">
        <table class="w-full caption-bottom text-sm">
          <thead class="[&_tr]:border-b border-white/5 bg-background/50 backdrop-blur-md">
            <tr class="border-b border-white/5 transition-colors">
              <th class="h-12 px-6 text-left align-middle font-semibold text-muted-foreground w-[30%]">Tenant / Email</th>
              <th class="h-12 px-6 text-left align-middle font-semibold text-muted-foreground">Status</th>
              <th class="h-12 px-6 text-left align-middle font-semibold text-muted-foreground">Plan</th>
              <th class="h-12 px-6 text-left align-middle font-semibold text-muted-foreground">Niche Persona</th>
              <th class="h-12 px-6 text-left align-middle font-semibold text-muted-foreground">Credit Limit</th>
              <th class="h-12 px-6 text-left align-middle font-semibold text-muted-foreground">Created Date</th>
              <th class="h-12 px-6 text-right align-middle font-semibold text-muted-foreground">Actions</th>
            </tr>
          </thead>
          <tbody class="[&_tr:last-child]:border-0">
            <tr v-if="filteredTenants.length === 0">
              <td colspan="7" class="p-8 text-center text-muted-foreground font-mono">No tenants found matching your criteria.</td>
            </tr>
            <tr v-for="tenant in filteredTenants" :key="tenant.tenant_id" :class="['border-b border-white/5 transition-all duration-300 hover:bg-primary/5 hover:shadow-[inset_0_0_20px_rgba(var(--primary),0.05)] group', tenant.status === 'suspended' ? 'opacity-50 grayscale' : '']">
              <td class="p-4 align-middle">
                <div class="flex items-center gap-3">
                  <div class="w-8 h-8 rounded-md flex items-center justify-center text-xs font-bold text-white shrink-0 shadow-sm" :style="getAvatarGradient(tenant.name)">
                    {{ getInitials(tenant.name) }}
                  </div>
                  <div class="flex flex-col">
                    <span class="font-medium text-foreground">{{ tenant.name }}</span>
                    <span class="text-xs text-muted-foreground">{{ tenant.email || tenant.tenant_id.substring(0, 18) + '...' }}</span>
                  </div>
                </div>
              </td>
              <td class="p-4 align-middle">
                <div :class="['inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2', tenant.status === 'active' ? 'border-transparent bg-emerald-500/10 text-emerald-500 hover:bg-emerald-500/20' : 'border-transparent bg-rose-500/10 text-rose-500 hover:bg-rose-500/20']">
                  {{ tenant.status === 'active' ? 'Active' : 'Suspended' }}
                </div>
              </td>
              <td class="p-4 align-middle">
                <div :class="['inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 border-transparent', 
                  (!tenant.subscription_tier || tenant.subscription_tier === 'payg') ? 'bg-secondary text-secondary-foreground hover:bg-secondary/80' : 
                  tenant.subscription_tier === 'plus' ? 'bg-blue-500/10 text-blue-500 hover:bg-blue-500/20' : 
                  'bg-purple-500/10 text-purple-500 hover:bg-purple-500/20']">
                  {{ (!tenant.subscription_tier || tenant.subscription_tier === 'payg') ? 'Pay-As-You-Go' : tenant.subscription_tier === 'plus' ? 'Plus Plan' : 'Pro Plan' }}
                </div>
              </td>
              <td class="p-4 align-middle">
                <div class="inline-flex items-center rounded-full border border-transparent bg-secondary px-2.5 py-0.5 text-xs font-semibold text-secondary-foreground transition-colors hover:bg-secondary/80">
                  {{ tenant.niche }}
                </div>
              </td>
              <td class="p-4 align-middle">
                <div class="flex flex-col">
                  <span class="font-mono text-amber-500 font-medium">${{ tenant.credit_limit_usd.toFixed(2) }}</span>
                  <span class="text-[10px] text-muted-foreground uppercase tracking-wider">Monthly Limit</span>
                </div>
              </td>
              <td class="p-4 align-middle text-muted-foreground text-xs">
                {{ formatDate(tenant.created_at) }}
              </td>
              <td class="p-4 align-middle text-right">
                <div class="flex items-center justify-end gap-2">
                  <button @click="router.push('/tenants/' + tenant.tenant_id)" class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-xs font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 border border-input bg-background shadow-sm hover:bg-accent hover:text-accent-foreground h-8 px-3">
                    <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="mr-2"><path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/></svg>
                    Customize
                  </button>
                  <button v-if="tenant.status === 'active'" @click="toggleStatus(tenant)" class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-xs font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 border border-transparent bg-transparent hover:bg-rose-500/10 text-rose-500 h-8 w-8 px-0" title="Suspend Tenant">
                    <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>
                  </button>
                  <button v-else @click="toggleStatus(tenant)" class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-xs font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 border border-transparent bg-transparent hover:bg-emerald-500/10 text-emerald-500 h-8 w-8 px-0" title="Reactivate Tenant">
                    <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>



    <!-- Provisioning Form Modal -->
    <div v-if="showProvisionModal" class="fixed inset-0 z-50 bg-background/80 backdrop-blur-md flex items-center justify-center">
      <div class="fixed left-[50%] top-[50%] z-50 grid w-full max-w-lg translate-x-[-50%] translate-y-[-50%] gap-4 glass-panel p-8 shadow-2xl sm:rounded-2xl border border-white/10">
        <div class="flex flex-col space-y-1.5 sm:text-left">
          <h2 class="text-lg font-semibold leading-none tracking-tight">Provision New Tenant</h2>
          <p class="text-sm text-muted-foreground">Assign company workspace, credentials, and niche agent.</p>
        </div>

        <form @submit.prevent="provisionTenant" class="space-y-4 py-4">
          <div class="space-y-2">
            <label class="text-sm font-medium leading-none">Company / Tenant Name</label>
            <input type="text" class="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring" v-model="provisionForm.name" placeholder="e.g., Alfie Realty PK" required />
          </div>

          <div class="space-y-2">
            <label class="text-sm font-medium leading-none">Assign Niche Agent Persona</label>
            <select class="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring" v-model="provisionForm.niche" required>
              <option value="" disabled>Select a niche persona</option>
              <option v-for="persona in personas" :key="persona.id" :value="persona.niche_name">
                {{ formatTitle(persona.niche_name) }} ({{ persona.niche_name }})
              </option>
            </select>
          </div>

          <div class="space-y-2">
            <label class="text-sm font-medium leading-none">Client Admin Email Address</label>
            <input type="email" class="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring" v-model="provisionForm.email" placeholder="admin@clientcompany.com" required />
          </div>

          <div class="space-y-2">
            <label class="text-sm font-medium leading-none">Client Admin Password</label>
            <input type="password" class="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring" v-model="provisionForm.password" placeholder="••••••••••••" required />
          </div>

          <div class="space-y-2">
            <label class="text-sm font-medium leading-none">Credit Limit (USD)</label>
            <input type="number" step="0.01" class="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring font-mono" v-model.number="provisionForm.credit_limit_usd" required />
          </div>

          <div class="flex items-center justify-end gap-2 pt-4 border-t border-border mt-6">
            <button type="button" class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 border border-input bg-background shadow-sm hover:bg-accent hover:text-accent-foreground h-9 px-4 py-2" @click="showProvisionModal = false">Cancel</button>
            <button type="submit" class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground shadow hover:bg-primary/90 h-9 px-4 py-2" :disabled="provisioning">
              {{ provisioning ? 'Provisioning...' : 'Provision Tenant' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Provision Success Modal (Show API Key ONCE) -->
    <div v-if="successResult" class="fixed inset-0 z-[100] bg-background/90 backdrop-blur-xl flex items-center justify-center">
      <div class="fixed left-[50%] top-[50%] z-50 grid w-full max-w-lg translate-x-[-50%] translate-y-[-50%] gap-4 glass-panel p-8 shadow-[0_0_50px_rgba(16,185,129,0.15)] sm:rounded-2xl border border-emerald-500/30">
        <div class="flex flex-col space-y-1.5 sm:text-left">
          <h2 class="text-xl font-semibold leading-none tracking-tight text-emerald-500 flex items-center gap-2">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
            Tenant Provisioned!
          </h2>
          <p class="text-sm text-muted-foreground mt-2">Copy and securely store the raw API key below.</p>
        </div>

        <div class="bg-rose-500/10 border-l-4 border-rose-500 p-4 rounded-md mt-4 text-sm text-rose-500">
          <strong>Security Warning:</strong> This raw API key will <u class="font-semibold">never</u> be shown again. Make sure to copy it now!
        </div>

        <div class="space-y-4 py-4">
          <div class="space-y-2">
            <label class="text-sm font-medium leading-none">Generated Tenant API Key</label>
            <div class="flex gap-2">
              <input type="text" class="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm font-mono text-amber-500" :value="successResult.api_key" readonly />
              <button class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring border border-input bg-background shadow-sm hover:bg-accent hover:text-accent-foreground h-9 px-4 py-2 shrink-0" @click="copyToClipboard(successResult.api_key)">Copy</button>
            </div>
          </div>

          <div class="space-y-2">
            <label class="text-sm font-medium leading-none">SIP Room Metadata (JSON)</label>
            <textarea class="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm shadow-sm font-mono text-xs text-muted-foreground" :value="successResult.sip_room_metadata" readonly rows="3"></textarea>
          </div>
        </div>

        <div class="flex items-center justify-end gap-2 pt-4 mt-2">
          <button class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring bg-primary text-primary-foreground shadow hover:bg-primary/90 h-9 px-4 py-2 w-full" @click="closeSuccessModal">Done & Close</button>
        </div>
      </div>
    </div>

    <!-- Custom Confirm Modal -->
    <div v-if="confirmDialog.show" class="fixed inset-0 z-[110] bg-background/80 backdrop-blur-md flex items-center justify-center animate-in fade-in duration-200">
      <div class="fixed left-[50%] top-[50%] z-50 grid w-full max-w-md translate-x-[-50%] translate-y-[-50%] gap-4 glass-panel p-6 shadow-2xl sm:rounded-2xl border border-white/10 animate-in zoom-in-95 duration-200">
        <div class="flex flex-col space-y-1.5 sm:text-left">
          <h2 class="text-lg font-semibold leading-none tracking-tight">{{ confirmDialog.title }}</h2>
          <p class="text-sm text-muted-foreground mt-2">{{ confirmDialog.message }}</p>
        </div>
        <div class="flex items-center justify-end gap-2 pt-4">
          <button @click="confirmDialog.cancel" class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors h-9 px-4 py-2 border border-input bg-background shadow-sm hover:bg-accent hover:text-accent-foreground">Cancel</button>
          <button @click="confirmDialog.confirm" class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors h-9 px-4 py-2 bg-primary text-primary-foreground shadow hover:bg-primary/90">Confirm</button>
        </div>
      </div>
    </div>

    <!-- Toast Notifications -->
    <div class="fixed bottom-6 right-6 z-[120] flex flex-col gap-3">
      <div v-for="toast in toasts" :key="toast.id" :class="['px-4 py-3 rounded-xl shadow-2xl border text-sm font-medium transition-all duration-300 animate-in slide-in-from-right-8 fade-in flex items-center gap-3 backdrop-blur-xl', toast.type === 'error' ? 'bg-rose-500/10 border-rose-500/30 text-rose-500' : 'bg-emerald-500/10 border-emerald-500/30 text-emerald-500']">
        <svg v-if="toast.type === 'error'" xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" x2="12" y1="8" y2="12"/><line x1="12" x2="12.01" y1="16" y2="16"/></svg>
        <svg v-else xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
        {{ toast.message }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import api from '../services/api';

const router = useRouter();
const tenants = ref([]);
const personas = ref([]);
const fishAudioVoices = ref([]);
const loading = ref(true);
const searchQuery = ref('');

const showProvisionModal = ref(false);
const provisioning = ref(false);
const successResult = ref(null);
const confirmDialog = ref({ show: false, title: '', message: '', confirm: null, cancel: null });
const toasts = ref([]);

const showToast = (message, type = 'success') => {
  const id = Date.now();
  toasts.value.push({ id, message, type });
  setTimeout(() => {
    toasts.value = toasts.value.filter(t => t.id !== id);
  }, 4000);
};

const customConfirm = (title, message) => {
  return new Promise((resolve) => {
    confirmDialog.value = {
      show: true,
      title,
      message,
      confirm: () => {
        confirmDialog.value.show = false;
        resolve(true);
      },
      cancel: () => {
        confirmDialog.value.show = false;
        resolve(false);
      }
    };
  });
};

const provisionForm = ref({
  name: '',
  niche: 'real_estate',
  email: '',
  password: '',
  credit_limit_usd: 50.00
});

const formatTitle = (str) => {
  if (!str) return '';
  return str.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
};

const formatDate = (isoStr) => {
  if (!isoStr) return 'N/A';
  return new Date(isoStr).toLocaleDateString();
};

const getInitials = (name) => {
  if (!name) return '??';
  const parts = name.trim().split(' ');
  if (parts.length >= 2) return (parts[0][0] + parts[1][0]).toUpperCase();
  return name.substring(0, 2).toUpperCase();
};

const getAvatarGradient = (name) => {
  const gradients = [
    'background:linear-gradient(135deg,#3B82F6,#8B5CF6);',
    'background:linear-gradient(135deg,#F59E0B,#EF4444);',
    'background:linear-gradient(135deg,#22C55E,#06B6D4);',
    'background:linear-gradient(135deg,#8B5CF6,#EC4899);'
  ];
  let hash = 0;
  for (let i = 0; i < (name || '').length; i++) hash += name.charCodeAt(i);
  return gradients[hash % gradients.length];
};

const fetchTenants = async () => {
  loading.value = true;
  try {
    const res = await api.get('/api/super/tenants');
    tenants.value = res.data;
  } catch (err) {
    console.error('Failed to fetch tenants:', err);
  } finally {
    loading.value = false;
  }
};

const fetchPersonas = async () => {
  try {
    const res = await api.get('/api/super/personas');
    personas.value = res.data;
  } catch (err) {
    console.error('Failed to fetch personas:', err);
  }
};

const fetchVoices = async () => {
  try {
    const res = await api.get('/api/super/fish-audio/voices');
    fishAudioVoices.value = res.data?.items || [];
  } catch (err) {
    console.error('Failed to fetch voices:', err);
  }
};

const totalCount = computed(() => tenants.value.length);
const activeCount = computed(() => tenants.value.filter(t => t.status === 'active').length);
const suspendedCount = computed(() => tenants.value.filter(t => t.status === 'suspended').length);

const filteredTenants = computed(() => {
  if (!searchQuery.value.trim()) return tenants.value;
  const q = searchQuery.value.toLowerCase();
  return tenants.value.filter(t => 
    (t.name && t.name.toLowerCase().includes(q)) ||
    (t.email && t.email.toLowerCase().includes(q)) ||
    (t.niche && t.niche.toLowerCase().includes(q))
  );
});

const openProvisionModal = () => {
  provisionForm.value = {
    name: '',
    niche: personas.value.length > 0 ? personas.value[0].niche_name : 'real_estate',
    email: '',
    password: '',
    credit_limit_usd: 50.00
  };
  showProvisionModal.value = true;
};



const provisionTenant = async () => {
  provisioning.value = true;
  try {
    const res = await api.post('/api/super/provision', provisionForm.value);
    successResult.value = res.data;
    showProvisionModal.value = false;
    fetchTenants();
    showToast('Tenant provisioned successfully.');
  } catch (err) {
    showToast(err.response?.data?.detail || 'Failed to provision tenant.', 'error');
  } finally {
    provisioning.value = false;
  }
};

const toggleStatus = async (tenant) => {
  const newStatus = tenant.status === 'active' ? 'suspended' : 'active';
  const confirmed = await customConfirm(
    'Confirm Status Change',
    `Are you sure you want to change the status of ${tenant.name} to ${newStatus}?`
  );
  if (!confirmed) return;

  try {
    await api.patch(`/api/super/tenants/${tenant.tenant_id}`, { status: newStatus });
    fetchTenants();
    showToast(`Tenant status updated to ${newStatus}.`);
  } catch (err) {
    showToast(err.response?.data?.detail || 'Failed to update tenant status.', 'error');
  }
};

const copyToClipboard = (text) => {
  navigator.clipboard.writeText(text);
  showToast('Copied to clipboard!');
};

const closeSuccessModal = () => {
  successResult.value = null;
};

onMounted(() => {
  fetchTenants();
  fetchPersonas();
  fetchVoices();
});
</script>
