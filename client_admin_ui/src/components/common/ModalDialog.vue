<template>
  <div
    v-if="modelValue"
    class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-background/80 backdrop-blur-sm transition-all duration-200"
    @click.self="handleClose"
  >
    <div
      class="glass-panel w-full rounded-xl border border-border shadow-2xl overflow-hidden relative animate-in fade-in zoom-in-95 duration-150"
      :class="maxWidthClass"
    >
      <!-- Modal Header -->
      <div class="px-6 py-4 border-b border-border/50 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <slot name="icon" />
          <div>
            <h3 class="text-sm font-semibold text-foreground">{{ title }}</h3>
            <p v-if="subtitle" class="text-xs text-muted-foreground">{{ subtitle }}</p>
          </div>
        </div>
        <button
          @click="handleClose"
          class="w-7 h-7 rounded-lg text-muted-foreground hover:text-foreground hover:bg-muted/50 flex items-center justify-center transition-colors cursor-pointer"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </button>
      </div>

      <!-- Modal Body -->
      <div class="p-6">
        <slot />
      </div>

      <!-- Modal Footer -->
      <div v-if="$slots.footer" class="px-6 py-3.5 bg-muted/20 border-t border-border/40 flex items-center justify-end gap-2.5">
        <slot name="footer" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted } from 'vue';

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false,
  },
  title: {
    type: String,
    required: true,
  },
  subtitle: {
    type: String,
    default: '',
  },
  maxWidth: {
    type: String,
    default: 'md', // 'sm', 'md', 'lg', 'xl', '2xl'
  },
});

const emit = defineEmits(['update:modelValue', 'close']);

const maxWidthClass = computed(() => {
  switch (props.maxWidth) {
    case 'sm': return 'max-w-sm';
    case 'md': return 'max-w-md';
    case 'lg': return 'max-w-lg';
    case 'xl': return 'max-w-xl';
    case '2xl': return 'max-w-2xl';
    default: return 'max-w-md';
  }
});

function handleClose() {
  emit('update:modelValue', false);
  emit('close');
}

function handleKeyDown(e) {
  if (e.key === 'Escape' && props.modelValue) {
    handleClose();
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeyDown);
});

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyDown);
});
</script>
