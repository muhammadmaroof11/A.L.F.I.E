<template>
  <div class="glass-panel p-6 rounded-xl relative overflow-hidden group border border-border/50 space-y-5">
    <div class="flex items-center justify-between">
      <div>
        <h3 class="text-xs font-semibold uppercase tracking-wider text-muted-foreground flex items-center gap-2">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="text-primary">
            <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
            <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
          </svg>
          Operational Knowledge Base & FAQs
        </h3>
        <p class="text-xs text-muted-foreground mt-0.5">
          These verified Q&A pairs are prewarmed into Redis semantic vector cache for 0ms retrieval.
        </p>
      </div>
      <button
        @click="showAddModal = true"
        class="px-3 py-1.5 rounded-lg bg-primary/15 hover:bg-primary/25 border border-primary/30 text-primary text-xs font-semibold flex items-center gap-1.5 transition-all cursor-pointer"
      >
        <span>+ Add FAQ Item</span>
      </button>
    </div>

    <!-- FAQ Items List -->
    <div v-if="faqs.length === 0" class="p-8 border border-dashed border-border/60 rounded-xl text-center">
      <p class="text-xs text-muted-foreground">No knowledge base items configured yet.</p>
      <button
        @click="showAddModal = true"
        class="mt-3 px-3 py-1.5 rounded-md bg-muted text-foreground text-xs font-mono font-medium hover:bg-muted/80 transition-colors"
      >
        Add First Question & Answer
      </button>
    </div>

    <div v-else class="space-y-2.5">
      <div
        v-for="(faq, idx) in faqs"
        :key="faq.id || idx"
        class="glass-panel p-4 rounded-xl border border-border/50 hover:border-border transition-all flex items-start justify-between gap-4"
      >
        <div class="space-y-1 flex-1">
          <div class="flex items-center gap-2">
            <span class="text-[10px] font-mono font-bold uppercase bg-muted text-muted-foreground px-1.5 py-0.5 rounded">Q</span>
            <h4 class="text-xs font-semibold text-foreground">{{ faq.question }}</h4>
          </div>
          <div class="flex items-start gap-2 pt-1">
            <span class="text-[10px] font-mono font-bold uppercase bg-primary/10 text-primary px-1.5 py-0.5 rounded">A</span>
            <p class="text-xs text-muted-foreground leading-relaxed">{{ faq.answer }}</p>
          </div>
        </div>

        <button
          @click="$emit('delete-faq', idx)"
          class="text-xs text-muted-foreground hover:text-rose-400 p-1 rounded hover:bg-rose-500/10 transition-colors"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="3 6 5 6 21 6"></polyline>
            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
          </svg>
        </button>
      </div>
    </div>

    <!-- Modal to Add FAQ -->
    <ModalDialog
      v-model="showAddModal"
      title="Add Knowledge Base FAQ"
      subtitle="Add verified answers to common caller questions."
      max-width="md"
    >
      <div class="space-y-3">
        <div>
          <label class="text-xs font-medium text-foreground block mb-1">Question / Intent</label>
          <input
            v-model="newQuestion"
            type="text"
            placeholder="e.g. What are your weekend operating hours?"
            class="w-full rounded-md border border-input bg-background px-3 py-1.5 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
          />
        </div>
        <div>
          <label class="text-xs font-medium text-foreground block mb-1">Verified Factual Answer</label>
          <textarea
            v-model="newAnswer"
            rows="3"
            placeholder="e.g. We are open on Saturdays from 9am to 4pm, and closed on Sundays."
            class="w-full rounded-md border border-input bg-background px-3 py-1.5 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-primary custom-scrollbar resize-none"
          ></textarea>
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
          @click="addFaqItem"
          :disabled="!newQuestion.trim() || !newAnswer.trim()"
          class="px-4 py-1.5 rounded-lg bg-primary text-primary-foreground text-xs font-semibold hover:bg-primary/90 disabled:opacity-50"
        >
          Add to Knowledge Base
        </button>
      </template>
    </ModalDialog>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import ModalDialog from '../common/ModalDialog.vue';

defineProps({
  faqs: {
    type: Array,
    default: () => [],
  },
});

const emit = defineEmits(['add-faq', 'delete-faq']);

const showAddModal = ref(false);
const newQuestion = ref('');
const newAnswer = ref('');

function addFaqItem() {
  if (!newQuestion.value.trim() || !newAnswer.value.trim()) return;
  emit('add-faq', { question: newQuestion.value.trim(), answer: newAnswer.value.trim() });
  newQuestion.value = '';
  newAnswer.value = '';
  showAddModal.value = false;
}
</script>
