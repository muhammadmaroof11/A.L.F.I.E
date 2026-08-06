<template>
  <div class="space-y-6 h-[calc(100vh-8rem)] flex flex-col">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 shrink-0">
      <div class="flex flex-col space-y-1">
        <h2 class="text-2xl font-semibold tracking-tight">Live Debug Feed</h2>
        <p class="text-sm text-muted-foreground">Real-time system telemetry and errors.</p>
      </div>
      <div class="flex items-center gap-3 w-full sm:w-auto">
        <select class="flex h-9 w-full sm:w-48 rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring">
          <option>All Tenants</option>
          <option>Alfie Realty PK</option>
        </select>
        <button class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring border border-input bg-background shadow-sm hover:bg-accent hover:text-accent-foreground h-9 px-4 py-2 shrink-0">
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="mr-2"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/></svg>
          Clear
        </button>
      </div>
    </div>
    
    <!-- Terminal Area -->
    <div class="flex-1 rounded-xl bg-[#0d1117] border border-border shadow-inner overflow-hidden flex flex-col font-mono text-[13px] relative">
      <!-- Terminal Header -->
      <div class="h-8 bg-[#161b22] border-b border-border/50 flex items-center px-4 shrink-0 justify-between">
        <div class="flex items-center gap-2">
          <div class="w-3 h-3 rounded-full bg-rose-500/80"></div>
          <div class="w-3 h-3 rounded-full bg-amber-500/80"></div>
          <div class="w-3 h-3 rounded-full bg-emerald-500/80"></div>
        </div>
        <div class="text-[10px] text-muted-foreground uppercase tracking-widest font-sans font-semibold flex items-center gap-2">
          <span class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
          Live Stream
        </div>
      </div>
      
      <!-- Terminal Content -->
      <div class="p-4 overflow-y-auto flex-1 space-y-1.5">
        
        <div class="flex items-start gap-3 text-slate-300 hover:bg-white/5 px-2 py-1 rounded transition-colors group">
          <span class="text-slate-500 shrink-0 select-none">10:42:05.122</span>
          <span class="text-emerald-400 font-semibold shrink-0 w-10">INFO</span>
          <span class="text-indigo-400 shrink-0 w-28">[worker-stt]</span>
          <span class="break-all flex-1">Deepgram stream connected for tenant <span class="bg-primary/20 text-primary px-1 rounded">alfie_realty_pk</span></span>
        </div>

        <div class="flex items-start gap-3 text-slate-300 hover:bg-white/5 px-2 py-1 rounded transition-colors group">
          <span class="text-slate-500 shrink-0 select-none">10:42:06.840</span>
          <span class="text-blue-400 font-semibold shrink-0 w-10">DBUG</span>
          <span class="text-indigo-400 shrink-0 w-28">[core-router]</span>
          <span class="break-all flex-1">Route calculated in 42ms (node_id: n8n_start_1)</span>
        </div>

        <div class="flex items-start gap-3 text-amber-200 bg-amber-500/10 hover:bg-amber-500/20 px-2 py-1 rounded transition-colors group">
          <span class="text-slate-500 shrink-0 select-none">10:42:15.002</span>
          <span class="text-amber-400 font-semibold shrink-0 w-10">WARN</span>
          <span class="text-indigo-400 shrink-0 w-28">[llm-bridge]</span>
          <span class="break-all flex-1">High latency from openrouter (1.2s TTFT)</span>
        </div>

        <div class="flex items-start gap-3 text-rose-200 bg-rose-500/10 hover:bg-rose-500/20 px-2 py-1 rounded transition-colors group border-l-2 border-rose-500">
          <span class="text-slate-500 shrink-0 select-none">10:42:18.991</span>
          <span class="text-rose-400 font-semibold shrink-0 w-10">ERR!</span>
          <span class="text-indigo-400 shrink-0 w-28">[webhook-out]</span>
          <span class="break-all flex-1">Failed to post call data to n8n: ETIMEDOUT 10.0.4.2:5678</span>
        </div>
        
        <!-- Simulate blinking cursor -->
        <div class="flex items-start gap-3 px-2 py-1">
          <span class="w-2 h-4 bg-slate-400 animate-pulse mt-0.5"></span>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
</script>
