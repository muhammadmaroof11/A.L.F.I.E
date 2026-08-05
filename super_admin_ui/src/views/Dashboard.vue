<template>
  <div>
    <!-- Stats Row -->
    <div class="grid grid-cols-4 gap-6 mb-8">
      <div class="bg-bgBase border border-bgSurface p-4">
        <div class="text-xs font-mono text-textMuted uppercase mb-2">Total Tokens</div>
        <div class="text-2xl font-mono text-blue">24.1M</div>
        <div class="text-xs font-mono text-green mt-2">+12% vs last week</div>
      </div>
      <div class="bg-bgBase border border-bgSurface p-4">
        <div class="text-xs font-mono text-textMuted uppercase mb-2">Total Cost</div>
        <div class="text-2xl font-mono text-white">$142.80</div>
        <div class="text-xs font-mono text-red mt-2">+$12.40 today</div>
      </div>
      <div class="bg-bgBase border border-bgSurface p-4">
        <div class="text-xs font-mono text-textMuted uppercase mb-2">Active Tenants</div>
        <div class="text-2xl font-mono text-white">4</div>
        <div class="text-xs font-mono text-green mt-2">Online</div>
      </div>
      <div class="bg-bgBase border border-bgSurface p-4">
        <div class="text-xs font-mono text-textMuted uppercase mb-2">Avg Latency</div>
        <div class="text-2xl font-mono text-white">412ms</div>
        <div class="text-xs font-mono text-textMuted mt-2">LLM + TTS</div>
      </div>
    </div>

    <!-- Main Dashboard Area -->
    <div class="grid grid-cols-3 gap-6">
      <div class="col-span-2 bg-bgBase border border-bgSurface p-6">
        <h3 class="font-mono text-sm uppercase text-textMuted mb-6">Token Usage Trends</h3>
        <div class="h-64 flex items-end gap-2 px-4 border-b border-bgSurface pb-2 relative">
          <!-- Horizontal grid lines -->
          <div class="absolute w-full border-t border-bgSurface/30 bottom-1/4"></div>
          <div class="absolute w-full border-t border-bgSurface/30 bottom-2/4"></div>
          <div class="absolute w-full border-t border-bgSurface/30 bottom-3/4"></div>
          
          <div class="flex-1 bg-blue/20 hover:bg-blue transition-colors rounded-t-sm" style="height: 30%"></div>
          <div class="flex-1 bg-blue/20 hover:bg-blue transition-colors rounded-t-sm" style="height: 45%"></div>
          <div class="flex-1 bg-blue/20 hover:bg-blue transition-colors rounded-t-sm" style="height: 25%"></div>
          <div class="flex-1 bg-blue/20 hover:bg-blue transition-colors rounded-t-sm" style="height: 60%"></div>
          <div class="flex-1 bg-blue/20 hover:bg-blue transition-colors rounded-t-sm" style="height: 40%"></div>
          <div class="flex-1 bg-blue/20 hover:bg-blue transition-colors rounded-t-sm" style="height: 80%"></div>
          <div class="flex-1 bg-blue rounded-t-sm" style="height: 95%; box-shadow: 0 0 10px rgba(59,130,246,0.5);"></div>
        </div>
      </div>

      <div class="bg-bgBase border border-bgSurface p-6">
        <h3 class="font-mono text-sm uppercase text-textMuted mb-6">Model Distribution</h3>
        <div class="space-y-4">
          <div>
            <div class="flex justify-between text-xs font-mono mb-1">
              <span class="text-white">Llama 3.1 8B</span>
              <span class="text-blue">68%</span>
            </div>
            <div class="w-full bg-bgSurface h-1.5 rounded-full overflow-hidden">
              <div class="bg-blue h-full w-[68%]"></div>
            </div>
          </div>
          <div>
            <div class="flex justify-between text-xs font-mono mb-1">
              <span class="text-white">GPT-4o Mini</span>
              <span class="text-green">22%</span>
            </div>
            <div class="w-full bg-bgSurface h-1.5 rounded-full overflow-hidden">
              <div class="bg-green h-full w-[22%]"></div>
            </div>
          </div>
          <div>
            <div class="flex justify-between text-xs font-mono mb-1">
              <span class="text-white">Nova-2 STT</span>
              <span class="text-amber">10%</span>
            </div>
            <div class="w-full bg-bgSurface h-1.5 rounded-full overflow-hidden">
              <div class="bg-amber h-full w-[10%]"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
</script>
