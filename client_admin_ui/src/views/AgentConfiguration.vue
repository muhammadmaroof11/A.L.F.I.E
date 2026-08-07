<template>
  <div class="space-y-8 max-w-5xl mx-auto pb-12">
    
    <!-- Header Area -->
    <div class="glass-panel p-8 relative overflow-hidden rounded-xl">
      <div class="absolute top-0 right-0 w-64 h-64 bg-primary/10 rounded-full blur-[80px] pointer-events-none"></div>
      
      <div class="flex items-start justify-between relative z-10">
        <div class="flex items-center gap-6">
          <div class="w-16 h-16 rounded-xl bg-primary/10 flex items-center justify-center text-primary shadow-sm border border-primary/20">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M12 2v20"></path><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>
          </div>
          <div>
            <h2 class="text-2xl font-semibold mb-1">Agent Persona Config</h2>
            <p class="text-sm text-muted-foreground">Customize voice, tone, and system prompt for your AI assistant.</p>
          </div>
        </div>
        
        <div class="flex items-center gap-4">
          <div v-if="tier === 'custom' || tier === 'enterprise'" class="flex items-center gap-2 mr-4 bg-background/50 backdrop-blur-md px-3 py-1.5 rounded-lg border border-border/50">
            <label class="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Expert Mode</label>
            <button @click="expertMode = !expertMode" :class="expertMode ? 'bg-primary' : 'bg-muted'" class="relative inline-flex h-5 w-9 shrink-0 cursor-pointer items-center justify-center rounded-full border-2 border-transparent transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background">
              <span :class="expertMode ? 'translate-x-2' : '-translate-x-2'" class="pointer-events-none block h-4 w-4 rounded-full bg-background shadow-lg ring-0 transition-transform"></span>
            </button>
          </div>
          
          <button @click="saveConfig" :disabled="saving" class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground shadow hover:bg-primary/90 h-10 px-4 py-2 gap-2">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"></path><polyline points="17 21 17 13 7 13 7 21"></polyline><polyline points="7 3 7 8 15 8"></polyline></svg>
            {{ saving ? 'Saving...' : 'Save Configuration' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Configuration Sections -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
      
      <!-- Left Column: Settings -->
      <div class="lg:col-span-1 space-y-6">
        
        <!-- Niche Settings -->
        <div class="glass-panel p-6 rounded-xl relative overflow-hidden group hover-glow transition-all duration-300">
          <h3 class="text-sm font-semibold uppercase tracking-wider mb-5 flex items-center gap-2">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="text-primary"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path><polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline><line x1="12" y1="22.08" x2="12" y2="12"></line></svg>
            Agent Niche
          </h3>
          <div class="space-y-4">
            <div class="space-y-2">
              <label class="text-sm font-medium leading-none">Specialization</label>
              <select v-model="form.niche" class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50">
                <option value="general">General Assistant</option>
                <option value="sales">Inbound Sales</option>
                <option value="support">Customer Support</option>
                <option value="luxury_transfer">Luxury Transport Booking</option>
              </select>
            </div>
            <div v-if="form.niche === 'luxury_transfer'" class="mt-4 p-3 bg-primary/10 border border-primary/20 rounded-md text-xs text-primary/90 flex items-start gap-2">
              <svg class="shrink-0 mt-0.5" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>
              This niche automatically activates the Route Distance and Booking tools. Configure fleet pricing in the Transport Settings tab.
            </div>
          </div>
        </div>

        <!-- Voice Settings -->
        <div class="glass-panel p-6 rounded-xl relative overflow-hidden group hover-glow transition-all duration-300">
          <h3 class="text-sm font-semibold uppercase tracking-wider mb-5 flex items-center gap-2">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="text-primary"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path><path d="M19 10v2a7 7 0 0 1-14 0v-2"></path><line x1="12" y1="19" x2="12" y2="23"></line><line x1="8" y1="23" x2="16" y2="23"></line></svg>
            Voice Model
          </h3>
          <div class="space-y-4">
            <div class="space-y-2">
              <label class="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">Provider</label>
              <select disabled class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50">
                <option value="openai">OpenAI (TTS-1)</option>
              </select>
            </div>
            <div class="space-y-2">
              <label class="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">Voice Identity</label>
              <select v-model="form.tts_voice_id" class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50">
                <option value="alloy">Alloy (Neutral)</option>
                <option value="echo">Echo (Warm)</option>
                <option value="shimmer">Shimmer (Bright)</option>
              </select>
            </div>
            
            <button class="w-full mt-2 inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-10 px-4 py-2 gap-2">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
              Test Voice
            </button>
          </div>
        </div>
        
        <!-- Behavior Settings -->
        <div v-if="expertMode" class="glass-panel p-6 rounded-xl relative overflow-hidden group hover-glow transition-all duration-300 animate-in fade-in slide-in-from-top-2">
          <h3 class="text-sm font-semibold uppercase tracking-wider mb-5 flex items-center gap-2">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="text-primary"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>
            LLM Settings
          </h3>
          <div class="space-y-4">
            <div class="space-y-2">
              <label class="text-sm font-medium leading-none">Model</label>
              <select v-model="form.llm_model" class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50">
                <option value="llama-3.1-8b-instant">Llama 3.1 8B (Fast)</option>
                <option value="llama-3.1-70b-versatile">Llama 3.1 70B (Smart)</option>
              </select>
            </div>
            
            <div class="pt-4 border-t border-border/50">
              <div class="flex justify-between items-center mb-2">
                <label class="text-sm font-medium leading-none">Creativity (Temperature)</label>
                <span class="text-xs font-mono text-primary">{{ form.llm_temperature }}</span>
              </div>
              <input type="range" v-model.number="form.llm_temperature" min="0" max="1" step="0.1" class="w-full accent-primary h-2 bg-muted rounded-lg appearance-none cursor-pointer outline-none">
            </div>
          </div>
        </div>

      </div>

      <!-- Right Column: Prompts -->
      <div class="lg:col-span-2 space-y-6">
        
        <div class="glass-panel p-8 flex flex-col rounded-xl relative overflow-hidden group hover-glow transition-all duration-300">
          <h3 class="text-sm font-semibold uppercase tracking-wider mb-2 flex items-center gap-2">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="text-primary"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
            System Prompt
          </h3>
          <p class="text-xs text-muted-foreground mb-6">This prompt defines the agent's core identity, goals, and guardrails.</p>
          
          <div class="flex-1 relative">
            <textarea v-model="form.system_prompt_override" class="flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50 h-full min-h-[300px] font-mono resize-none custom-scrollbar" placeholder="Enter system prompt override..."></textarea>
          </div>
        </div>

        <!-- Custom Tools Builder -->
        <div v-if="expertMode" class="glass-panel p-8 flex flex-col rounded-xl relative overflow-hidden group hover-glow transition-all duration-300 animate-in fade-in slide-in-from-top-4">
          <div class="flex justify-between items-center mb-6">
            <div>
              <h3 class="text-sm font-semibold uppercase tracking-wider mb-1 flex items-center gap-2">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="text-primary"><polygon points="12 2 2 7 12 12 22 7 12 2"></polygon><polyline points="2 17 12 22 22 17"></polyline><polyline points="2 12 12 17 22 12"></polyline></svg>
                Custom API Tools (Webhooks)
              </h3>
              <p class="text-xs text-muted-foreground">Define external endpoints the AI can trigger during a conversation.</p>
            </div>
            <button @click="addCustomTool" class="glass-button bg-primary/10 text-primary hover:bg-primary/20 text-xs px-3 py-1.5 flex items-center gap-1.5">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
              Add Tool
            </button>
          </div>

          <div v-if="form.custom_tools.length === 0" class="p-8 border border-dashed border-border/50 rounded-xl text-center flex flex-col items-center justify-center bg-muted/5">
            <svg class="text-muted-foreground mb-3" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><line x1="9" y1="3" x2="9" y2="21"></line></svg>
            <p class="text-sm text-muted-foreground">No custom tools defined.</p>
          </div>
          
          <div v-else class="space-y-4">
            <div v-for="(tool, index) in form.custom_tools" :key="index" class="p-4 border border-border/50 rounded-xl bg-background/50 space-y-4">
              <div class="flex justify-between items-start gap-4">
                <div class="flex-1 grid grid-cols-2 gap-4">
                  <div class="space-y-1.5">
                    <label class="text-xs font-semibold text-muted-foreground">Tool Name (e.g. check_order)</label>
                    <input v-model="tool.name" type="text" class="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm transition-colors placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring">
                  </div>
                  <div class="space-y-1.5">
                    <label class="text-xs font-semibold text-muted-foreground">Webhook URL</label>
                    <input v-model="tool.webhook_url" type="url" placeholder="https://..." class="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm transition-colors placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring">
                  </div>
                </div>
                <button @click="removeCustomTool(index)" class="text-red-400 hover:bg-red-500/10 p-1.5 rounded-md transition-colors mt-5">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                </button>
              </div>
              <div class="space-y-1.5">
                <label class="text-xs font-semibold text-muted-foreground">Description (Instructs the AI when to use this)</label>
                <input v-model="tool.description" type="text" class="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm transition-colors placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring">
              </div>
              <div class="space-y-1.5">
                <label class="text-xs font-semibold text-muted-foreground">JSON Schema (Parameters to extract)</label>
                <textarea v-model="tool.schema" class="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-xs font-mono shadow-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring" placeholder='{"type": "object", "properties": {"order_id": {"type": "string"}}}'></textarea>
              </div>
            </div>
          </div>
        </div>
        
      </div>
      
    </div>
    
    <!-- Save Toast -->
    <div v-if="showToast" class="fixed bottom-6 right-6 glass-panel border-primary/50 text-foreground px-6 py-4 rounded-xl shadow-2xl flex items-center gap-3 animate-in fade-in slide-in-from-bottom-4 z-50">
      <div class="w-8 h-8 rounded-full bg-emerald-500/20 text-emerald-500 flex items-center justify-center">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
      </div>
      <div>
        <p class="font-semibold text-sm">Configuration Saved</p>
        <p class="text-xs text-muted-foreground">The AI agent has been updated.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import api from '../services/api';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const agentId = route.params.agent_id;

const form = ref({
  system_prompt_override: '',
  tts_voice_id: 'alloy',
  llm_model: 'llama-3.1-8b-instant',
  llm_temperature: 0.3,
  niche: 'general',
  custom_tools: []
});

const saving = ref(false);
const showToast = ref(false);
const tier = ref('payg');
const expertMode = ref(false);

const getTenantIdFromToken = () => {
  const token = localStorage.getItem('alfie_client_token');
  if (!token) return null;
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    return payload.tenant_id;
  } catch (e) {
    return null;
  }
};

const fetchConfig = async () => {
  const tenantId = getTenantIdFromToken();
  if (!tenantId || !agentId) {
    router.push('/agents');
    return;
  }
  
  try {
    const [agentsRes, billingRes] = await Promise.all([
      api.get(`/api/client/agents?tenant_id=${tenantId}`),
      api.get(`/api/client/billing/subscription?tenant_id=${tenantId}`).catch(() => null)
    ]);
    
    if (billingRes && billingRes.data) {
      tier.value = billingRes.data.subscription_tier;
    }

    const agent = agentsRes.data.find(a => a.agent_id === agentId);
    
    if (agent) {
      form.value = { 
        system_prompt_override: agent.system_prompt_override || '',
        tts_voice_id: agent.tts_voice_id || 'alloy',
        llm_model: agent.llm_model || 'llama-3.1-8b-instant',
        llm_temperature: agent.llm_temperature !== null ? agent.llm_temperature : 0.3,
        niche: agent.niche || 'general',
        custom_tools: agent.custom_tools || []
      };
    } else {
      router.push('/agents');
    }
  } catch (err) {
    console.warn("Failed to fetch agent config:", err);
  }
};

const addCustomTool = () => {
  form.value.custom_tools.push({
    name: '',
    description: '',
    schema: '{\n  "type": "object",\n  "properties": {\n    \n  }\n}',
    webhook_url: ''
  });
};

const removeCustomTool = (index) => {
  form.value.custom_tools.splice(index, 1);
};

const saveConfig = async () => {
  const tenantId = getTenantIdFromToken();
  if (!tenantId || !agentId) return;
  
  saving.value = true;
  try {
    await api.put(`/api/client/agents/${agentId}?tenant_id=${tenantId}`, form.value);
    
    // Show toast
    showToast.value = true;
    setTimeout(() => {
      showToast.value = false;
    }, 3000);
  } catch (err) {
    console.error("Failed to save config:", err);
  } finally {
    saving.value = false;
  }
};

onMounted(() => {
  fetchConfig();
});
</script>
