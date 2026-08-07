<template>
  <div class="space-y-6 pb-12 animate-in fade-in slide-in-from-bottom-4 duration-500 w-full">
    <!-- Header with Back Button -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border/50 pb-6">
      <div class="flex items-center gap-4">
        <router-link to="/tenants" class="inline-flex items-center justify-center w-9 h-9 rounded-full bg-background border border-border/50 shadow-sm hover:bg-muted text-foreground transition-all hover:scale-105 hover:shadow-md">
          <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m15 18-6-6 6-6"/></svg>
        </router-link>
        <div class="flex flex-col">
          <h2 class="text-2xl font-bold tracking-tight text-foreground flex items-center gap-3">
            {{ tenant?.name || 'Loading Configuration...' }}
            <span v-if="tenant" class="text-[10px] uppercase tracking-widest font-mono font-semibold px-2 py-1 bg-primary/10 text-primary border border-primary/20 rounded-md">{{ tenant.niche }}</span>
          </h2>
          <p class="text-sm text-muted-foreground mt-1">Tenant Agent Configuration & Overrides</p>
        </div>
      </div>
      
      <!-- Actions -->
      <div class="flex items-center gap-3" v-if="!loading">
        <button type="button" @click="cancelChanges" :class="['inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors h-10 px-5 border border-input bg-background shadow-sm text-foreground', !isDirty ? 'opacity-50 cursor-not-allowed' : 'hover:bg-muted']" :disabled="!isDirty || saving">
          Cancel
        </button>
        <button type="submit" form="tenant-config-form" :class="['inline-flex items-center justify-center rounded-md text-sm font-medium transition-all bg-primary text-primary-foreground h-10 px-6 shadow-sm', !isDirty ? 'opacity-50 cursor-not-allowed' : 'hover:bg-primary/90 hover:scale-105 shadow-[0_4px_20px_rgba(var(--primary),0.4)]']" :disabled="!isDirty || saving">
          <svg v-if="saving" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
          <svg v-else xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="mr-2"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/><polyline points="17 21 17 13 7 13 7 21"/><polyline points="7 3 7 8 15 8"/></svg>
          {{ saving ? 'Saving...' : 'Save Configuration' }}
        </button>
      </div>
    </div>

    <div v-if="loading" class="flex justify-center items-center h-64">
      <div class="flex flex-col items-center gap-4">
        <div class="animate-spin w-8 h-8 border-2 border-primary border-t-transparent rounded-full drop-shadow-[0_0_10px_rgba(var(--primary),0.5)]"></div>
        <p class="text-sm text-muted-foreground animate-pulse">Loading tenant data...</p>
      </div>
    </div>

    <form v-else id="tenant-config-form" @submit.prevent="saveConfig" class="flex flex-col gap-8 w-full">
      
      <div class="columns-1 xl:columns-2 gap-6 w-full space-y-6">
        <!-- Behavior & Context -->
      <div class="rounded-xl glass-panel border border-border/60 shadow-lg overflow-hidden transition-all hover:border-primary/30 group break-inside-avoid">
        <div class="p-6 border-b border-border/40 bg-gradient-to-r from-muted/30 to-transparent">
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center text-primary group-hover:scale-110 transition-transform">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
            </div>
            <div>
              <h3 class="font-semibold text-lg text-foreground">Behavior & Context</h3>
              <p class="text-xs text-muted-foreground mt-0.5">Define how the agent acts and greets the caller.</p>
            </div>
          </div>
        </div>
        <div class="p-6 space-y-6 bg-background/20">
          <div class="space-y-2">
            <label class="text-sm font-semibold text-foreground">Greeting Message Override</label>
            <input type="text" class="flex h-11 w-full rounded-md border border-input bg-background px-4 py-2 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus:border-primary placeholder:text-muted-foreground" v-model="form.greeting_message" placeholder="e.g., Hello! Thank you for calling Alfie Realty..." />
            <p class="text-xs text-muted-foreground">The first sentence the agent says when answering the phone.</p>
          </div>

          <div class="space-y-2">
            <label class="text-sm font-semibold text-foreground">System Prompt Override</label>
            <textarea class="flex min-h-[140px] w-full rounded-md border border-input bg-background px-4 py-3 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus:border-primary font-mono text-xs placeholder:text-muted-foreground leading-relaxed" v-model="form.system_prompt_override" placeholder="Add specific client rules (e.g. Always emphasize 5% discount for upfront payments...)"></textarea>
            <p class="text-xs text-muted-foreground">This is appended to the base niche prompt. Use this for client-specific business rules.</p>
          </div>
        </div>
      </div>

      <!-- Agents Roster -->
      <div class="rounded-xl glass-panel border border-border/60 shadow-lg overflow-hidden transition-all hover:border-emerald-500/30 group break-inside-avoid">
        <div class="p-6 border-b border-border/40 bg-gradient-to-r from-emerald-500/5 to-transparent">
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 rounded-lg bg-emerald-500/10 flex items-center justify-center text-emerald-500 group-hover:scale-110 transition-transform">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>
            </div>
            <div>
              <h3 class="font-semibold text-lg text-foreground">Tenant Agents</h3>
              <p class="text-xs text-muted-foreground mt-0.5">Configured agents for this tenant (Read-Only).</p>
            </div>
          </div>
        </div>
        <div class="p-0 overflow-x-auto bg-background/20">
          <table class="w-full text-sm text-left">
            <thead class="text-xs uppercase bg-muted/30 text-muted-foreground border-b border-border/40">
              <tr>
                <th class="px-6 py-4 font-medium tracking-wider">Agent Name</th>
                <th class="px-6 py-4 font-medium tracking-wider">Niche</th>
                <th class="px-6 py-4 font-medium tracking-wider">Model</th>
                <th class="px-6 py-4 font-medium tracking-wider">Phone #</th>
                <th class="px-6 py-4 font-medium tracking-wider text-right">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-border/40">
              <tr v-for="agent in agents" :key="agent.agent_id" class="hover:bg-muted/10 transition-colors">
                <td class="px-6 py-4 font-medium text-foreground">{{ agent.name }}</td>
                <td class="px-6 py-4">
                  <span class="px-2 py-1 text-[10px] uppercase font-bold tracking-wider rounded-md bg-accent text-accent-foreground border border-accent/50">{{ agent.niche }}</span>
                </td>
                <td class="px-6 py-4 text-xs font-mono text-muted-foreground">{{ agent.llm_model || 'Default' }}</td>
                <td class="px-6 py-4 text-xs font-mono text-muted-foreground">
                  <span v-if="agent.phone_numbers && agent.phone_numbers.length" v-for="phone in agent.phone_numbers" :key="phone" class="block">
                    {{ phone }}
                  </span>
                  <span v-else class="text-muted-foreground/50">Unassigned</span>
                </td>
                <td class="px-6 py-4 text-right">
                  <button @click.prevent="openEditAgent(agent)" class="text-sm font-medium text-blue-500 hover:text-blue-400">Edit</button>
                </td>
              </tr>
              <tr v-if="!agents || agents.length === 0">
                <td colspan="5" class="px-6 py-8 text-center text-muted-foreground">No agents provisioned for this tenant.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Advanced & Limits -->
      <div class="rounded-xl glass-panel border border-border/60 shadow-lg overflow-hidden transition-all hover:border-rose-500/30 group break-inside-avoid">
        <div class="p-6 border-b border-border/40 bg-gradient-to-r from-rose-500/5 to-transparent">
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 rounded-lg bg-rose-500/10 flex items-center justify-center text-rose-500 group-hover:scale-110 transition-transform">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/></svg>
            </div>
            <div>
              <h3 class="font-semibold text-lg text-foreground">Advanced Limits</h3>
              <p class="text-xs text-muted-foreground mt-0.5">Usage and guardrails.</p>
            </div>
          </div>
        </div>
        <div class="p-6 grid grid-cols-1 md:grid-cols-2 gap-8 bg-background/20">
          <div class="space-y-2">
            <label class="text-sm font-semibold text-foreground">Max Call Duration (Minutes)</label>
            <input type="number" class="flex h-11 w-full rounded-md border border-input bg-background px-4 py-2 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-rose-500 focus:border-rose-500 font-mono font-bold" v-model.number="form.max_call_duration_min" />
          </div>
        </div>
      </div>
      
      <!-- Subscription Management -->
      <div class="rounded-xl glass-panel border border-border/60 shadow-lg overflow-hidden transition-all hover:border-blue-500/30 group break-inside-avoid">
        <div class="p-6 border-b border-border/40 bg-gradient-to-r from-blue-500/5 to-transparent">
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 rounded-lg bg-blue-500/10 flex items-center justify-center text-blue-500 group-hover:scale-110 transition-transform">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>
            </div>
            <div>
              <h3 class="font-semibold text-lg text-foreground">Subscription Management</h3>
              <p class="text-xs text-muted-foreground mt-0.5">Manage billing tiers and limits.</p>
            </div>
          </div>
        </div>
        <div class="p-6 space-y-6">
          <div class="space-y-2">
            <label class="text-sm font-semibold text-foreground">Subscription Tier</label>
            <select class="flex h-11 w-full rounded-md border border-input bg-background px-4 py-2 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus:border-blue-500" v-model="form.subscription_tier">
              <option value="payg">Pay As You Go ($0/mo, $0.15/min)</option>
              <option value="plus">Plus ($99/mo, 1000 mins included)</option>
              <option value="pro">Pro ($299/mo, 4000 mins included)</option>
              <option value="custom">Enterprise Custom</option>
            </select>
          </div>

          <div v-if="form.subscription_tier === 'custom'" class="grid grid-cols-1 md:grid-cols-3 gap-4 animate-in fade-in zoom-in-95 duration-300">
            <div class="space-y-2">
              <label class="text-sm font-semibold text-foreground flex items-center gap-2">
                Custom Monthly Price
                <span class="text-xs bg-emerald-500/20 text-emerald-500 px-2 py-0.5 rounded-full">USD</span>
              </label>
              <input type="number" step="0.01" class="flex h-11 w-full rounded-md border border-input bg-background px-4 py-2 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus:border-blue-500 font-mono" v-model.number="form.custom_monthly_price" />
            </div>
            <div class="space-y-2">
              <label class="text-sm font-semibold text-foreground">Custom Included Minutes</label>
              <input type="number" class="flex h-11 w-full rounded-md border border-input bg-background px-4 py-2 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus:border-blue-500 font-mono" v-model.number="form.custom_included_minutes" />
            </div>
            <div class="space-y-2">
              <label class="text-sm font-semibold text-foreground">Custom Per-Minute Rate ($)</label>
              <input type="number" step="0.01" class="flex h-11 w-full rounded-md border border-input bg-background px-4 py-2 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus:border-blue-500 font-mono" v-model.number="form.custom_per_minute_rate" />
            </div>
          </div>

          <div class="space-y-2">
            <label class="text-sm font-semibold text-foreground">Included Minutes Balance</label>
            <input type="number" class="flex h-11 w-full rounded-md border border-input bg-background px-4 py-2 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus:border-blue-500" v-model.number="form.included_minutes_balance" />
            <p class="text-xs text-muted-foreground">Manual override for remaining included monthly minutes.</p>
          </div>
        </div>
      </div>
      </div> <!-- End of grid -->
    </form>

    <!-- Edit Agent Modal -->
    <div v-if="isEditingAgent" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-background/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div class="bg-card w-full max-w-lg rounded-xl shadow-2xl border border-border/60 overflow-hidden flex flex-col">
        <div class="px-6 py-4 border-b border-border/40 flex justify-between items-center bg-muted/20">
          <h3 class="text-lg font-semibold text-foreground">Edit Agent Configurations</h3>
          <button @click="closeEditAgent" class="text-muted-foreground hover:text-foreground transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
          </button>
        </div>
        <div class="p-6 space-y-4">
          <div class="space-y-2">
            <label class="text-sm font-semibold text-foreground">Agent Name</label>
            <input type="text" v-model="editingAgentData.name" class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500" />
          </div>
          <div class="space-y-2">
            <label class="text-sm font-semibold text-foreground">Voice ID (ElevenLabs / PlayHT)</label>
            <input type="text" v-model="editingAgentData.tts_voice_id" class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500 font-mono" />
          </div>
          <div class="space-y-2">
            <label class="text-sm font-semibold text-foreground flex justify-between">
              System Prompt Override
              <span class="text-xs text-muted-foreground font-normal">Overrides Niche Prompt</span>
            </label>
            <textarea v-model="editingAgentData.system_prompt_override" rows="5" class="flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500 resize-y" placeholder="You are an AI assistant..."></textarea>
          </div>
        </div>
        <div class="px-6 py-4 border-t border-border/40 bg-muted/20 flex justify-end gap-3">
          <button @click="closeEditAgent" class="px-4 py-2 text-sm font-medium text-foreground bg-secondary hover:bg-secondary/80 rounded-md transition-colors">Cancel</button>
          <button @click="saveAgent" :disabled="savingAgent" class="px-4 py-2 text-sm font-medium text-primary-foreground bg-emerald-600 hover:bg-emerald-700 rounded-md transition-colors shadow-sm disabled:opacity-50">
            {{ savingAgent ? 'Saving...' : 'Save Agent' }}
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import api from '../services/api';

