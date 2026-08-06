<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
      <div class="flex flex-col space-y-1">
        <h2 class="text-2xl font-semibold tracking-tight">Tool & Webhook Registry</h2>
        <p class="text-sm text-muted-foreground">Manage native function-calling tools and external HTTP webhook actions.</p>
      </div>
      <button @click="showModal = true" class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground shadow hover:bg-primary/90 h-9 px-4 py-2 shrink-0">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="mr-2 h-4 w-4"><path d="M5 12h14"/><path d="M12 5v14"/></svg>
        Register Custom Webhook Tool
      </button>
    </div>

    <!-- Native Tools Grid -->
    <div class="space-y-4">
      <h3 class="text-lg font-semibold tracking-tight flex items-center gap-2">
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-primary"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
        Native Built-in Toolsets
      </h3>
      
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div class="rounded-xl border bg-card text-card-foreground shadow-sm p-6 flex flex-col justify-between group hover:shadow-md transition-shadow">
          <div>
            <div class="flex justify-between items-center mb-3">
              <h4 class="font-semibold tracking-tight">Real Estate Tools</h4>
              <span class="inline-flex items-center rounded-full border border-transparent bg-emerald-500/10 px-2 py-0.5 text-[10px] font-semibold text-emerald-500">Active</span>
            </div>
            <div class="font-mono text-xs text-muted-foreground bg-muted/50 inline-block px-2 py-1 rounded mb-4">real_estate_tools</div>
            <div class="space-y-2">
              <p class="text-xs text-muted-foreground">Functions:</p>
              <div class="flex flex-wrap gap-1.5">
                <code class="text-[10px] bg-secondary text-secondary-foreground px-1.5 py-0.5 rounded">search_properties</code>
                <code class="text-[10px] bg-secondary text-secondary-foreground px-1.5 py-0.5 rounded">book_site_visit</code>
                <code class="text-[10px] bg-secondary text-secondary-foreground px-1.5 py-0.5 rounded">check_director_schedule</code>
              </div>
            </div>
          </div>
        </div>

        <div class="rounded-xl border bg-card text-card-foreground shadow-sm p-6 flex flex-col justify-between group hover:shadow-md transition-shadow">
          <div>
            <div class="flex justify-between items-center mb-3">
              <h4 class="font-semibold tracking-tight">Car Rental Tools</h4>
              <span class="inline-flex items-center rounded-full border border-transparent bg-emerald-500/10 px-2 py-0.5 text-[10px] font-semibold text-emerald-500">Active</span>
            </div>
            <div class="font-mono text-xs text-muted-foreground bg-muted/50 inline-block px-2 py-1 rounded mb-4">car_rental_tools</div>
            <div class="space-y-2">
              <p class="text-xs text-muted-foreground">Functions:</p>
              <div class="flex flex-wrap gap-1.5">
                <code class="text-[10px] bg-secondary text-secondary-foreground px-1.5 py-0.5 rounded">check_fleet_availability</code>
                <code class="text-[10px] bg-secondary text-secondary-foreground px-1.5 py-0.5 rounded">quote_rental_rates</code>
                <code class="text-[10px] bg-secondary text-secondary-foreground px-1.5 py-0.5 rounded">confirm_reservation</code>
              </div>
            </div>
          </div>
        </div>

        <div class="rounded-xl border bg-card text-card-foreground shadow-sm p-6 flex flex-col justify-between group hover:shadow-md transition-shadow">
          <div>
            <div class="flex justify-between items-center mb-3">
              <h4 class="font-semibold tracking-tight">Core Telephony Tools</h4>
              <span class="inline-flex items-center rounded-full border border-transparent bg-emerald-500/10 px-2 py-0.5 text-[10px] font-semibold text-emerald-500">Active</span>
            </div>
            <div class="font-mono text-xs text-muted-foreground bg-muted/50 inline-block px-2 py-1 rounded mb-4">core_tools</div>
            <div class="space-y-2">
              <p class="text-xs text-muted-foreground">Functions:</p>
              <div class="flex flex-wrap gap-1.5">
                <code class="text-[10px] bg-secondary text-secondary-foreground px-1.5 py-0.5 rounded">transfer_call</code>
                <code class="text-[10px] bg-secondary text-secondary-foreground px-1.5 py-0.5 rounded">end_call</code>
                <code class="text-[10px] bg-secondary text-secondary-foreground px-1.5 py-0.5 rounded">send_sms_summary</code>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Custom Webhook Tools List -->
    <div class="space-y-4 pt-4 border-t border-border">
      <h3 class="text-lg font-semibold tracking-tight flex items-center gap-2">
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-primary"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>
        Custom HTTP Webhook Tools
      </h3>
      
      <div v-if="loading" class="flex items-center justify-center h-32 text-muted-foreground">
        Loading tools...
      </div>

      <div v-else class="rounded-md border bg-card shadow-sm">
        <div class="w-full overflow-auto">
          <table class="w-full caption-bottom text-sm">
            <thead class="[&_tr]:border-b bg-muted/50">
              <tr class="border-b transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted">
                <th class="h-10 px-4 text-left align-middle font-medium text-muted-foreground w-[20%]">Tool Name</th>
                <th class="h-10 px-4 text-left align-middle font-medium text-muted-foreground w-[30%]">Method & Endpoint</th>
                <th class="h-10 px-4 text-left align-middle font-medium text-muted-foreground">Description</th>
                <th class="h-10 px-4 text-right align-middle font-medium text-muted-foreground">Actions</th>
              </tr>
            </thead>
            <tbody class="[&_tr:last-child]:border-0">
              <tr v-if="customTools.length === 0">
                <td colspan="4" class="p-8 text-center text-muted-foreground">No custom webhook tools registered yet. Click above to register your first API tool.</td>
              </tr>
              <tr v-for="tool in customTools" :key="tool.id" class="border-b transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted">
                <td class="p-4 align-middle">
                  <span class="font-mono text-[13px] font-semibold text-amber-500">{{ tool.tool_name }}</span>
                </td>
                <td class="p-4 align-middle">
                  <div class="flex items-center gap-2">
                    <span :class="['inline-flex items-center rounded border px-2 py-0.5 text-[10px] font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2', tool.http_method === 'POST' ? 'border-transparent bg-primary/10 text-primary' : 'border-transparent bg-emerald-500/10 text-emerald-500']">
                      {{ tool.http_method }}
                    </span>
                    <span class="font-mono text-[11px] text-muted-foreground truncate max-w-[200px]" :title="tool.webhook_url">{{ tool.webhook_url }}</span>
                  </div>
                </td>
                <td class="p-4 align-middle text-muted-foreground text-xs">
                  {{ tool.description }}
                </td>
                <td class="p-4 align-middle text-right">
                  <button @click="deleteTool(tool.id)" class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-xs font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring hover:bg-rose-500/10 text-rose-500 h-8 w-8 px-0" title="Delete Tool">
                    <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/></svg>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Modal Form -->
    <div v-if="showModal" class="fixed inset-0 z-50 bg-background/80 backdrop-blur-sm flex items-center justify-center">
      <div class="fixed left-[50%] top-[50%] z-50 grid w-full max-w-lg translate-x-[-50%] translate-y-[-50%] gap-4 border bg-background p-6 shadow-lg sm:rounded-lg">
        <div class="flex flex-col space-y-1.5 sm:text-left">
          <h2 class="text-lg font-semibold leading-none tracking-tight">Register Custom HTTP Webhook Tool</h2>
          <p class="text-sm text-muted-foreground">Expose external CRM or API endpoints to the agent LLM.</p>
        </div>

        <form @submit.prevent="createTool" class="space-y-4 py-4">
          <div class="space-y-2">
            <label class="text-sm font-medium leading-none">Tool Name</label>
            <input type="text" class="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring font-mono text-xs" v-model="form.tool_name" required placeholder="check_crm_lead" />
            <p class="text-[11px] text-muted-foreground">Use snake_case format without spaces.</p>
          </div>

          <div class="space-y-2">
            <label class="text-sm font-medium leading-none">HTTP Method & Webhook URL</label>
            <div class="flex gap-2">
              <select class="flex h-9 w-24 rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring" v-model="form.http_method">
                <option value="POST">POST</option>
                <option value="GET">GET</option>
              </select>
              <input type="url" class="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring font-mono text-xs" v-model="form.webhook_url" required placeholder="https://api.clientcrm.com/v1/lead" />
            </div>
          </div>

          <div class="space-y-2">
            <label class="text-sm font-medium leading-none">Description</label>
            <textarea class="flex min-h-[80px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring" v-model="form.description" rows="3" required placeholder="Call this tool when caller asks to verify their existing reservation..."></textarea>
            <p class="text-[11px] text-muted-foreground">Prompt guidance for LLM on when to invoke this tool.</p>
          </div>

          <div class="flex items-center justify-end gap-2 pt-4 border-t border-border mt-6">
            <button type="button" class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 border border-input bg-background shadow-sm hover:bg-accent hover:text-accent-foreground h-9 px-4 py-2" @click="showModal = false">Cancel</button>
            <button type="submit" class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground shadow hover:bg-primary/90 h-9 px-4 py-2">Register Tool</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '../services/api';

const customTools = ref([]);
const loading = ref(true);
const showModal = ref(false);

const form = ref({
  tool_name: '',
  description: '',
  webhook_url: '',
  http_method: 'POST'
});

const fetchTools = async () => {
  loading.value = true;
  try {
    const res = await api.get('/api/super/custom-tools');
    customTools.value = res.data || [];
  } catch (err) {
    console.warn('Could not fetch tools:', err);
  } finally {
    loading.value = false;
  }
};

const createTool = async () => {
  try {
    await api.post('/api/super/custom-tools', form.value);
    showModal.value = false;
    form.value = { tool_name: '', description: '', webhook_url: '', http_method: 'POST' };
    fetchTools();
  } catch (err) {
    alert(err.response?.data?.detail || 'Failed to create tool.');
  }
};

const deleteTool = async (id) => {
  if (!confirm('Are you sure you want to delete this custom tool?')) return;
  try {
    await api.delete(`/api/super/custom-tools/${id}`);
    fetchTools();
  } catch (err) {
    alert('Failed to delete tool.');
  }
};

onMounted(() => {
  fetchTools();
});
</script>
