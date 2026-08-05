<template>
  <div class="space-y-8 max-w-5xl mx-auto pb-12">
    
    <!-- Header Area -->
    <div class="glass-elevated rounded-3xl p-8 border border-border relative overflow-hidden">
      <div class="absolute top-0 right-0 w-64 h-64 bg-accent/10 rounded-full blur-[80px] pointer-events-none"></div>
      
      <div class="flex items-start justify-between relative z-10">
        <div class="flex items-center gap-6">
          <div class="w-20 h-20 rounded-2xl bg-gradient-accent p-0.5 shadow-glow">
            <div class="w-full h-full bg-background rounded-[14px] flex items-center justify-center">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="url(#paint0_linear)" stroke-width="1.5"><path d="M12 2v20"></path><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>
                <defs>
                  <linearGradient id="paint0_linear" x1="12" y1="2" x2="12" y2="22" gradientUnits="userSpaceOnUse">
                    <stop stop-color="#14b8a6"/>
                    <stop offset="1" stop-color="#10b981"/>
                  </linearGradient>
                </defs>
              </svg>
            </div>
          </div>
          <div>
            <h2 class="text-2xl font-display font-bold text-white mb-2">Agent Persona Config</h2>
            <p class="text-textSecondary">Customize voice, tone, and system prompt for your AI assistant.</p>
          </div>
        </div>
        
        <button class="btn-glow px-6 py-2.5 rounded-xl text-sm font-medium text-white transition-all flex items-center gap-2">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"></path><polyline points="17 21 17 13 7 13 7 21"></polyline><polyline points="7 3 7 8 15 8"></polyline></svg>
          Save Configuration
        </button>
      </div>
    </div>

    <!-- Configuration Sections -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
      
      <!-- Left Column: Settings -->
      <div class="lg:col-span-1 space-y-6">
        
        <!-- Voice Settings -->
        <div class="glass p-6 rounded-2xl border border-border">
          <h3 class="text-sm font-bold text-textPrimary uppercase tracking-wider mb-5 flex items-center gap-2">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="text-accent"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path><path d="M19 10v2a7 7 0 0 1-14 0v-2"></path><line x1="12" y1="19" x2="12" y2="23"></line><line x1="8" y1="23" x2="16" y2="23"></line></svg>
            Voice Model
          </h3>
          <div class="space-y-4">
            <div>
              <label class="block text-xs font-medium text-textSecondary mb-2">Provider</label>
              <select class="w-full bg-background border border-border rounded-lg px-4 py-2.5 text-white text-sm focus:border-accent focus:ring-1 focus:ring-accent outline-none appearance-none">
                <option value="openai">OpenAI (TTS-1)</option>
                <option value="elevenlabs">ElevenLabs</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-medium text-textSecondary mb-2">Voice Identity</label>
              <select class="w-full bg-background border border-border rounded-lg px-4 py-2.5 text-white text-sm focus:border-accent focus:ring-1 focus:ring-accent outline-none appearance-none">
                <option value="alloy">Alloy (Neutral)</option>
                <option value="echo">Echo (Warm)</option>
                <option value="shimmer">Shimmer (Bright)</option>
              </select>
            </div>
            
            <button class="w-full mt-2 glass-elevated border border-border text-accent hover:text-accentSecondary hover:border-accent/30 py-2.5 rounded-lg text-sm font-medium transition-all flex items-center justify-center gap-2">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
              Test Voice
            </button>
          </div>
        </div>
        
        <!-- Behavior Settings -->
        <div class="glass p-6 rounded-2xl border border-border">
          <h3 class="text-sm font-bold text-textPrimary uppercase tracking-wider mb-5 flex items-center gap-2">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="text-accent"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>
            Dialer Config
          </h3>
          <div class="space-y-4">
            <div>
              <div class="flex justify-between items-center mb-2">
                <label class="text-xs font-medium text-textSecondary">Interruption Sensitivity</label>
                <span class="text-xs font-mono text-accent">0.8</span>
              </div>
              <input type="range" min="0" max="1" step="0.1" value="0.8" class="w-full accent-accent h-1 bg-surface rounded-lg appearance-none cursor-pointer">
            </div>
            
            <div class="flex items-center justify-between pt-4 border-t border-border/50">
              <label class="text-sm text-white font-medium">Record Calls</label>
              <div class="w-10 h-6 bg-accent rounded-full relative cursor-pointer">
                <div class="absolute right-1 top-1 w-4 h-4 bg-white rounded-full transition-transform"></div>
              </div>
            </div>
          </div>
        </div>

      </div>

      <!-- Right Column: Prompts -->
      <div class="lg:col-span-2 space-y-6">
        
        <div class="glass-elevated p-8 rounded-3xl border border-border h-full flex flex-col">
          <h3 class="text-sm font-bold text-textPrimary uppercase tracking-wider mb-2 flex items-center gap-2">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="text-accent"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
            System Prompt
          </h3>
          <p class="text-xs text-textSecondary mb-6">This prompt defines the agent's core identity, goals, and guardrails.</p>
          
          <div class="flex-1 relative">
            <textarea class="w-full h-full min-h-[300px] bg-background border border-border rounded-xl p-5 text-white font-mono text-sm leading-relaxed focus:border-accent focus:ring-1 focus:ring-accent outline-none resize-none custom-scrollbar" placeholder="Enter system prompt...">You are Alfie, an AI leasing assistant for our properties.
Your goal is to answer caller questions and collect their details to schedule a viewing.

Rules:
1. Be concise. Never speak for more than 2-3 sentences.
2. Ask for the caller's name if you don't have it.
3. If they ask about pricing, properties start at $2,500/mo.
4. Try to push for a viewing if they show interest.</textarea>
          </div>
        </div>
        
      </div>
      
    </div>
  </div>
</template>

<script setup>
// Configuration component layout
</script>