const route = useRoute();
const router = useRouter();

const tenantId = route.params.id;
const tenant = ref(null);
const agents = ref([]);
const loading = ref(true);
const saving = ref(false);

const form = ref({
  system_prompt_override: '',
  greeting_message: '',
  max_call_duration_min: 15,
  subscription_tier: 'payg',
  included_minutes_balance: 0,
  custom_monthly_price: 0,
  custom_included_minutes: 0,
  custom_per_minute_rate: 0.15
});

const originalForm = ref(null);

const isDirty = computed(() => {
  if (!originalForm.value) return false;
  return JSON.stringify(form.value) !== JSON.stringify(originalForm.value);
});

const cancelChanges = () => {
  if (originalForm.value && isDirty.value) {
    form.value = JSON.parse(JSON.stringify(originalForm.value));
  }
};

const fetchTenant = async () => {
  try {
    const res = await api.get('/api/super/tenants');
    const t = res.data.find(x => x.tenant_id === tenantId);
    if (t) {
      tenant.value = t;
      const cfg = t.tenant_config || {};
      form.value = {
        system_prompt_override: cfg.system_prompt_override || '',
        greeting_message: cfg.greeting_message || '',
        max_call_duration_min: cfg.max_call_duration_min || 15,
        subscription_tier: t.subscription_tier || 'payg',
        included_minutes_balance: t.included_minutes_balance || 0,
        custom_monthly_price: t.custom_monthly_price || 0,
        custom_included_minutes: t.custom_included_minutes || 0,
        custom_per_minute_rate: t.custom_per_minute_rate !== undefined ? parseFloat(t.custom_per_minute_rate) : 0.15
      };
      originalForm.value = JSON.parse(JSON.stringify(form.value));
    } else {
      router.push('/tenants');
    }
  } catch (err) {
    console.error(err);
    router.push('/tenants');
  }
};

