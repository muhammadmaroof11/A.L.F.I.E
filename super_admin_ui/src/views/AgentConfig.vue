<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
      <div class="flex flex-col space-y-1">
        <h2 class="text-2xl font-semibold tracking-tight">Global Agent Configuration</h2>
        <p class="text-sm text-muted-foreground">Manage base system behavior, LLM engine routing, and AI models.</p>
      </div>
      <button @click="saveConfiguration" :disabled="saving" class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground shadow hover:bg-primary/90 h-9 px-4 py-2 shrink-0">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="mr-2 h-4 w-4" v-if="!saving"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/><polyline points="17 21 17 13 7 13 7 21"/><polyline points="7 3 7 8 15 8"/></svg>
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="mr-2 h-4 w-4 animate-spin" v-else><path d="M21 12a9 9 0 1 1-6.219-8.56"/></svg>
        {{ saving ? 'Saving...' : 'Save Configuration' }}
      </button>
    </div>

    <!-- Success Banner -->
    <div v-if="successMsg" class="rounded-md border border-emerald-500/50 bg-emerald-500/10 p-4 text-emerald-500 flex items-start gap-3">
      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="mt-0.5 shrink-0"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
      <div class="text-sm font-medium">{{ successMsg }}</div>
    </div>

    <!-- Error Banner -->
    <div v-if="errorMsg" class="rounded-md border border-rose-500/50 bg-rose-500/10 p-4 text-rose-500 flex items-start gap-3">
      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="mt-0.5 shrink-0"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
      <div class="text-sm font-medium">{{ errorMsg }}</div>
    </div>

    <div v-if="loading" class="flex items-center justify-center h-32 text-muted-foreground">
      Loading configuration...
    </div>

    <form v-else @submit.prevent="saveConfiguration" class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      
      <!-- LLM ENGINE -->
      <div class="rounded-xl border bg-card text-card-foreground shadow-sm flex flex-col group">
        <div class="flex flex-col space-y-1.5 p-6 pb-4 border-b">
          <div class="flex justify-between items-center">
            <div>
              <h3 class="font-semibold leading-none tracking-tight">LLM Engine</h3>
              <p class="text-sm text-muted-foreground mt-1">Model routing and generation.</p>
            </div>
            <button type="button" @click="config.llm_enabled = !config.llm_enabled" :class="['relative inline-flex h-5 w-9 shrink-0 cursor-pointer items-center justify-center rounded-full focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background transition-colors', config.llm_enabled ? 'bg-primary' : 'bg-input']" role="switch" :aria-checked="config.llm_enabled">
              <span :class="['pointer-events-none block h-4 w-4 rounded-full bg-background shadow-lg ring-0 transition-transform', config.llm_enabled ? 'translate-x-2' : '-translate-x-2']"></span>
            </button>
          </div>
        </div>
        <div class="p-6 space-y-4" :class="{'opacity-50 pointer-events-none': !config.llm_enabled}">
          <div class="space-y-2">
            <label class="text-sm font-medium leading-none">Provider</label>
            <select class="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring" v-model="config.llm_provider">
              <option value="OpenRouter">OpenRouter (Unified LLM Gateway)</option>
            </select>
          </div>
          <div class="space-y-2">
            <label class="text-sm font-medium leading-none">Primary Conversational Model</label>
            <select class="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring" v-model="config.llm_model">
              <option value="meta-llama/llama-3.3-70b-instruct">meta-llama/llama-3.3-70b-instruct (Best Conversational Human-Like)</option>
              <option value="meta-llama/llama-3.1-8b-instruct">meta-llama/llama-3.1-8b-instruct (Ultra Fast 150ms TTFT)</option>
              <option value="anthropic/claude-3.5-sonnet">anthropic/claude-3.5-sonnet (High Empathy & Reasoning)</option>
              <option value="openai/gpt-4o">openai/gpt-4o (Omnimodal Intelligence)</option>
              <option value="qwen/qwen-2.5-72b-instruct">qwen/qwen-2.5-72b-instruct (Multilingual Specialist)</option>
            </select>
          </div>
          <div class="space-y-2">
            <div class="flex items-center justify-between">
              <label class="text-sm font-medium leading-none">Temperature (Warmth & Creativity)</label>
              <span class="font-mono text-xs text-muted-foreground">{{ config.llm_temperature }}</span>
            </div>
            <input type="range" class="w-full accent-primary" min="0" max="1" step="0.05" v-model.number="config.llm_temperature">
          </div>
          <div class="flex items-center space-x-2 pt-2">
            <input type="checkbox" id="semantic_caching" class="peer h-4 w-4 shrink-0 rounded-sm border border-primary ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 text-primary accent-primary" v-model="config.semantic_caching">
            <label for="semantic_caching" class="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
              Enable semantic caching
            </label>
          </div>
        </div>
      </div>

      <!-- SPEECH TO TEXT -->
      <div class="rounded-xl border bg-card text-card-foreground shadow-sm flex flex-col group">
        <div class="flex flex-col space-y-1.5 p-6 pb-4 border-b">
          <div class="flex justify-between items-center">
            <div>
              <h3 class="font-semibold leading-none tracking-tight">Speech-to-Text (STT)</h3>
              <p class="text-sm text-muted-foreground mt-1">Streaming transcription.</p>
            </div>
            <button type="button" @click="config.stt_enabled = !config.stt_enabled" :class="['relative inline-flex h-5 w-9 shrink-0 cursor-pointer items-center justify-center rounded-full focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background transition-colors', config.stt_enabled ? 'bg-primary' : 'bg-input']" role="switch" :aria-checked="config.stt_enabled">
              <span :class="['pointer-events-none block h-4 w-4 rounded-full bg-background shadow-lg ring-0 transition-transform', config.stt_enabled ? 'translate-x-2' : '-translate-x-2']"></span>
            </button>
          </div>
        </div>
        <div class="p-6 space-y-4" :class="{'opacity-50 pointer-events-none': !config.stt_enabled}">
          <div class="space-y-2">
            <label class="text-sm font-medium leading-none">Provider</label>
            <select class="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring" v-model="config.stt_provider">
              <option value="Deepgram (Nova 2)">Deepgram (Nova 2 Streaming)</option>
            </select>
          </div>
          <div class="space-y-2">
            <label class="text-sm font-medium leading-none">Language / Dialect</label>
            <select class="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring" v-model="config.stt_language">
              <option value="en-US">English (US)</option>
              <option value="en-UK">English (UK)</option>
              <option value="ur-PK">Urdu (PK)</option>
              <option value="ar">Arabic</option>
            </select>
          </div>
          <div class="space-y-2">
            <div class="flex items-center justify-between">
              <label class="text-sm font-medium leading-none">Endpointing (VAD) Sensitivity</label>
              <span class="font-mono text-xs text-muted-foreground">{{ config.vad_sensitivity }}ms</span>
            </div>
            <input type="range" class="w-full accent-primary" min="100" max="1000" step="50" v-model.number="config.vad_sensitivity">
          </div>
          <div class="flex items-center space-x-2 pt-2">
            <input type="checkbox" id="profanity_filter" class="peer h-4 w-4 shrink-0 rounded-sm border border-primary ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 text-primary accent-primary" v-model="config.profanity_filter">
            <label for="profanity_filter" class="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
              Enable Profanity Filter
            </label>
          </div>
        </div>
      </div>

      <!-- TEXT TO SPEECH -->
      <div class="rounded-xl border bg-card text-card-foreground shadow-sm flex flex-col group">
        <div class="flex flex-col space-y-1.5 p-6 pb-4 border-b">
          <div class="flex justify-between items-center">
            <div>
              <h3 class="font-semibold leading-none tracking-tight">Text-to-Speech (TTS)</h3>
              <p class="text-sm text-muted-foreground mt-1">Voice synthesis.</p>
            </div>
            <button type="button" @click="config.tts_enabled = !config.tts_enabled" :class="['relative inline-flex h-5 w-9 shrink-0 cursor-pointer items-center justify-center rounded-full focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background transition-colors', config.tts_enabled ? 'bg-primary' : 'bg-input']" role="switch" :aria-checked="config.tts_enabled">
              <span :class="['pointer-events-none block h-4 w-4 rounded-full bg-background shadow-lg ring-0 transition-transform', config.tts_enabled ? 'translate-x-2' : '-translate-x-2']"></span>
            </button>
          </div>
        </div>
        <div class="p-6 space-y-4" :class="{'opacity-50 pointer-events-none': !config.tts_enabled}">
          <div class="space-y-2">
            <label class="text-sm font-medium leading-none">Provider</label>
            <select class="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring" v-model="config.tts_provider">
              <option value="fish_audio">Fish Audio Engine</option>
            </select>
          </div>
          <div class="space-y-2" v-if="config.tts_provider === 'fish_audio'">
            <label class="text-sm font-medium leading-none">Discover Fish Audio Voices</label>
            <select class="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring" @change="e => { if(e.target.value) config.default_voice_id = e.target.value; }">
              <option value="">-- Browse Fish Audio Voices --</option>
              <option v-for="voice in fishAudioVoices" :key="voice.id" :value="voice.id">
                {{ voice.title }} (by {{ voice.author }})
              </option>
            </select>
          </div>
          <div class="space-y-2">
            <label class="text-sm font-medium leading-none">Voice ID (Global Default or Custom)</label>
            <input type="text" class="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring font-mono text-xs text-amber-500" v-model="config.default_voice_id" />
          </div>
          <div class="space-y-2">
            <div class="flex items-center justify-between">
              <label class="text-sm font-medium leading-none">Speaking Rate</label>
              <span class="font-mono text-xs text-muted-foreground">{{ config.speaking_rate }}x</span>
            </div>
            <input type="range" class="w-full accent-primary" min="0.5" max="2.0" step="0.1" v-model.number="config.speaking_rate">
          </div>
        </div>
      </div>

      <!-- CALL SETTINGS -->
      <div class="rounded-xl border bg-card text-card-foreground shadow-sm flex flex-col group">
        <div class="flex flex-col space-y-1.5 p-6 pb-4 border-b">
          <h3 class="font-semibold leading-none tracking-tight">Global Limits</h3>
          <p class="text-sm text-muted-foreground mt-1">Failsafes and guardrails.</p>
        </div>
        <div class="p-6 space-y-4">
          <div class="space-y-2">
            <label class="text-sm font-medium leading-none">Max Call Duration (minutes)</label>
            <input type="number" class="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring" v-model.number="config.max_call_duration_min" />
          </div>
          <div class="space-y-2">
            <label class="text-sm font-medium leading-none">Idle Timeout (seconds)</label>
            <input type="number" class="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring" v-model.number="config.idle_timeout_sec" />
          </div>
        </div>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '../services/api';

