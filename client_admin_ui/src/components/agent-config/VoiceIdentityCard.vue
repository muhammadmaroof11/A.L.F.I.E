<template>
  <div class="glass-panel p-6 rounded-xl relative overflow-hidden group border border-border/50 space-y-4">
    <div class="flex items-center justify-between">
      <h3 class="text-xs font-semibold uppercase tracking-wider text-muted-foreground flex items-center gap-2">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="text-primary">
          <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
          <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
        </svg>
        Voice Engine & Identity
      </h3>
      <span class="text-[10px] font-mono text-primary font-bold uppercase bg-primary/10 px-2 py-0.5 rounded">
        {{ voiceConfig.provider || 'fish_audio' }}
      </span>
    </div>

    <div class="space-y-3">
      <!-- Voice Provider -->
      <div class="space-y-1.5">
        <label class="text-xs font-medium text-foreground">TTS Voice Provider</label>
        <select
          v-model="voiceConfig.provider"
          class="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-xs focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-primary"
        >
          <option value="cartesia">Cartesia Sonic (90ms Ultra-Low Latency)</option>
          <option value="fish_audio">Fish Audio S2.1 Pro (Dynamic Emotion)</option>
          <option value="elevenlabs">ElevenLabs Turbo v2.5 (High Fidelity)</option>
          <option value="deepgram">Deepgram Aura (Zero-Config Fallback)</option>
          <option value="openai">OpenAI TTS (Alloy/Nova)</option>
        </select>
      </div>

      <!-- Voice Preset / ID -->
      <div class="space-y-1.5">
        <label class="text-xs font-medium text-foreground">Voice Persona ID / Preset</label>
        <input
          v-model="voiceConfig.voice_id"
          type="text"
          placeholder="e.g. 224a2257dd4943209a683d27a5e41439"
          class="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-xs font-mono focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-primary"
        />
      </div>

      <!-- Speed & Latency Mode -->
      <div class="grid grid-cols-2 gap-3 pt-1">
        <div class="space-y-1.5">
          <label class="text-xs font-medium text-foreground">Speaking Rate ({{ voiceConfig.speed || 1.0 }}x)</label>
          <input
            v-model.number="voiceConfig.speed"
            type="range"
            min="0.8"
            max="1.3"
            step="0.05"
            class="w-full accent-primary"
          />
        </div>
        <div class="space-y-1.5">
          <label class="text-xs font-medium text-foreground">Latency Mode</label>
          <select
            v-model="voiceConfig.latency_mode"
            class="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-xs focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-primary"
          >
            <option value="ultra_low">Ultra-Low (<120ms)</option>
            <option value="balanced">Balanced (High Quality)</option>
            <option value="expressive">Max Expressiveness</option>
          </select>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  voiceConfig: {
    type: Object,
    required: true,
  },
});
</script>
