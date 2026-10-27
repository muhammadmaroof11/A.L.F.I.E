<template>
  <div class="relative w-full flex items-center justify-center overflow-hidden rounded-lg bg-muted/20 border border-border/40 py-2">
    <canvas ref="canvasEl" :width="width" :height="height" class="w-full h-full max-h-12"></canvas>
  </div>
</template>

<script setup>
import { ref, toRef } from 'vue';
import { useWaveform } from '../../composables/useWaveform';

const props = defineProps({
  speakerState: {
    type: String,
    default: 'idle', // 'caller_speaking', 'agent_speaking', 'idle'
  },
  width: {
    type: Number,
    default: 280,
  },
  height: {
    type: Number,
    default: 40,
  },
});

const canvasEl = ref(null);
const speakerStateRef = toRef(props, 'speakerState');
useWaveform(canvasEl, speakerStateRef);
</script>
