<template>
  <div class="space-y-8 max-w-5xl mx-auto pb-12">
    <!-- Header Banner Area -->
    <div class="glass-panel p-8 relative overflow-hidden rounded-xl border border-border/50">
      <div class="absolute top-0 right-0 w-64 h-64 bg-primary/10 rounded-full blur-[80px] pointer-events-none"></div>

      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 relative z-10">
        <div class="flex items-center gap-5">
          <div class="w-14 h-14 rounded-xl bg-primary/10 flex items-center justify-center text-primary shadow-sm border border-primary/20">
            <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M12 2v20"></path>
              <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>
            </svg>
          </div>
          <div>
            <div class="flex items-center gap-2">
              <h2 class="text-2xl font-bold tracking-tight text-foreground">
                {{ agentConfigStore.form.agent_name || 'Agent Persona Configuration' }}
              </h2>
              <span class="text-[10px] font-mono uppercase bg-primary/10 text-primary border border-primary/20 px-2 py-0.5 rounded-full font-bold">
                {{ agentConfigStore.form.niche || 'General' }}
              </span>
            </div>
            <p class="text-xs text-muted-foreground mt-0.5">
              Configure speech engine, system guardrails, operational knowledge base, and CRM webhooks.
            </p>
          </div>
        </div>

        <div class="flex items-center gap-3">
          <!-- Voice Test Simulator Button -->
          <button
            @click="showSimulator = true"
            type="button"
            class="glass-button bg-primary/10 text-primary hover:bg-primary/20 text-xs px-3.5 py-2 flex items-center gap-2 shadow-[0_0_12px_hsl(var(--primary)/0.2)]"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
              <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
              <line x1="12" y1="19" x2="12" y2="23"></line>
              <line x1="8" y1="23" x2="16" y2="23"></line>
            </svg>
            <span>Test Voice Agent</span>
          </button>

          <!-- Save Button -->
          <button
            @click="handleSave"
            :disabled="agentConfigStore.saving"
            class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-xs font-semibold transition-colors bg-primary text-primary-foreground shadow hover:bg-primary/90 h-9 px-4 py-2 gap-2 disabled:opacity-50"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"></path>
              <polyline points="17 21 17 13 7 13 7 21"></polyline>
              <polyline points="7 3 7 8 15 8"></polyline>
            </svg>
            <span>{{ agentConfigStore.saving ? 'Saving...' : 'Save Configuration' }}</span>
          </button>
        </div>
      </div>

      <!-- Navigation Tabs -->
      <div class="flex items-center gap-2 mt-6 pt-4 border-t border-border/30 relative z-10 text-xs font-medium overflow-x-auto">
        <button
          @click="activeTab = 'voice'"
          :class="activeTab === 'voice' ? 'bg-primary/15 text-primary border-primary/30' : 'text-muted-foreground hover:text-foreground border-transparent'"
          class="px-3.5 py-1.5 rounded-lg border transition-all flex items-center gap-1.5 whitespace-nowrap"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
            <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
          </svg>
          Voice & LLM Model
        </button>

        <button
          @click="activeTab = 'squad'"
          :class="activeTab === 'squad' ? 'bg-primary/15 text-primary border-primary/30' : 'text-muted-foreground hover:text-foreground border-transparent'"
          class="px-3.5 py-1.5 rounded-lg border transition-all flex items-center gap-1.5 whitespace-nowrap"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
            <circle cx="9" cy="7" r="4"></circle>
          </svg>
          Multi-Agent Squad (Phase 7)
        </button>

        <button
          @click="activeTab = 'kb'"
          :class="activeTab === 'kb' ? 'bg-primary/15 text-primary border-primary/30' : 'text-muted-foreground hover:text-foreground border-transparent'"
          class="px-3.5 py-1.5 rounded-lg border transition-all flex items-center gap-1.5 whitespace-nowrap"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
            <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
          </svg>
          Knowledge Base & FAQs
        </button>

        <button
          @click="activeTab = 'integrations'"
          :class="activeTab === 'integrations' ? 'bg-primary/15 text-primary border-primary/30' : 'text-muted-foreground hover:text-foreground border-transparent'"
          class="px-3.5 py-1.5 rounded-lg border transition-all flex items-center gap-1.5 whitespace-nowrap"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="16 18 22 12 16 6"></polyline>
            <polyline points="8 6 2 12 8 18"></polyline>
          </svg>
          CRM & Webhook Alerts
        </button>
      </div>
    </div>

    <!-- Alert / Toast Message -->
    <div v-if="saveSuccess" class="p-3 bg-emerald-500/10 border border-emerald-500/30 rounded-xl text-xs text-emerald-400 flex items-center gap-2">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
        <polyline points="22 4 12 14.01 9 11.01"></polyline>
      </svg>
      <span>Configuration saved and prewarmed in Redis cache successfully.</span>
    </div>

    <!-- TAB 1: Voice & Model Settings -->
    <div v-if="activeTab === 'voice'" class="grid grid-cols-1 lg:grid-cols-3 gap-8">
      <!-- Left 1 Col: Niche & Voice -->
      <div class="lg:col-span-1 space-y-6">
        <NicheSelectorCard v-model="agentConfigStore.form.niche" />
        <VoiceIdentityCard :voice-config="agentConfigStore.form.voice_config" />
      </div>

      <!-- Right 2 Cols: LLM Model & System Prompt -->
      <div class="lg:col-span-2 space-y-6">
        <LLMModelCard
          :llm-config="agentConfigStore.form.llm_config"
          v-model:system-prompt="agentConfigStore.form.system_prompt"
        />
      </div>
    </div>

    <!-- TAB 2: Multi-Agent Squad Settings (Phase 7) -->
    <div v-if="activeTab === 'squad'">
      <SquadRosterCard
        :squad-members="agentConfigStore.form.squad_members"
        @add-member="agentConfigStore.addSquadMember"
        @delete-member="agentConfigStore.removeSquadMember"
      />
    </div>

    <!-- TAB 3: Knowledge Base & FAQs -->
    <div v-if="activeTab === 'kb'">
      <KnowledgeBasePanel
        :faqs="agentConfigStore.faqs"
        @add-faq="({ question, answer }) => agentConfigStore.addFaq(question, answer)"
        @delete-faq="agentConfigStore.removeFaq"
      />
    </div>

    <!-- TAB 4: CRM & Webhook Integrations -->
    <div v-if="activeTab === 'integrations'">
      <IntegrationsPanel :integrations="agentConfigStore.form.integrations" />
    </div>

    <!-- Voice Simulator Modal -->
    <VoiceSimulatorModal
      v-if="showSimulator"
      :is-open="showSimulator"
      :niche="agentConfigStore.form.niche"
      :agent-name="agentConfigStore.form.agent_name"
      @close="showSimulator = false"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useAgentConfigStore } from '../stores/agentConfig';

import VoiceIdentityCard from '../components/agent-config/VoiceIdentityCard.vue';
import NicheSelectorCard from '../components/agent-config/NicheSelectorCard.vue';
import LLMModelCard from '../components/agent-config/LLMModelCard.vue';
import KnowledgeBasePanel from '../components/agent-config/KnowledgeBasePanel.vue';
import IntegrationsPanel from '../components/agent-config/IntegrationsPanel.vue';
import SquadRosterCard from '../components/agent-config/SquadRosterCard.vue';
import VoiceSimulatorModal from '../components/VoiceSimulatorModal.vue';

const agentConfigStore = useAgentConfigStore();
const activeTab = ref('voice');
const showSimulator = ref(false);
const saveSuccess = ref(false);

async function handleSave() {
  const ok = await agentConfigStore.saveConfig();
  if (ok) {
    saveSuccess.value = true;
    setTimeout(() => {
      saveSuccess.value = false;
    }, 4000);
  }
}

onMounted(() => {
  agentConfigStore.fetchConfig();
});
</script>
