<template>
  <div class="glass-panel p-6 rounded-xl relative overflow-hidden group border border-border/50 space-y-4">
    <div class="flex items-center justify-between">
      <h3 class="text-xs font-semibold uppercase tracking-wider text-muted-foreground flex items-center gap-2">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="text-primary">
          <circle cx="12" cy="12" r="10"></circle>
          <line x1="2" y1="12" x2="22" y2="12"></line>
        </svg>
        Cognitive LLM Engine
      </h3>
      <span class="text-[10px] font-mono text-primary font-bold uppercase bg-primary/10 px-2 py-0.5 rounded">
        {{ llmConfig.provider || 'openrouter' }}
      </span>
    </div>

    <div class="space-y-3">
      <!-- LLM Provider & Model -->
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <div class="space-y-1.5">
          <label class="text-xs font-medium text-foreground">Inference Gateway</label>
          <select
            v-model="llmConfig.provider"
            class="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-xs focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-primary"
          >
            <option value="openrouter">OpenRouter (Multi-Model Mesh)</option>
            <option value="litellm">Local LiteLLM Proxy (Port 4000)</option>
            <option value="groq">Groq LPU (Sub-150ms TTFT)</option>
            <option value="openai">OpenAI Direct</option>
            <option value="anthropic">Anthropic Direct</option>
          </select>
        </div>
        <div class="space-y-1.5">
          <label class="text-xs font-medium text-foreground">Model Architecture</label>
          <select
            v-model="llmConfig.model"
            class="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-xs focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-primary font-mono"
          >
            <option value="meta-llama/llama-3.3-70b-instruct">Llama 3.3 70B Instruct (Recommended)</option>
            <option value="meta-llama/llama-3.1-8b-instruct">Llama 3.1 8B Instruct (Ultra-Fast)</option>
            <option value="anthropic/claude-3.5-sonnet">Claude 3.5 Sonnet (Max Reasoning)</option>
            <option value="openai/gpt-4o-mini">GPT-4o Mini (Cost-Optimized)</option>
          </select>
        </div>
      </div>

      <!-- Temperature & Max Tokens -->
      <div class="grid grid-cols-2 gap-3">
        <div class="space-y-1.5">
          <label class="text-xs font-medium text-foreground">Temperature ({{ llmConfig.temperature || 0.7 }})</label>
          <input
            v-model.number="llmConfig.temperature"
            type="range"
            min="0.1"
            max="1.0"
            step="0.05"
            class="w-full accent-primary"
          />
        </div>
        <div class="space-y-1.5">
          <label class="text-xs font-medium text-foreground">Max Completion Tokens</label>
          <input
            v-model.number="llmConfig.max_tokens"
            type="number"
            min="100"
            max="4000"
            class="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-xs font-mono focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-primary"
          />
        </div>
      </div>

      <!-- Custom System Prompt -->
      <div class="space-y-1.5 pt-1">
        <div class="flex items-center justify-between">
          <label class="text-xs font-medium text-foreground">Custom System Instructions & Tone</label>
          <span class="text-[10px] font-mono text-muted-foreground">{{ (systemPrompt || '').length }} chars</span>
        </div>
        <textarea
          :value="systemPrompt"
          @input="$emit('update:systemPrompt', $event.target.value)"
          rows="5"
          placeholder="Specify exact company details, office hours, pricing disclaimers, or behavioral guidelines..."
          class="w-full rounded-lg border border-border bg-background px-3 py-2 text-xs font-mono text-foreground focus:outline-none focus:ring-1 focus:ring-primary custom-scrollbar resize-y"
        ></textarea>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  llmConfig: {
    type: Object,
    required: true,
  },
  systemPrompt: {
    type: String,
    default: '',
  },
});

defineEmits(['update:systemPrompt']);
</script>
