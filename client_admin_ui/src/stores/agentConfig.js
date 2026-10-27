import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { api } from '../services/api';

export const useAgentConfigStore = defineStore('agentConfig', () => {
  const loading = ref(false);
  const saving = ref(false);
  const error = ref(null);
  const isDirty = ref(false);

  const form = ref({
    agent_name: 'A.L.F.I.E Voice Agent',
    niche: 'general',
    system_prompt: '',
    greeting_message: 'Hello, thank you for calling. How can I help you today?',
    voice_config: {
      provider: 'fish_audio',
      voice_id: '224a2257dd4943209a683d27a5e41439',
      speed: 1.0,
      latency_mode: 'balanced',
    },
    llm_config: {
      provider: 'openrouter',
      model: 'meta-llama/llama-3.1-8b-instruct',
      temperature: 0.7,
      max_tokens: 1000,
    },
    vad_config: {
      min_silence_duration: 0.55,
      activation_threshold: 0.3,
      endpointing_preset: 'natural',
      anti_interruption_enabled: true,
    },
    enabled_tools: ['core_tools'],
    custom_tools: [],
    integrations: {
      webhook_url: '',
      webhook_secret: '',
      cal_com_api_key: '',
      cal_com_event_type_id: '',
      crm_auto_sync: true,
    },
    squad_members: [],
  });

  const faqs = ref([]);

  async function fetchConfig(agentId = null) {
    loading.value = true;
    error.value = null;
    try {
      const endpoint = agentId ? `/api/client/agents/${agentId}` : '/api/client/agent-config';
      const resp = await api.get(endpoint);
      if (resp.data) {
        const d = resp.data;
        form.value.agent_name = d.agent_name || d.name || form.value.agent_name;
        form.value.niche = d.niche || form.value.niche;
        form.value.system_prompt = d.system_prompt || '';
        form.value.greeting_message = d.greeting_message || form.value.greeting_message;
        if (d.voice_config) form.value.voice_config = { ...form.value.voice_config, ...d.voice_config };
        if (d.llm_config) form.value.llm_config = { ...form.value.llm_config, ...d.llm_config };
        if (d.vad_config) form.value.vad_config = { ...form.value.vad_config, ...d.vad_config };
        if (d.enabled_tools) form.value.enabled_tools = d.enabled_tools;
        if (d.custom_tools) form.value.custom_tools = d.custom_tools;
        if (d.integrations) form.value.integrations = { ...form.value.integrations, ...d.integrations };
        if (d.squad_members || d.squad_roster) form.value.squad_members = d.squad_members || d.squad_roster.members || [];
      }

      // Fetch Knowledge Base FAQs
      const faqResp = await api.get('/api/client/knowledge-base');
      if (faqResp.data && Array.isArray(faqResp.data.faqs)) {
        faqs.value = faqResp.data.faqs;
      }
      isDirty.value = false;
    } catch (err) {
      console.warn('Could not load remote agent config:', err);
      error.value = 'Loaded default configuration (offline/sandbox mode)';
    } finally {
      loading.value = false;
    }
  }

  async function saveConfig(agentId = null) {
    saving.value = true;
    error.value = null;
    try {
      const endpoint = agentId ? `/api/client/agents/${agentId}` : '/api/client/agent-config';
      await api.post(endpoint, form.value);

      // Save FAQs
      await api.post('/api/client/knowledge-base', { faqs: faqs.value });
      isDirty.value = false;
      return true;
    } catch (err) {
      console.error('Save configuration error:', err);
      error.value = 'Failed to save configuration';
      return false;
    } finally {
      saving.value = false;
    }
  }

  function addSquadMember(member) {
    form.value.squad_members.push({
      agent_id: member.agent_id || `squad_${Date.now()}`,
      name: member.name || 'Specialist',
      role: member.role || 'specialist',
      niche: member.niche || 'general',
      system_prompt: member.system_prompt || '',
      greeting_message: member.greeting_message || '',
      enabled_tools: member.enabled_tools || ['core_tools'],
      voice_config: member.voice_config || { provider: 'fish_audio' },
    });
    isDirty.value = true;
  }

  function removeSquadMember(index) {
    form.value.squad_members.splice(index, 1);
    isDirty.value = true;
  }

  function addFaq(question, answer) {
    if (!question || !answer) return;
    faqs.value.push({ id: `faq_${Date.now()}`, question, answer });
    isDirty.value = true;
  }

  function removeFaq(index) {
    faqs.value.splice(index, 1);
    isDirty.value = true;
  }

  return {
    loading,
    saving,
    error,
    isDirty,
    form,
    faqs,
    fetchConfig,
    saveConfig,
    addSquadMember,
    removeSquadMember,
    addFaq,
    removeFaq,
  };
});
