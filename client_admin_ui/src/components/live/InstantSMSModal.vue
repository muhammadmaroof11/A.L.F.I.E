<template>
  <ModalDialog
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    title="Instant SMS Follow-up"
    subtitle="Dispatch booking confirmations, portal links, or payment receipts directly to the caller's phone."
    max-width="md"
  >
    <template #icon>
      <div class="w-9 h-9 rounded-lg bg-sky-500/10 text-sky-400 flex items-center justify-center border border-sky-500/20">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path>
          <polyline points="22,6 12,13 2,6"></polyline>
        </svg>
      </div>
    </template>

    <div class="space-y-4">
      <div>
        <label class="text-xs font-medium text-foreground block mb-1.5">Recipient Mobile Number</label>
        <input
          v-model="targetPhone"
          type="text"
          placeholder="+1 (555) 000-0000"
          class="w-full rounded-lg border border-border bg-background px-3 py-2 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-primary font-mono"
        />
      </div>

      <div>
        <label class="text-xs font-medium text-foreground block mb-1.5">Message Content</label>
        <textarea
          v-model="smsContent"
          rows="3"
          placeholder="Hi! Here is the confirmation link for your appointment..."
          class="w-full rounded-lg border border-border bg-background px-3 py-2 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-primary custom-scrollbar resize-none"
        ></textarea>
      </div>

      <!-- Quick Template Buttons -->
      <div>
        <span class="text-[11px] font-mono text-muted-foreground block mb-1.5">Templates:</span>
        <div class="flex flex-wrap gap-1.5">
          <button
            v-for="tpl in templates"
            :key="tpl.title"
            @click="smsContent = tpl.text"
            class="px-2 py-1 rounded bg-muted hover:bg-muted/80 text-[11px] text-muted-foreground hover:text-foreground border border-border/50 transition-colors"
          >
            {{ tpl.title }}
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
        @click="sendSMS"
        :disabled="!targetPhone || !smsContent || isSending"
        class="px-4 py-1.5 rounded-lg bg-primary text-primary-foreground text-xs font-semibold hover:bg-primary/90 transition-colors disabled:opacity-50 flex items-center gap-1.5"
      >
        <span>{{ isSending ? 'Sending...' : 'Send SMS Now' }}</span>
      </button>
    </template>
  </ModalDialog>
</template>

<script setup>
import { ref, watch } from 'vue';
import ModalDialog from '../common/ModalDialog.vue';

const props = defineProps({
  modelValue: Boolean,
  callId: String,
  defaultPhone: String,
});

const emit = defineEmits(['update:modelValue', 'send']);

const targetPhone = ref(props.defaultPhone || '');
const smsContent = ref('');
const isSending = ref(false);

watch(
  () => props.defaultPhone,
  (newVal) => {
    if (newVal) targetPhone.value = newVal;
  }
);

const templates = [
  { title: 'Calendar Confirmation', text: 'Thank you for calling! Your appointment has been booked. View details here: https://cal.com/booking' },
  { title: 'Intake Portal Link', text: 'Please complete your secure intake questionnaire before your consultation: https://alfie.ai/intake' },
  { title: 'Payment Receipt', text: 'Thank you! Your payment deposit has been received. View your invoice here: https://alfie.ai/receipt' },
];

function sendSMS() {
  if (!targetPhone.value || !smsContent.value) return;
  emit('send', { phone: targetPhone.value, message: smsContent.value });
  smsContent.value = '';
  emit('update:modelValue', false);
}
</script>
