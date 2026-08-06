<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
      <div class="flex flex-col space-y-1">
        <h2 class="text-2xl font-semibold tracking-tight">Niches & Agent Personas</h2>
        <p class="text-sm text-muted-foreground">Define system prompts, default voice IDs, and behavior templates for vertical markets.</p>
      </div>
      <button @click="openModal()" class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground shadow hover:bg-primary/90 h-9 px-4 py-2 shrink-0">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="mr-2 h-4 w-4"><path d="M5 12h14"/><path d="M12 5v14"/></svg>
        Create New Persona
      </button>
    </div>

    <!-- Error message if any -->
    <div v-if="errorMessage" class="rounded-md border border-rose-500/50 bg-rose-500/10 p-4 text-rose-500 flex items-start gap-3">
      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="mt-0.5 shrink-0"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
      <div class="text-sm font-medium">{{ errorMessage }}</div>
    </div>

    <!-- Personas Grid -->
    <div v-if="loading" class="flex items-center justify-center h-32 text-muted-foreground">
      Loading personas...
    </div>
    
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div v-for="persona in personas" :key="persona.id" class="rounded-xl glass-panel text-card-foreground flex flex-col justify-between overflow-hidden group hover-glow transition-all duration-300 relative border border-white/5">
        <div class="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
        <div class="p-6 relative z-10">
          <div class="flex justify-between items-start mb-4">
            <div>
              <span class="inline-flex items-center rounded-full border border-primary/20 bg-primary/10 px-2.5 py-0.5 text-[10px] font-semibold uppercase tracking-widest text-primary transition-colors shadow-[0_0_8px_rgba(var(--primary),0.2)]">
                {{ persona.niche_name }}
              </span>
              <div class="text-lg font-semibold tracking-tight mt-2 text-foreground group-hover:text-primary transition-colors">
                {{ formatTitle(persona.niche_name) }}
              </div>
            </div>
            <div class="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
              <button @click="openModal(persona)" class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-xs font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring hover:bg-muted text-muted-foreground hover:text-foreground h-8 w-8" title="Edit Persona">
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4Z"/></svg>
              </button>
              <button @click="deletePersona(persona.id)" class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-xs font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring hover:bg-rose-500/10 text-rose-500 h-8 w-8" title="Delete Persona">
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/></svg>
              </button>
            </div>
          </div>

          <div class="space-y-4">
            <div class="space-y-1">
              <label class="text-[11px] font-medium text-muted-foreground uppercase tracking-wider">Voice ID</label>
              <div class="font-mono text-xs text-amber-500 truncate">
                {{ persona.voice_id || 'Default Fish Audio' }}
              </div>
            </div>

            <div class="space-y-1">
              <label class="text-[11px] font-medium text-muted-foreground uppercase tracking-wider">System Prompt Preview</label>
              <div class="bg-muted/50 rounded-md p-3 font-mono text-[11px] text-muted-foreground max-h-24 overflow-y-auto whitespace-pre-wrap border border-border/50">
                {{ persona.system_prompt }}
              </div>
            </div>

            <div v-if="persona.example_conversation" class="space-y-1">
              <label class="text-[11px] font-medium text-muted-foreground uppercase tracking-wider">Example Conversation</label>
              <div class="bg-muted/50 rounded-md p-3 text-[11px] text-muted-foreground max-h-20 overflow-y-auto whitespace-pre-wrap border border-border/50">
                {{ persona.example_conversation }}
              </div>
            </div>
          </div>
        </div>

        <div class="px-6 py-3 border-t border-white/5 bg-background/50 backdrop-blur-sm flex justify-between items-center text-[10px] text-muted-foreground relative z-10">
          <span class="font-mono">Created: {{ formatDate(persona.created_at) }}</span>
          <span class="flex items-center gap-1.5 text-emerald-500 font-medium">
            <span class="w-1.5 h-1.5 rounded-full bg-emerald-500 shadow-[0_0_5px_rgba(16,185,129,0.8)]"></span> Active Template
          </span>
        </div>
      </div>
    </div>

    <!-- Modal Form -->
    <div v-if="showModal" class="fixed inset-0 z-50 bg-background/80 backdrop-blur-md flex items-center justify-center">
      <div class="fixed left-[50%] top-[50%] z-50 grid w-full max-w-xl translate-x-[-50%] translate-y-[-50%] gap-4 glass-panel p-8 shadow-2xl sm:rounded-2xl max-h-[90vh] overflow-y-auto border border-white/10">
        <div class="flex flex-col space-y-1.5 sm:text-left">
          <h2 class="text-lg font-semibold leading-none tracking-tight">{{ editingId ? 'Edit Niche Persona' : 'Create New Niche Persona' }}</h2>
          <p class="text-sm text-muted-foreground">Configure system prompt guidelines & default voice ID.</p>
        </div>

        <form @submit.prevent="savePersona" class="space-y-4 py-4">
          <div class="space-y-2">
            <label class="text-sm font-medium leading-none">Niche Identifier</label>
            <input type="text" class="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50" v-model="form.niche_name" placeholder="e.g., medical_receptionist" required :disabled="!!editingId" />
            <p v-if="!editingId" class="text-[11px] text-muted-foreground">Use lowercase with underscores (snake_case).</p>
          </div>

          <div class="space-y-2">
            <label class="text-sm font-medium leading-none">Discover & Select Fish Audio Voice</label>
            <select class="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring" @change="e => { if(e.target.value) form.voice_id = e.target.value; }">
              <option value="">-- Select from Fish Audio Discover --</option>
              <option v-for="voice in fishAudioVoices" :key="voice.id" :value="voice.id">
                {{ voice.title }} (by {{ voice.author }})
              </option>
            </select>
          </div>

          <div class="space-y-2">
            <label class="text-sm font-medium leading-none">Fish Audio Voice ID (Selected or Custom)</label>
            <input type="text" class="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring font-mono text-xs text-amber-500" v-model="form.voice_id" placeholder="Paste custom Voice ID or select above..." required />
          </div>

          <div class="space-y-2">
            <label class="text-sm font-medium leading-none">System Prompt</label>
            <textarea class="flex min-h-[120px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring font-mono text-xs" v-model="form.system_prompt" rows="6" placeholder="ROLE: Medical Receptionist Assistant..." required></textarea>
            <p class="text-[11px] text-muted-foreground">Instructions & Persona Behavioral Guidelines</p>
          </div>

          <div class="space-y-2">
            <label class="text-sm font-medium leading-none">Example Conversation Script (Optional)</label>
            <textarea class="flex min-h-[80px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring" v-model="form.example_conversation" rows="3" placeholder="User: Hi, I'd like to book an appointment..."></textarea>
          </div>

          <div class="flex items-center justify-end gap-2 pt-4 border-t border-border mt-6">
            <button type="button" class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 border border-input bg-background shadow-sm hover:bg-accent hover:text-accent-foreground h-9 px-4 py-2" @click="closeModal">Cancel</button>
            <button type="submit" class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground shadow hover:bg-primary/90 h-9 px-4 py-2" :disabled="saving">
              {{ saving ? 'Saving...' : (editingId ? 'Update Persona' : 'Create Persona') }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '../services/api';

const personas = ref([]);
const fishAudioVoices = ref([]);
const loading = ref(true);
const saving = ref(false);
const showModal = ref(false);
const editingId = ref(null);
const errorMessage = ref('');

const fetchFishAudioVoices = async () => {
  try {
    const res = await api.get('/api/super/fish-audio/voices');
    fishAudioVoices.value = res.data?.items || [];
  } catch (err) {
    console.warn('Could not fetch Fish Audio voices:', err);
  }
};

const form = ref({
  niche_name: '',
  system_prompt: '',
  voice_id: '224a2257dd4943209a683d27a5e41439',
  example_conversation: ''
});

const formatTitle = (str) => {
  if (!str) return '';
  return str.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
};

const formatDate = (isoStr) => {
  if (!isoStr) return 'N/A';
  return new Date(isoStr).toLocaleDateString();
};

const fetchPersonas = async () => {
  loading.value = true;
  errorMessage.value = '';
  try {
    const res = await api.get('/api/super/personas');
    personas.value = res.data;
  } catch (err) {
    errorMessage.value = err.response?.data?.detail || 'Failed to load personas.';
  } finally {
    loading.value = false;
  }
};

const openModal = (persona = null) => {
  if (persona) {
    editingId.value = persona.id;
    form.value = {
      niche_name: persona.niche_name,
      system_prompt: persona.system_prompt,
      voice_id: persona.voice_id || '224a2257dd4943209a683d27a5e41439',
      example_conversation: persona.example_conversation || ''
    };
  } else {
    editingId.value = null;
    form.value = {
      niche_name: '',
      system_prompt: '',
      voice_id: '224a2257dd4943209a683d27a5e41439',
      example_conversation: ''
    };
  }
  showModal.value = true;
};

const closeModal = () => {
  showModal.value = false;
  editingId.value = null;
};

const savePersona = async () => {
  saving.value = true;
  try {
    if (editingId.value) {
      await api.put(`/api/super/personas/${editingId.value}`, form.value);
    } else {
      await api.post('/api/super/personas', form.value);
    }
    closeModal();
    fetchPersonas();
  } catch (err) {
    alert(err.response?.data?.detail || 'Failed to save persona.');
  } finally {
    saving.value = false;
  }
};

const deletePersona = async (id) => {
  if (!confirm('Are you sure you want to delete this niche persona template?')) return;
  try {
    await api.delete(`/api/super/personas/${id}`);
    fetchPersonas();
  } catch (err) {
    alert(err.response?.data?.detail || 'Failed to delete persona.');
  }
};

onMounted(() => {
  fetchPersonas();
  fetchFishAudioVoices();
});
</script>