const fetchAgents = async () => {
  try {
    const res = await api.get(`/api/super/tenants/${tenantId}/agents`);
    agents.value = res.data || [];
  } catch (err) {
    console.error("Failed to fetch tenant agents:", err);
  }
};

const isEditingAgent = ref(false);
const savingAgent = ref(false);
const editingAgentData = ref({
  agent_id: '',
  name: '',
  tts_voice_id: '',
  system_prompt_override: ''
});

const openEditAgent = (agent) => {
  editingAgentData.value = {
    agent_id: agent.agent_id,
    name: agent.name || '',
    tts_voice_id: agent.tts_voice_id || '',
    system_prompt_override: agent.system_prompt_override || ''
  };
  isEditingAgent.value = true;
};

const closeEditAgent = () => {
  isEditingAgent.value = false;
};

const saveAgent = async () => {
  savingAgent.value = true;
  try {
    await api.put(`/api/super/tenants/${tenantId}/agents/${editingAgentData.value.agent_id}`, {
      name: editingAgentData.value.name,
      tts_voice_id: editingAgentData.value.tts_voice_id,
      system_prompt_override: editingAgentData.value.system_prompt_override
    });
    // refresh agents list
    await fetchAgents();
    closeEditAgent();
  } catch (err) {
    alert(err.response?.data?.detail || 'Failed to update agent');
  } finally {
    savingAgent.value = false;
  }
};

const saveConfig = async () => {
  saving.value = true;
  try {
    const configPayload = { ...form.value };
    delete configPayload.subscription_tier;
    delete configPayload.included_minutes_balance;

    await api.put(`/api/super/tenants/${tenantId}/config`, configPayload);
    await api.put(`/api/super/tenants/${tenantId}/subscription`, {
      subscription_tier: form.value.subscription_tier,
      included_minutes_balance: form.value.included_minutes_balance,
      custom_monthly_price: form.value.custom_monthly_price,
      custom_included_minutes: form.value.custom_included_minutes,
      custom_per_minute_rate: form.value.custom_per_minute_rate
    });
    originalForm.value = JSON.parse(JSON.stringify(form.value));
  } catch (err) {
    alert(err.response?.data?.detail || 'Failed to save configuration');
  } finally {
    saving.value = false;
  }
};

onMounted(async () => {
  loading.value = true;
  await Promise.all([fetchTenant(), fetchAgents()]);
  loading.value = false;
});
</script>
