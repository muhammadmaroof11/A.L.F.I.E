<template>
  <div class="h-full flex flex-col gap-6">
    <div class="flex items-center justify-between flex-shrink-0">
      <div>
        <h2 class="text-3xl font-display font-bold text-white mb-2">Global Metrics</h2>
        <p class="text-sm text-textSecondary">Real-time system health and capacity overview</p>
      </div>
      <div class="flex items-center gap-2 px-4 py-2 glass rounded-lg text-sm text-textSecondary">
        <svg class="animate-spin h-4 w-4 text-accent" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
        Live Sync Active
      </div>
    </div>

    <!-- Bento Grid -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      
      <div class="glass-elevated rounded-2xl p-6 flex flex-col justify-between group hover:-translate-y-1 transition-transform duration-300">
        <div class="flex justify-between items-start mb-4">
          <div class="p-3 bg-accent/10 text-accent rounded-xl">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg>
          </div>
          <span class="text-xs font-medium text-green bg-green/10 px-2 py-1 rounded-full">+12% vs last hour</span>
        </div>
        <div>
          <div class="text-4xl font-display font-bold text-white mb-1">142</div>
          <div class="text-sm font-medium text-textSecondary uppercase tracking-wider">Active SIP Calls</div>
        </div>
      </div>

      <div class="glass-elevated rounded-2xl p-6 flex flex-col justify-between group hover:-translate-y-1 transition-transform duration-300">
        <div class="flex justify-between items-start mb-4">
          <div class="p-3 bg-accentSecondary/10 text-accentSecondary rounded-xl">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>
          </div>
          <span class="text-xs font-medium text-green bg-green/10 px-2 py-1 rounded-full">Stable</span>
        </div>
        <div>
          <div class="text-4xl font-display font-bold text-white mb-1">340<span class="text-lg text-textMuted ml-1">ms</span></div>
          <div class="text-sm font-medium text-textSecondary uppercase tracking-wider">Avg Agent Latency</div>
        </div>
      </div>

      <div class="glass-elevated rounded-2xl p-6 flex flex-col justify-between group hover:-translate-y-1 transition-transform duration-300">
        <div class="flex justify-between items-start mb-4">
          <div class="p-3 bg-amber/10 text-amber rounded-xl">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="2" width="20" height="8" rx="2" ry="2"></rect><rect x="2" y="14" width="20" height="8" rx="2" ry="2"></rect><line x1="6" y1="6" x2="6.01" y2="6"></line><line x1="6" y1="18" x2="6.01" y2="18"></line></svg>
          </div>
          <span class="text-xs font-medium text-amber bg-amber/10 px-2 py-1 rounded-full">84% Load</span>
        </div>
        <div>
          <div class="text-4xl font-display font-bold text-white mb-1">4.2<span class="text-lg text-textMuted ml-1">M</span></div>
          <div class="text-sm font-medium text-textSecondary uppercase tracking-wider">Tokens Processed (24h)</div>
        </div>
      </div>

    </div>
    
    <!-- System Diagram -->
    <div class="glass rounded-2xl p-6 flex-1 relative overflow-hidden group">
      <div class="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyMCIgaGVpZ2h0PSIyMCI+CgkJPGNpcmNsZSBjeD0iMiIgY3k9IjIiIHI9IjEiIGZpbGw9InJnYmEoMjU1LDI1NSwyNTUsMC4wNSkiLz4KCTwvc3ZnPg==')] [mask-image:radial-gradient(ellipse_at_center,black_40%,transparent_70%)]"></div>
      
      <div class="relative z-10 h-full flex flex-col">
        <h3 class="text-lg font-medium text-white mb-6">Cluster Architecture Status</h3>
        
        <div class="flex-1 flex items-center justify-center gap-12">
          
          <div class="flex flex-col gap-4">
            <div class="glass-elevated px-6 py-4 rounded-xl flex items-center gap-4 w-64 border-l-4 border-accent">
              <div class="w-3 h-3 rounded-full bg-accent animate-pulse shadow-[0_0_10px_currentColor]"></div>
              <div>
                <div class="text-sm font-medium text-white">Traefik Ingress</div>
                <div class="text-xs font-mono text-textMuted">99.99% Uptime</div>
              </div>
            </div>
          </div>
          
          <div class="w-16 h-0.5 bg-border relative">
            <div class="absolute w-2 h-2 bg-accent rounded-full -top-[3px] animate-[ping_2s_infinite]"></div>
          </div>
          
          <div class="flex flex-col gap-4">
            <div class="glass-elevated px-6 py-4 rounded-xl flex items-center gap-4 w-64 border-l-4 border-green">
              <div class="w-3 h-3 rounded-full bg-green animate-pulse shadow-[0_0_10px_currentColor]"></div>
              <div>
                <div class="text-sm font-medium text-white">LiveKit Voice Worker (x5)</div>
                <div class="text-xs font-mono text-textMuted">CPU 42% | RAM 2.1GB</div>
              </div>
            </div>
            
            <div class="glass-elevated px-6 py-4 rounded-xl flex items-center gap-4 w-64 border-l-4 border-accentSecondary">
              <div class="w-3 h-3 rounded-full bg-accentSecondary shadow-[0_0_10px_currentColor]"></div>
              <div>
                <div class="text-sm font-medium text-white">LiteLLM Gateway</div>
                <div class="text-xs font-mono text-textMuted">Cached: 64%</div>
              </div>
            </div>
          </div>

          <div class="w-16 h-0.5 bg-border relative"></div>

          <div class="flex flex-col gap-4">
            <div class="glass-elevated px-6 py-4 rounded-xl flex items-center gap-4 w-64 border-l-4 border-amber">
              <div class="w-3 h-3 rounded-full bg-amber shadow-[0_0_10px_currentColor]"></div>
              <div>
                <div class="text-sm font-medium text-white">Postgres DB</div>
                <div class="text-xs font-mono text-textMuted">Pool: 12/50 Conns</div>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// Static layout demonstration of system metrics
</script>
