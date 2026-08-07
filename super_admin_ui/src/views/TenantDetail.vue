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

      <!-- Brain (LLM) -->
      <div class="rounded-xl glass-panel border border-border/60 shadow-lg overflow-hidden transition-all hover:border-emerald-500/30 group break-inside-avoid">
        <div class="p-6 border-b border-border/40 bg-gradient-to-r from-emerald-500/5 to-transparent">
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 rounded-lg bg-emerald-500/10 flex items-center justify-center text-emerald-500 group-hover:scale-110 transition-transform">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" x2="12" y1="19" y2="22"/></svg>
            </div>
            <div>
              <h3 class="font-semibold text-lg text-foreground">Brain Engine (LLM)</h3>
              <p class="text-xs text-muted-foreground mt-0.5">Configure the reasoning engine and conversational warmth.</p>
            </div>
          </div>
        </div>
        <div class="p-6 grid grid-cols-1 md:grid-cols-2 gap-8 bg-background/20">
          <div class="space-y-2">
            <label class="text-sm font-semibold text-foreground">Conversational Model</label>
            <select class="flex h-11 w-full rounded-md border border-input bg-background px-4 py-2 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500 focus:border-emerald-500" v-model="form.llm_model">
              <option value="meta-llama/llama-3.3-70b-instruct">Llama 3.3 70B Instruct (Human-Like)</option>
              <option value="meta-llama/llama-3.1-8b-instruct">Llama 3.1 8B Instruct (Ultra Fast)</option>
              <option value="anthropic/claude-3.5-sonnet">Claude 3.5 Sonnet (High Empathy)</option>
              <option value="openai/gpt-4o">GPT-4o Omnimodal</option>
              <option value="qwen/qwen-2.5-72b-instruct">Qwen 2.5 72B (Multilingual)</option>
            </select>
          </div>

          <div class="space-y-3">
            <div class="flex items-center justify-between">
              <label class="text-sm font-semibold text-foreground">Temperature (Warmth)</label>
              <span class="font-mono text-xs bg-background px-2.5 py-1 rounded-md text-foreground border border-border/80 shadow-sm font-bold">{{ form.llm_temperature.toFixed(2) }}</span>
            </div>
            <input type="range" class="w-full accent-emerald-500 cursor-grab active:cursor-grabbing" min="0" max="1" step="0.05" v-model.number="form.llm_temperature">
            <div class="flex justify-between text-[11px] font-medium text-muted-foreground">
              <span>Robotic (0.0)</span>
              <span>Creative (1.0)</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Voice (TTS) -->
      <div class="rounded-xl glass-panel border border-border/60 shadow-lg overflow-hidden transition-all hover:border-amber-500/30 group break-inside-avoid">
        <div class="p-6 border-b border-border/40 bg-gradient-to-r from-amber-500/5 to-transparent">
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 rounded-lg bg-amber-500/10 flex items-center justify-center text-amber-500 group-hover:scale-110 transition-transform">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"/></svg>
            </div>
            <div>
              <h3 class="font-semibold text-lg text-foreground">Voice Synthesis (TTS)</h3>
              <p class="text-xs text-muted-foreground mt-0.5">Control how the agent sounds to the caller.</p>
            </div>
          </div>
        </div>
        <div class="p-6 space-y-8 bg-background/20">
          <div class="space-y-2">
            <label class="text-sm font-semibold text-foreground">Discover & Assign Voice</label>
            <select class="flex h-11 w-full rounded-md border border-input bg-background px-4 py-2 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-500 focus:border-amber-500" @change="e => { if(e.target.value) form.tts_voice_id = e.target.value; }">
              <option value="">-- Select from Fish Audio Library --</option>
              <option v-for="voice in voices" :key="voice.id" :value="voice.id">
                {{ voice.title }} (by {{ voice.author }})
              </option>
            </select>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div class="space-y-2">
              <label class="text-sm font-semibold text-foreground">Fish Audio Voice ID</label>
              <input type="text" class="flex h-11 w-full rounded-md border border-input bg-background px-4 py-2 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-500 focus:border-amber-500 font-mono text-xs text-amber-600 dark:text-amber-500 font-bold" v-model="form.tts_voice_id" placeholder="Voice ID string..." />
            </div>

            <div class="space-y-3">
              <div class="flex items-center justify-between">
                <label class="text-sm font-semibold text-foreground">Speaking Speed Rate</label>
                <span class="font-mono text-xs bg-background px-2.5 py-1 rounded-md text-foreground border border-border/80 shadow-sm font-bold">{{ form.speaking_rate.toFixed(1) }}x</span>
              </div>
              <input type="range" class="w-full accent-amber-500 cursor-grab active:cursor-grabbing" min="0.5" max="2.0" step="0.1" v-model.number="form.speaking_rate">
              <div class="flex justify-between text-[11px] font-medium text-muted-foreground">
                <span>Slow (0.5x)</span>
                <span>Fast (2.0x)</span>
              </div>
            </div>
          </div>
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
              <h3 class="font-semibold text-lg text-foreground">Advanced Limits & STT</h3>
              <p class="text-xs text-muted-foreground mt-0.5">Language mapping and guardrails.</p>
            </div>
          </div>
        </div>
        <div class="p-6 grid grid-cols-1 md:grid-cols-2 gap-8 bg-background/20">
          <div class="space-y-2">
            <label class="text-sm font-semibold text-foreground">STT Streaming Language</label>
            <select class="flex h-11 w-full rounded-md border border-input bg-background px-4 py-2 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-rose-500 focus:border-rose-500" v-model="form.stt_language">
              <option value="en-US">English (US)</option>
              <option value="en-UK">English (UK)</option>
              <option value="ur-PK">Urdu (PK)</option>
              <option value="ar">Arabic</option>
            </select>
          </div>

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
            </select>
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
const voices = ref([]);
const loading = ref(true);
const saving = ref(false);

const form = ref({
  system_prompt_override: '',
  llm_model: 'meta-llama/llama-3.3-70b-instruct',
  llm_temperature: 0.3,
  speaking_rate: 1.0,
  tts_voice_id: '224a2257dd4943209a683d27a5e41439',
  greeting_message: '',
  stt_language: 'en-US',
  max_call_duration_min: 15,
  subscription_tier: 'payg',
  included_minutes_balance: 0
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
        llm_model: cfg.llm_model || 'meta-llama/llama-3.3-70b-instruct',
        llm_temperature: cfg.llm_temperature !== undefined ? cfg.llm_temperature : 0.3,
        speaking_rate: cfg.speaking_rate !== undefined ? cfg.speaking_rate : 1.0,
        tts_voice_id: cfg.tts_voice_id || '224a2257dd4943209a683d27a5e41439',
        greeting_message: cfg.greeting_message || '',
        stt_language: cfg.stt_language || 'en-US',
        max_call_duration_min: cfg.max_call_duration_min || 15,
        subscription_tier: t.subscription_tier || 'payg',
        included_minutes_balance: t.included_minutes_balance || 0
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

const fetchVoices = async () => {
  try {
    const res = await api.get('/api/super/fish-audio/voices');
    voices.value = res.data?.items || [];
  } catch (err) {
    console.error(err);
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
      included_minutes_balance: form.value.included_minutes_balance
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
  await Promise.all([fetchTenant(), fetchVoices()]);
  loading.value = false;
});
</script>
