<template>
  <div
    class="p-4 rounded-xl border transition-all duration-200"
    :class="isTakenOver ? 'bg-rose-500/10 border-rose-500/30 shadow-[0_0_20px_hsl(var(--destructive)/0.15)]' : 'glass-panel border-border/60'"
  >
    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
      <!-- State Indicator -->
      <div class="flex items-center gap-3">
        <div
          class="w-8 h-8 rounded-lg flex items-center justify-center"
          :class="isTakenOver ? 'bg-rose-500/20 text-rose-400 animate-pulse' : 'bg-primary/10 text-primary'"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
            <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
            <line x1="12" y1="19" x2="12" y2="23"></line>
            <line x1="8" y1="23" x2="16" y2="23"></line>
          </svg>
        </div>
        <div>
          <div class="flex items-center gap-2">
            <span class="text-xs font-semibold text-foreground">
              {{ isTakenOver ? 'HUMAN SUPERVISOR TAKEOVER ACTIVE' : 'Supervisor Control Hub' }}
            </span>
            <BadgePill :variant="isTakenOver ? 'rose' : 'emerald'" :pulse="isTakenOver">
              {{ isTakenOver ? 'Agent Muted' : 'AI Agent Autonomous' }}
            </BadgePill>
          </div>
          <p class="text-[11px] text-muted-foreground mt-0.5">
            {{ isTakenOver ? 'Your microphone is live on the call. The AI agent has suspended speaking.' : 'Intervene instantly, inject private ghost prompts, or dial DTMF tones.' }}
          </p>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="flex items-center gap-2 w-full sm:w-auto">
        <template v-if="!isTakenOver">
          <button
            @click="$emit('takeover')"
            class="flex-1 sm:flex-initial px-3.5 py-1.5 rounded-lg bg-rose-600 hover:bg-rose-700 text-white text-xs font-semibold flex items-center justify-center gap-1.5 shadow-sm transition-all cursor-pointer"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
              <circle cx="8.5" cy="7" rel="icon" r="4"></circle>
              <polyline points="17 11 19 13 23 9"></polyline>
            </svg>
            <span>Take Over Call</span>
          </button>
        </template>
        <template v-else>
          <button
            @click="$emit('toggle-mic')"
            class="px-3 py-1.5 rounded-lg border text-xs font-medium flex items-center gap-1.5 transition-colors cursor-pointer"
            :class="isMicMuted ? 'bg-amber-500/10 text-amber-400 border-amber-500/30' : 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'"
          >
            <span>{{ isMicMuted ? 'Unmute Mic' : 'Mute Mic' }}</span>
          </button>
          <button
            @click="$emit('release')"
            class="flex-1 sm:flex-initial px-3.5 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold flex items-center justify-center gap-1.5 shadow-sm transition-all cursor-pointer"
          >
            <span>Release to AI</span>
          </button>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import BadgePill from '../common/BadgePill.vue';

defineProps({
  isTakenOver: Boolean,
  isMicMuted: Boolean,
});

defineEmits(['takeover', 'release', 'toggle-mic']);
</script>