const loading = ref(true);
const saving = ref(false);
const successMsg = ref('');
const errorMsg = ref('');
const fishAudioVoices = ref([]);

const fetchFishAudioVoices = async () => {
  try {
    const res = await api.get('/api/super/fish-audio/voices');
    fishAudioVoices.value = res.data?.items || [];
  } catch (e) {
    console.warn('Could not fetch Fish Audio voices:', e);
  }
};

const config = ref({
  llm_enabled: true,
  llm_provider: 'OpenRouter',
  llm_model: 'meta-llama/llama-3.1-8b-instruct',
  llm_temperature: 0.3,
  semantic_caching: true,
  stt_enabled: true,
  stt_provider: 'Deepgram (Nova 2)',
  stt_language: 'en-US',
  vad_sensitivity: 400,
  profanity_filter: true,
  tts_enabled: true,
  tts_provider: 'fish_audio',
  default_voice_id: '224a2257dd4943209a683d27a5e41439',
  speaking_rate: 1.0,
  max_call_duration_min: 15,
  idle_timeout_sec: 30
});

const loadConfig = async () => {
  loading.value = true;
  errorMsg.value = '';
  try {
    const res = await api.get('/api/super/config/global_agent_config');
    if (res.data && Object.keys(res.data).length > 0) {
      config.value = { ...config.value, ...res.data };
    }
  } catch (err) {
    console.warn('Could not load global config:', err);
  } finally {
    loading.value = false;
  }
};

const saveConfiguration = async () => {
  saving.value = true;
  successMsg.value = '';
  errorMsg.value = '';
  try {
    await api.post('/api/super/config/global_agent_config', { value: config.value });
    successMsg.value = 'Global Agent Configuration saved successfully!';
    setTimeout(() => { successMsg.value = ''; }, 4000);
  } catch (err) {
    errorMsg.value = err.response?.data?.detail || 'Failed to save global configuration.';
  } finally {
    saving.value = false;
  }
};

onMounted(() => {
  loadConfig();
  fetchFishAudioVoices();
});
</script>
