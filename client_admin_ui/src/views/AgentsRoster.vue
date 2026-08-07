<template>
  <div class="h-full flex flex-col p-8 overflow-y-auto w-full max-w-6xl mx-auto space-y-8">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold tracking-tight text-foreground flex items-center gap-3">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-primary"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>
          Agents Roster
        </h1>
        <p class="text-muted-foreground mt-1 text-sm">Manage your AI agents, assign phone numbers, and configure their personas.</p>
      </div>
      <button @click="provisionAgent" :disabled="provisioning" class="glass-button bg-primary/10 text-primary hover:bg-primary/20 flex items-center gap-2 shadow-[0_0_15px_hsl(var(--primary)/0.2)]">
        <svg v-if="provisioning" class="animate-spin -ml-1 mr-2 h-4 w-4 text-primary" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
        <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
        Provision New Agent
      </button>
    </div>

    <!-- Error/Loading states -->
    <div v-if="loading" class="flex justify-center p-12">
      <div class="animate-pulse flex flex-col items-center gap-4">
        <div class="h-12 w-12 rounded-full border-4 border-primary border-t-transparent animate-spin"></div>
        <p class="text-muted-foreground text-sm font-medium">Loading agents...</p>
      </div>
    </div>
    
    <div v-else-if="error" class="glass-panel p-6 border-red-500/20 bg-red-500/5 text-red-400 rounded-xl">
      <div class="flex items-center gap-3">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
        <p>{{ error }}</p>
      </div>
    </div>

    <div v-else-if="agents.length === 0" class="glass-panel p-16 flex flex-col items-center justify-center text-center rounded-xl border border-border/50">
      <div class="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mb-4 text-primary shadow-[0_0_20px_hsl(var(--primary)/0.2)]">
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>
      </div>
      <h3 class="text-xl font-semibold text-foreground mb-2">No Agents Found</h3>
      <p class="text-muted-foreground max-w-md">Your workspace doesn't have any AI agents configured yet. Provision a new agent to get started.</p>
      <button @click="provisionAgent" class="mt-6 glass-button bg-primary/10 text-primary hover:bg-primary/20 flex items-center gap-2">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
        Provision New Agent
      </button>
    </div>

    <!-- Agents Grid -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div v-for="agent in agents" :key="agent.agent_id" class="glass-panel rounded-xl border border-border/50 overflow-hidden group hover:border-primary/30 transition-all duration-300 shadow-lg hover:shadow-[0_0_25px_hsl(var(--primary)/0.15)] flex flex-col">
        <div class="p-5 border-b border-border/30 bg-muted/10 relative overflow-hidden">
          <div class="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
          <div class="flex items-center justify-between relative z-10">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center text-primary border border-primary/20 shadow-[0_0_10px_hsl(var(--primary)/0.2)]">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
              </div>
              <div>
                <h3 class="font-semibold text-foreground tracking-tight">{{ agent.name }}</h3>
                <span class="text-xs text-muted-foreground uppercase tracking-widest font-mono bg-muted/50 px-2 py-0.5 rounded-sm">{{ agent.niche || 'General' }}</span>
              </div>
            </div>
            <button @click="$router.push(`/agents/${agent.agent_id}`)" class="text-muted-foreground hover:text-primary transition-colors p-2 glass-button !px-2 !py-2 rounded-lg">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9"></path><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path></svg>
            </button>
          </div>
        </div>
        <div class="p-5 flex-1 flex flex-col gap-4">
          <div class="space-y-1">
            <div class="text-xs text-muted-foreground uppercase font-semibold tracking-wider">Phone Numbers</div>
            <div v-if="agent.phone_numbers && agent.phone_numbers.length" class="flex flex-wrap gap-2">
              <span v-for="num in agent.phone_numbers" :key="num" class="text-sm font-mono bg-background/50 border border-border/50 px-2.5 py-1 rounded-md text-foreground flex items-center gap-2 shadow-sm">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-primary"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg>
                {{ num }}
              </span>
            </div>
            <div v-else class="text-sm text-muted-foreground italic">No numbers assigned</div>
          </div>
          
          <div class="space-y-1 mt-auto pt-4 border-t border-border/30">
            <div class="text-xs text-muted-foreground uppercase font-semibold tracking-wider">Configuration Status</div>
            <div class="flex items-center gap-2 text-sm">
              <span v-if="agent.system_prompt_override" class="flex items-center gap-1.5 text-emerald-400 font-medium">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
                Prompt Configured
              </span>
              <span v-else class="flex items-center gap-1.5 text-amber-400 font-medium">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
                Using Default Prompt
              </span>
            </div>
          </div>
        </div>
        <div class="p-3 bg-background/30 border-t border-border/40 flex justify-between items-center text-xs text-muted-foreground">
          <span>Model: {{ agent.llm_model || 'Global Default' }}</span>
          <button @click="$router.push(`/agents/${agent.agent_id}`)" class="text-primary hover:text-primary/80 font-medium tracking-wide flex items-center gap-1 transition-colors">
            Configure
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"></polyline></svg>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useAuthStore } from '../stores/auth';

const authStore = useAuthStore();
const loading = ref(true);
const error = ref('');
const agents = ref([]);
const provisioning = ref(false);

const fetchAgents = async () => {
  loading.value = true;
  error.value = '';
  try {
    const res = await fetch(`/api/client/agents?tenant_id=${authStore.user.tenant_id}`, {
      headers: { 'Authorization': `Bearer ${authStore.token}` }
    });
    if (!res.ok) throw new Error('Failed to load agents');
    const data = await res.json();
    agents.value = data;
  } catch (err) {
    console.error(err);
    error.value = 'Unable to load agents. Please check your connection and try again.';
  } finally {
    loading.value = false;
  }
};

const provisionAgent = async () => {
  // We want to avoid generic browser prompts as requested by the user. 
  // Let's just create it directly.
  provisioning.value = true;
  try {
    // Generate a default name like "Agent 1" based on current length
    const agentName = `New Agent ${agents.value.length + 1}`;
    
    const res = await fetch(`/api/client/agents?tenant_id=${authStore.user.tenant_id}`, {
      method: 'POST',
      headers: { 
        'Authorization': `Bearer ${authStore.token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        name: agentName,
        niche: 'general'
      })
    });
    
    if (!res.ok) throw new Error('Failed to provision agent');
    
    // Reload agents
    await fetchAgents();
  } catch (err) {
    console.error(err);
    alert('Failed to provision a new agent.');
  } finally {
    provisioning.value = false;
  }
};

onMounted(() => {
  fetchAgents();
});
</script>
