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
        
        <button @click="saveConfig" :disabled="saving" class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground shadow hover:bg-primary/90 h-10 px-4 py-2 gap-2">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"></path><polyline points="17 21 17 13 7 13 7 21"></polyline><polyline points="7 3 7 8 15 8"></polyline></svg>
          {{ saving ? 'Saving...' : 'Save Configuration' }}
        </button>
      </div>
    </div>

    <!-- Configuration Sections -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
      
      <!-- Left Column: Settings -->
      <div class="lg:col-span-1 space-y-6">
        
        <!-- Voice Settings -->
        <div class="glass-panel p-6 rounded-xl relative overflow-hidden group hover-glow transition-all duration-300">
          <h3 class="text-sm font-semibold uppercase tracking-wider mb-5 flex items-center gap-2">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="text-primary"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path><path d="M19 10v2a7 7 0 0 1-14 0v-2"></path><line x1="12" y1="19" x2="12" y2="23"></line><line x1="8" y1="23" x2="16" y2="23"></line></svg>
            Voice Model
          </h3>
          <div class="space-y-4">
            <div class="space-y-2">
              <label class="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">Provider</label>
              <select v-model="form.voice_config.provider" class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50">
                <option value="openai">OpenAI (TTS-1)</option>
                <option value="elevenlabs">ElevenLabs</option>
                <option value="fish_audio">Fish Audio</option>
              </select>
            </div>
            <div class="space-y-2">
              <label class="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">Voice Identity</label>
              <select v-model="form.voice_config.voice_id" class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50">
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
        <div class="glass-panel p-6 rounded-xl relative overflow-hidden group hover-glow transition-all duration-300">
          <h3 class="text-sm font-semibold uppercase tracking-wider mb-5 flex items-center gap-2">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="text-primary"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>
            Dialer Config
          </h3>
          <div class="space-y-4">
            <div>
              <div class="flex justify-between items-center mb-2">
                <label class="text-sm font-medium leading-none">Interruption Sensitivity</label>
                <span class="text-xs font-mono text-primary">{{ form.vad_config.min_silence_duration }}</span>
              </div>
              <input type="range" v-model.number="form.vad_config.min_silence_duration" min="100" max="1000" step="50" class="w-full accent-primary h-2 bg-muted rounded-lg appearance-none cursor-pointer outline-none">
            </div>
            
            <div class="flex items-center justify-between pt-4 border-t border-border/50">
              <label class="text-sm font-medium leading-none">Record Calls</label>
              <button type="button" @click="form.record_calls = !form.record_calls" :class="form.record_calls ? 'bg-primary' : 'bg-input'" class="peer inline-flex h-6 w-11 shrink-0 cursor-pointer items-center rounded-full border-2 border-transparent transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background disabled:cursor-not-allowed disabled:opacity-50">
                <span :class="form.record_calls ? 'translate-x-5' : 'translate-x-0'" class="pointer-events-none block h-5 w-5 rounded-full bg-background shadow-lg ring-0 transition-transform"></span>
              </button>
            </div>
          </div>
        </div>
        
        <!-- Integrations Settings -->
        <div class="glass-panel p-6 rounded-xl relative overflow-hidden group hover-glow transition-all duration-300">
          <h3 class="text-sm font-semibold uppercase tracking-wider mb-5 flex items-center gap-2">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="text-primary"><path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"></path><polyline points="13 2 13 9 20 9"></polyline></svg>
            Integrations
          </h3>
          <div class="space-y-4">
            <div class="space-y-2">
              <label class="text-sm font-medium leading-none">CRM Provider</label>
              <select v-model="form.crm_provider" class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50">
                <option value="twenty">Twenty CRM</option>
                <option value="hubspot">HubSpot</option>
                <option value="gohighlevel">GoHighLevel</option>
              </select>
            </div>
            <div class="space-y-2">
              <label class="text-sm font-medium leading-none">CRM API Key</label>
              <input type="password" v-model="form.crm_api_key" placeholder="Enter API Key" class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50">
            </div>
            
            <div class="pt-4 border-t border-border/50 space-y-4">
              <div class="space-y-2">
                <label class="text-sm font-medium leading-none">Cal.com API Key</label>
                <input type="password" v-model="form.calendar_api_key" placeholder="Enter API Key" class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50">
              </div>
              <div class="space-y-2">
                <label class="text-sm font-medium leading-none">Cal.com Event Type ID</label>
                <input type="text" v-model="form.calendar_event_type_id" placeholder="e.g. 123456" class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50">
              </div>
            </div>
            
            <div class="pt-4 border-t border-border/50 space-y-4">
              <h4 class="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Telephony (Twilio BYOK)</h4>
              <div class="space-y-2">
                <label class="text-sm font-medium leading-none">Twilio Account SID</label>
                <input type="text" v-model="form.twilio_account_sid" placeholder="AC..." class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50">
              </div>
              <div class="space-y-2">
                <label class="text-sm font-medium leading-none">Twilio Auth Token</label>
                <input type="password" v-model="form.twilio_auth_token" placeholder="Enter Auth Token" class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50">
              </div>
              <div class="space-y-2">
                <label class="text-sm font-medium leading-none">AI Phone Number</label>
                <input type="text" v-model="form.twilio_phone_number" placeholder="+1234567890" class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50">
              </div>
            </div>
          </div>
        </div>

      </div>

      <!-- Right Column: Prompts -->
      <div class="lg:col-span-2 space-y-6">
        
        <div class="glass-panel p-8 h-full flex flex-col rounded-xl relative overflow-hidden group hover-glow transition-all duration-300">
          <h3 class="text-sm font-semibold uppercase tracking-wider mb-2 flex items-center gap-2">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="text-primary"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
            System Prompt
          </h3>
          <p class="text-xs text-muted-foreground mb-6">This prompt defines the agent's core identity, goals, and guardrails.</p>
          
          <div class="flex-1 relative">
            <textarea v-model="form.system_prompt_override" class="flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50 h-full min-h-[300px] font-mono resize-none custom-scrollbar" placeholder="Enter system prompt override..."></textarea>
          </div>
        </div>
        
      </div>
      
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '../services/api';

const form = ref({
  system_prompt_override: '',
  voice_config: { provider: 'openai', voice_id: 'alloy' },
  vad_config: { min_silence_duration: 300 },
  record_calls: true,
  llm_config: { model: 'llama-3.1-8b-instant' },
  crm_provider: 'twenty',
  crm_api_key: '',
  calendar_api_key: '',
  calendar_event_type_id: '',
  twilio_account_sid: '',
  twilio_auth_token: '',
  twilio_phone_number: ''
});

const saving = ref(false);

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
  if (!tenantId) return;
  
  try {
    const res = await api.get(`/api/client/config?tenant_id=${tenantId}`);
    if (res.data) {
      form.value = { ...form.value, ...res.data };
      if (!form.value.voice_config) form.value.voice_config = { provider: 'openai', voice_id: 'alloy' };
      if (!form.value.vad_config) form.value.vad_config = { min_silence_duration: 300 };
    }
  } catch (err) {
    console.warn("Failed to fetch tenant config:", err);
  }
};

const saveConfig = async () => {
  const tenantId = getTenantIdFromToken();
  if (!tenantId) return;
  
  saving.value = true;
  try {
    await api.put(`/api/client/config?tenant_id=${tenantId}`, form.value);
    alert("Configuration saved successfully!");
  } catch (err) {
    console.error("Failed to save config:", err);
    alert("Failed to save configuration.");
  } finally {
    saving.value = false;
  }
};

onMounted(() => {
  fetchConfig();
});
</script>
