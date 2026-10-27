<template>
  <ModalDialog
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    title="Ghost Whisper Directive"
    subtitle="Inject real-time private coaching instructions directly into the AI agent's turn prompt."
    max-width="md"
  >
    <template #icon>
      <div class="w-9 h-9 rounded-lg bg-indigo-500/10 text-indigo-400 flex items-center justify-center border border-indigo-500/20">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
        </svg>
      </div>
    </template>

    <div class="space-y-4">
      <div>
        <label class="text-xs font-medium text-foreground block mb-1.5">Whisper Instruction</label>
        <textarea
          v-model="promptText"
          rows="3"
          placeholder="e.g., Offer a 10% discount if they confirm booking now..."
          class="w-full rounded-lg border border-border bg-background px-3 py-2 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-primary custom-scrollbar resize-none"
        ></textarea>
      </div>

      <!-- Quick Preset Suggestions -->
      <div>
        <span class="text-[11px] font-mono text-muted-foreground block mb-1.5">Quick Directives:</span>
        <div class="flex flex-wrap gap-1.5">
          <button
            v-for="preset in presets"
            :key="preset"
            @click="promptText = preset"
            class="px-2 py-1 rounded bg-muted hover:bg-muted/80 text-[11px] text-muted-foreground hover:text-foreground border border-border/50 transition-colors"
          >
            {{ preset }}
          </button>
        </div>
      </div>
    </div>

    <template #footer>
      <button
        @click="$emit('update:modelValue', false)"
        class="px-3.5 py-1.5 rounded-lg border border-border text-xs text-muted-foreground hover:text-foreground hover:bg-muted/50 transition-colors"
      >
        Cancel
      </button>
      <button
        @click="submitWhisper"
        :disabled="!promptText.trim() || isSubmitting"
        class="px-4 py-1.5 rounded-lg bg-primary text-primary-foreground text-xs font-semibold hover:bg-primary/90 transition-colors disabled:opacity-50 flex items-center gap-1.5"
      >
        <span>{{ isSubmitting ? 'Injecting...' : 'Dispatch Whisper' }}</span>
      </button>
    </template>
  </ModalDialog>
</template>

<script setup>
import { ref } from 'vue';
import ModalDialog from '../common/ModalDialog.vue';

const props = defineProps({
  modelValue: Boolean,
  callId: String,
});

const emit = defineEmits(['update:modelValue', 'dispatch']);

const promptText = ref('');
const isSubmitting = ref(false);

const presets = [
  'Ask for their preferred date next week',
  'Offer a complimentary upgrade',
  'Politely de-escalate and apologize for delay',
  'Verify their primary contact number',
];

function submitWhisper() {
  if (!promptText.value.trim()) return;
  emit('dispatch', promptText.value.trim());
  promptText.value = '';
  emit('update:modelValue', false);
}
</script>
