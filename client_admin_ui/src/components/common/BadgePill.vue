<template>
  <span
    class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-mono font-semibold border transition-all"
    :class="variantClasses"
  >
    <span v-if="pulse" class="w-1.5 h-1.5 rounded-full animate-pulse" :class="dotClasses"></span>
    <slot />
  </span>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  variant: {
    type: String,
    default: 'default', // 'emerald', 'amber', 'rose', 'sky', 'primary', 'default'
  },
  pulse: {
    type: Boolean,
    default: false,
  },
});

const variantClasses = computed(() => {
  switch (props.variant) {
    case 'emerald':
    case 'success':
    case 'active':
      return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20';
    case 'amber':
    case 'warning':
      return 'bg-amber-500/10 text-amber-400 border-amber-500/20';
    case 'rose':
    case 'danger':
    case 'takeover':
      return 'bg-rose-500/10 text-rose-400 border-rose-500/20 animate-pulse';
    case 'sky':
    case 'speaking':
      return 'bg-sky-500/10 text-sky-400 border-sky-500/20';
    case 'primary':
      return 'bg-primary/10 text-primary border-primary/20';
    default:
      return 'bg-muted text-muted-foreground border-border/60';
  }
});

const dotClasses = computed(() => {
  switch (props.variant) {
    case 'emerald':
    case 'success':
    case 'active':
      return 'bg-emerald-400';
    case 'amber':
    case 'warning':
      return 'bg-amber-400';
    case 'rose':
    case 'danger':
    case 'takeover':
      return 'bg-rose-400';
    case 'sky':
    case 'speaking':
      return 'bg-sky-400';
    case 'primary':
      return 'bg-primary';
    default:
      return 'bg-muted-foreground';
  }
});
</script>
