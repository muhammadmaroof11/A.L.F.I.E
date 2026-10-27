<template>
  <div class="h-full flex flex-col p-8 overflow-y-auto w-full max-w-6xl mx-auto space-y-8">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-3xl font-bold tracking-tight text-foreground flex items-center gap-3">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-primary"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg>
          Carrier Phone Numbers
        </h1>
        <p class="text-muted-foreground mt-1 text-sm">Manage your dedicated carrier phone lines, search local area codes, and route inbound PSTN traffic.</p>
      </div>
      <div class="flex items-center gap-3">
        <button @click="fetchNumbers" class="glass-button text-xs px-3 py-2 flex items-center gap-1.5 hover:bg-muted/50">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" :class="{ 'animate-spin': loading }"><path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"/></svg>
          Refresh
        </button>
        <button @click="openBuyModal" class="glass-button bg-primary/10 text-primary hover:bg-primary/20 text-xs px-3.5 py-2 flex items-center gap-2 shadow-[0_0_15px_hsl(var(--primary)/0.2)]">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
          Buy New Number
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center p-12">
      <div class="animate-pulse flex flex-col items-center gap-4">
        <div class="h-12 w-12 rounded-full border-4 border-primary border-t-transparent animate-spin"></div>
        <p class="text-muted-foreground text-sm font-medium">Loading phone inventory...</p>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="numbers.length === 0" class="glass-panel p-16 flex flex-col items-center justify-center text-center rounded-xl border border-border/50">
      <div class="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mb-4 text-primary shadow-[0_0_20px_hsl(var(--primary)/0.2)]">
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg>
      </div>
      <h3 class="text-xl font-semibold text-foreground mb-2">No Phone Numbers Assigned</h3>
      <p class="text-muted-foreground max-w-md">Your workspace doesn't have an active carrier phone number yet. Search an area code and buy your first line.</p>
      <button @click="openBuyModal" class="mt-6 glass-button bg-primary/10 text-primary hover:bg-primary/20 flex items-center gap-2">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
        Search & Buy Number
      </button>
    </div>

    <!-- Phone Numbers List -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div v-for="num in numbers" :key="num.phone_number" class="glass-panel rounded-xl border border-border/50 p-6 flex flex-col justify-between group hover:border-primary/40 transition-all duration-300 relative overflow-hidden shadow-sm">
        <div class="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none"></div>
        
        <div class="space-y-3 relative z-10">
          <div class="flex items-center justify-between">
            <span class="text-[10px] font-mono uppercase bg-muted/60 text-muted-foreground px-2 py-0.5 rounded border border-border">
              {{ num.provider || 'Twilio' }}
            </span>
            <span class="text-[10px] font-semibold uppercase bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2 py-0.5 rounded-full flex items-center gap-1.5">
              <span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
              {{ num.status || 'Active' }}
            </span>
          </div>

          <div>
            <div class="text-xl font-bold font-mono text-foreground tracking-wide group-hover:text-primary transition-colors">
              {{ num.phone_number }}
            </div>
            <div class="text-xs text-muted-foreground mt-0.5">
              {{ num.friendly_name || 'Inbound Reception Line' }}
            </div>
          </div>

          <div class="pt-3 border-t border-border/30 space-y-1.5">
            <div class="flex items-center justify-between text-xs">
              <span class="text-muted-foreground">Assigned Agent:</span>
              <span class="font-medium text-foreground">{{ num.agent_name || 'Unassigned' }}</span>
            </div>
            <div class="flex items-center justify-between text-xs">
              <span class="text-muted-foreground">Niche Routing:</span>
              <span class="font-mono text-[10px] uppercase bg-primary/10 text-primary px-1.5 py-0.5 rounded">
                {{ num.niche || 'General' }}
              </span>
            </div>
          </div>
        </div>

        <div class="mt-4 pt-3 border-t border-border/30 flex items-center justify-between text-xs text-muted-foreground relative z-10">
          <span class="font-mono text-[11px]">{{ num.created_at ? new Date(num.created_at).toLocaleDateString() : 'Active' }}</span>
          <a :href="'tel:' + num.phone_number" class="text-primary hover:underline flex items-center gap-1">
            Test Dial
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>
          </a>
        </div>
      </div>
    </div>

    <!-- Buy Phone Number Modal -->
    <div v-if="showBuyModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-background/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div class="glass-panel bg-card w-full max-w-lg rounded-2xl shadow-2xl border border-border/60 overflow-hidden flex flex-col max-h-[90vh]">
        <div class="px-6 py-4 border-b border-border/40 flex justify-between items-center bg-muted/20">
          <div>
            <h3 class="text-base font-bold text-foreground">Acquire Dedicated Phone Number</h3>
            <p class="text-xs text-muted-foreground">Search carrier inventory by US area code and assign directly to an AI agent.</p>
          </div>
          <button @click="showBuyModal = false" class="text-muted-foreground hover:text-foreground transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
          </button>
        </div>

        <div class="p-6 space-y-4 overflow-y-auto custom-scrollbar flex-1">
          <!-- Search Form -->
          <div class="flex gap-2">
            <div class="flex-1 space-y-1">
              <label class="text-xs font-semibold uppercase text-muted-foreground">Area Code (e.g. 415, 212, 305)</label>
              <input v-model="areaCodeSearch" @keyup.enter="searchNumbers" type="text" placeholder="e.g. 415" maxlength="3" class="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-xs font-mono focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-primary" />
            </div>
            <button @click="searchNumbers" :disabled="searching" class="self-end px-4 py-2 h-9 rounded-md text-xs font-semibold bg-primary text-primary-foreground hover:bg-primary/90 transition-all flex items-center gap-1.5 disabled:opacity-50">
              <svg v-if="searching" class="animate-spin h-3.5 w-3.5 text-primary-foreground" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
              <span>{{ searching ? 'Searching...' : 'Search Numbers' }}</span>
            </button>
          </div>

          <!-- Assign to Agent Selection -->
          <div class="space-y-1">
            <label class="text-xs font-semibold uppercase text-muted-foreground">Assign Inbound Calls To</label>
            <select v-model="selectedAgentForOrder" class="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-xs focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-primary">
              <option v-for="agent in agentsList" :key="agent.agent_id" :value="agent.agent_id">
                {{ agent.name }} ({{ agent.niche || 'General' }})
              </option>
            </select>
          </div>

          <!-- Search Results List -->
          <div class="space-y-2 pt-2">
            <label class="text-xs font-semibold uppercase text-muted-foreground">Available Carrier Inventory</label>
            <div v-if="availableNumbers.length === 0" class="p-6 border border-dashed border-border rounded-xl text-center text-xs text-muted-foreground">
              {{ searching ? 'Searching carrier network...' : 'Enter an area code above and click Search Numbers.' }}
            </div>
            <div v-else class="space-y-2">
              <div v-for="item in availableNumbers" :key="item.phone_number" 
                   @click="selectedNumberToBuy = item.phone_number"
                   :class="selectedNumberToBuy === item.phone_number ? 'border-primary bg-primary/10 shadow-[0_0_12px_hsl(var(--primary)/0.2)]' : 'border-border/60 hover:border-primary/40 bg-background/50'"
                   class="p-3.5 rounded-xl border flex items-center justify-between cursor-pointer transition-all">
                <div class="flex items-center gap-3">
                  <div class="w-4 h-4 rounded-full border flex items-center justify-center" :class="selectedNumberToBuy === item.phone_number ? 'border-primary bg-primary text-primary-foreground' : 'border-muted-foreground'">
                    <span v-if="selectedNumberToBuy === item.phone_number" class="w-1.5 h-1.5 rounded-full bg-white"></span>
                  </div>
                  <div>
                    <div class="font-mono text-sm font-bold text-foreground">{{ item.friendly_name || item.phone_number }}</div>
                    <div class="text-[11px] text-muted-foreground">{{ item.locality || 'United States' }}, {{ item.region || 'US' }}</div>
                  </div>
                </div>
                <span class="text-[10px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2 py-0.5 rounded">Ready to Bind</span>
              </div>
            </div>
          </div>
        </div>

        <div class="px-6 py-4 border-t border-border/40 bg-muted/20 flex justify-between items-center">
          <span class="text-xs text-muted-foreground">$1.00/mo included in plan</span>
          <div class="flex gap-2">
            <button @click="showBuyModal = false" class="px-3.5 py-1.5 text-xs font-medium rounded-md bg-secondary text-secondary-foreground hover:bg-secondary/80">Cancel</button>
            <button @click="confirmOrder" :disabled="ordering || !selectedNumberToBuy" class="px-4 py-1.5 text-xs font-semibold rounded-md bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50 flex items-center gap-1.5">
              <svg v-if="ordering" class="animate-spin h-3.5 w-3.5 text-primary-foreground" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
              <span>{{ ordering ? 'Provisioning...' : 'Confirm & Bind Number' }}</span>
            </button>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '../services/api';

