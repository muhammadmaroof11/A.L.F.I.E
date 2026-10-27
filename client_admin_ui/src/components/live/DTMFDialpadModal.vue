<template>
  <ModalDialog
    :model-value="modelValue"
    @update:model-value="$emit('update:modelValue', $event)"
    title="SIP DTMF Keypad"
    subtitle="Transmit touch-tone audio pulses to navigate carrier IVR menus and extensions."
    max-width="sm"
  >
    <template #icon>
      <div class="w-9 h-9 rounded-lg bg-emerald-500/10 text-emerald-400 flex items-center justify-center border border-emerald-500/20">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
          <line x1="9" y1="9" x2="9" y2="9"></line>
          <line x1="15" y1="9" x2="15" y2="9"></line>
          <line x1="9" y1="15" x2="9" y2="15"></line>
          <line x1="15" y1="15" x2="15" y2="15"></line>
        </svg>
      </div>
    </template>

    <div class="space-y-4">
      <!-- Sequence Display -->
      <div class="glass-panel p-3 rounded-lg border border-border/60 flex items-center justify-between">
        <span class="text-xs font-mono font-bold tracking-widest text-primary min-h-[20px]">
          {{ dialedSequence || 'Ready...' }}
        </span>
        <button
          v-if="dialedSequence"
          @click="dialedSequence = dialedSequence.slice(0, -1)"
          class="text-xs text-muted-foreground hover:text-foreground p-1"
        >
          ⌫
        </button>
      </div>

      <!-- Numeric Keypad Grid -->
      <div class="grid grid-cols-3 gap-2">
        <button
          v-for="key in keypadKeys"
          :key="key.digit"
          @click="pressKey(key.digit)"
          class="glass-panel p-3 rounded-lg border border-border/50 hover:border-primary/50 hover:bg-primary/10 transition-all flex flex-col items-center justify-center active:scale-95 cursor-pointer"
        >
          <span class="text-base font-bold font-mono text-foreground">{{ key.digit }}</span>
          <span class="text-[9px] font-mono text-muted-foreground uppercase">{{ key.sub }}</span>
        </button>
      </div>

      <!-- Pause & Clear Controls -->
      <div class="flex items-center gap-2">
        <button
          @click="pressKey(',')"
          class="flex-1 py-1.5 rounded-lg border border-border text-xs text-muted-foreground hover:text-foreground hover:bg-muted/50 font-mono"
        >
          + Pause (500ms)
        </button>
        <button
          @click="dialedSequence = ''"
          class="px-3 py-1.5 rounded-lg border border-border text-xs text-muted-foreground hover:text-rose-400 hover:bg-rose-500/10 font-mono"
        >
          Clear
        </button>
      </div>
    </div>

    <template #footer>
      <button
        @click="$emit('update:modelValue', false)"
        class="px-3.5 py-1.5 rounded-lg border border-border text-xs text-muted-foreground hover:text-foreground hover:bg-muted/50 transition-colors"
      >
        Close
      </button>
      <button
        @click="transmitSequence"
        :disabled="!dialedSequence || isTransmitting"
        class="px-4 py-1.5 rounded-lg bg-primary text-primary-foreground text-xs font-semibold hover:bg-primary/90 transition-colors disabled:opacity-50 flex items-center gap-1.5"
      >
        <span>{{ isTransmitting ? 'Transmitting...' : 'Send Tones' }}</span>
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

const emit = defineEmits(['update:modelValue', 'transmit']);

const dialedSequence = ref('');
const isTransmitting = ref(false);

const keypadKeys = [
  { digit: '1', sub: ' ' },
  { digit: '2', sub: 'ABC' },
  { digit: '3', sub: 'DEF' },
  { digit: '4', sub: 'GHI' },
  { digit: '5', sub: 'JKL' },
  { digit: '6', sub: 'MNO' },
  { digit: '7', sub: 'PQRS' },
  { digit: '8', sub: 'TUV' },
  { digit: '9', sub: 'WXYZ' },
  { digit: '*', sub: ' ' },
  { digit: '0', sub: '+' },
  { digit: '#', sub: ' ' },
];

function pressKey(digit) {
  dialedSequence.value += digit;
}

function transmitSequence() {
  if (!dialedSequence.value) return;
  emit('transmit', dialedSequence.value);
  dialedSequence.value = '';
  emit('update:modelValue', false);
}
</script>
