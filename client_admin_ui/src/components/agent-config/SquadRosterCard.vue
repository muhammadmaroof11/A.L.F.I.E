<template>
  <div class="glass-panel p-6 rounded-xl relative overflow-hidden group border border-border/50 space-y-5">
    <div class="flex items-center justify-between">
      <div>
        <h3 class="text-xs font-semibold uppercase tracking-wider text-muted-foreground flex items-center gap-2">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="text-primary">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
            <circle cx="9" cy="7" r="4"></circle>
            <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
            <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
          </svg>
          Multi-Agent Squad Roster (Phase 7)
        </h3>
        <p class="text-xs text-muted-foreground mt-0.5">
          Configure specialized sub-agents for seamless in-memory zero-reconnect live call handoffs.
        </p>
      </div>
      <button
        @click="showAddModal = true"
        class="px-3 py-1.5 rounded-lg bg-primary/15 hover:bg-primary/25 border border-primary/30 text-primary text-xs font-semibold flex items-center gap-1.5 transition-all cursor-pointer"
      >
        <span>+ Add Squad Member</span>
      </button>
    </div>

    <!-- Squad Members List -->
    <div v-if="squadMembers.length === 0" class="p-8 border border-dashed border-border/60 rounded-xl text-center">
      <p class="text-xs text-muted-foreground">No sub-agent squad members added yet. Add specialized agents (e.g. Legal Intake Specialist, Billing Dispute Officer) for in-memory handoffs.</p>
      <button
        @click="showAddModal = true"
        class="mt-3 px-3 py-1.5 rounded-md bg-muted text-foreground text-xs font-mono font-medium hover:bg-muted/80 transition-colors"
      >
        Create First Squad Member
      </button>
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-3">
      <div
        v-for="(member, idx) in squadMembers"
        :key="member.agent_id || idx"
        class="glass-panel p-4 rounded-xl border border-border/50 hover:border-primary/40 transition-all space-y-2 relative"
      >
        <div class="flex items-start justify-between">
          <div>
            <h4 class="text-xs font-bold text-foreground">{{ member.name }}</h4>
            <span class="text-[10px] font-mono uppercase bg-primary/10 text-primary border border-primary/20 px-2 py-0.5 rounded-full inline-block mt-1">
              {{ member.role }}
            </span>
          </div>
          <button
            @click="$emit('delete-member', idx)"
            class="text-xs text-muted-foreground hover:text-rose-400 p-1 rounded hover:bg-rose-500/10 transition-colors"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="3 6 5 6 21 6"></polyline>
              <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
            </svg>
          </button>
        </div>

        <p class="text-[11px] text-muted-foreground line-clamp-2">
          {{ member.system_prompt || 'No specialized instructions set.' }}
        </p>

        <div v-if="member.greeting_message" class="text-[10px] text-primary/80 italic">
          "{{ member.greeting_message }}"
        </div>
      </div>
    </div>

    <!-- Modal to Add Squad Member -->
    <ModalDialog
      v-model="showAddModal"
      title="Add Multi-Agent Squad Member"
      subtitle="Register a specialized sub-agent for live call transfers."
      max-width="md"
    >
      <div class="space-y-3">
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="text-xs font-medium text-foreground block mb-1">Agent Name</label>
            <input
              v-model="newMember.name"
              type="text"
              placeholder="e.g. Sarah Miller"
              class="w-full rounded-md border border-input bg-background px-3 py-1.5 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
            />
          </div>
          <div>
            <label class="text-xs font-medium text-foreground block mb-1">Role Identifier</label>
            <input
              v-model="newMember.role"
              type="text"
              placeholder="e.g. legal_intake_specialist"
              class="w-full rounded-md border border-input bg-background px-3 py-1.5 text-xs font-mono text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
            />
          </div>
        </div>

        <div>
          <label class="text-xs font-medium text-foreground block mb-1">Specialized System Prompt</label>
          <textarea
            v-model="newMember.system_prompt"
            rows="3"
            placeholder="Instructions and qualification criteria for this sub-agent..."
            class="w-full rounded-md border border-input bg-background px-3 py-1.5 text-xs font-mono text-foreground focus:outline-none focus:ring-1 focus:ring-primary custom-scrollbar resize-none"
          ></textarea>
        </div>

        <div>
          <label class="text-xs font-medium text-foreground block mb-1">Custom Spoken Handoff Greeting (Optional)</label>
          <input
            v-model="newMember.greeting_message"
            type="text"
            placeholder="e.g. Hello, I'm Sarah from the Legal Intake squad. How can I help?"
            class="w-full rounded-md border border-input bg-background px-3 py-1.5 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
          />
        </div>
      </div>

      <template #footer>
        <button
          @click="showAddModal = false"
          class="px-3.5 py-1.5 rounded-lg border border-border text-xs text-muted-foreground hover:text-foreground"
        >
          Cancel
        </button>
        <button
          @click="addMemberItem"
          :disabled="!newMember.name.trim() || !newMember.role.trim()"
          class="px-4 py-1.5 rounded-lg bg-primary text-primary-foreground text-xs font-semibold hover:bg-primary/90 disabled:opacity-50"
        >
          Add to Squad
        </button>
      </template>
    </ModalDialog>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import ModalDialog from '../common/ModalDialog.vue';

defineProps({
  squadMembers: {
    type: Array,
    default: () => [],
  },
});

const emit = defineEmits(['add-member', 'delete-member']);

const showAddModal = ref(false);
const newMember = ref({
  name: '',
  role: '',
  system_prompt: '',
  greeting_message: '',
});

function addMemberItem() {
  if (!newMember.value.name.trim() || !newMember.value.role.trim()) return;
  emit('add-member', { ...newMember.value });
  newMember.value = { name: '', role: '', system_prompt: '', greeting_message: '' };
  showAddModal.value = false;
}
</script>