const numbers = ref([]);
const loading = ref(true);
const showBuyModal = ref(false);
const areaCodeSearch = ref('415');
const searching = ref(false);
const availableNumbers = ref([]);
const selectedNumberToBuy = ref('');
const selectedAgentForOrder = ref('');
const agentsList = ref([]);
const ordering = ref(false);

const fetchNumbers = async () => {
  loading.value = true;
  try {
    const res = await api.get('/api/client/phone-numbers');
    numbers.value = res.data || [];
  } catch (err) {
    console.error("Failed to load client phone numbers:", err);
  } finally {
    loading.value = false;
  }
};

const fetchAgents = async () => {
  try {
    const res = await api.get('/api/client/agents');
    agentsList.value = res.data || [];
    if (agentsList.value.length > 0) {
      selectedAgentForOrder.value = agentsList.value[0].agent_id;
    }
  } catch (err) {
    console.warn("Could not fetch agents:", err);
  }
};

const openBuyModal = () => {
  showBuyModal.value = true;
  if (availableNumbers.value.length === 0) {
    searchNumbers();
  }
};

const searchNumbers = async () => {
  searching.value = true;
  try {
    const res = await api.get('/api/client/phone-numbers/available', {
      params: { area_code: areaCodeSearch.value || '415' }
    });
    availableNumbers.value = res.data?.numbers || [];
    if (availableNumbers.value.length > 0) {
      selectedNumberToBuy.value = availableNumbers.value[0].phone_number;
    }
  } catch (err) {
    console.error("Failed to search numbers:", err);
  } finally {
    searching.value = false;
  }
};

const confirmOrder = async () => {
  if (!selectedNumberToBuy.value) return;
  ordering.value = true;
  try {
    const targetAgent = agentsList.value.find(a => a.agent_id === selectedAgentForOrder.value);
    await api.post('/api/client/phone-numbers/order', {
      phone_number: selectedNumberToBuy.value,
      agent_id: selectedAgentForOrder.value || undefined,
      niche: targetAgent?.niche || 'general'
    });
    showBuyModal.value = false;
    await fetchNumbers();
  } catch (err) {
    alert("Failed to purchase phone number: " + (err.response?.data?.detail || err.message));
  } finally {
    ordering.value = false;
  }
};

onMounted(() => {
  fetchNumbers();
  fetchAgents();
});
</script>
