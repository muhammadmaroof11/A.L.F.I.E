<template>
  <div class="max-w-5xl mx-auto space-y-6">
    <!-- Header with Actions & Filters -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2.5">
          <span>Interaction History</span>
          <span class="text-xs font-mono font-normal bg-primary/10 text-primary border border-primary/20 px-2.5 py-0.5 rounded-full">
            {{ filteredInteractions.length }} Calls Recorded
          </span>
        </h1>
        <p class="text-xs text-muted-foreground mt-0.5">Recorded phone calls, AI transcripts, automated QA scoring, and lost revenue triage.</p>
      </div>
      
      <!-- Action Toolbar -->
      <div class="flex flex-wrap items-center gap-2">
        <!-- Search -->
        <div class="relative">
          <svg class="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
          <input 
            v-model="searchQuery" 
            @input="debouncedSearch" 
            type="text" 
            placeholder="Search transcript, caller..." 
            class="h-8 pl-8 pr-3 rounded-lg border border-border bg-background/50 text-xs w-44 sm:w-52 focus:outline-none focus:ring-1 focus:ring-primary placeholder:text-muted-foreground/60"
          />
        </div>

        <!-- Conversion Filter -->
        <select 
          v-model="conversionFilter" 
          @change="fetchInteractions"
          class="h-8 px-2.5 rounded-lg border border-border bg-background/50 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
        >
          <option value="all">All Outcomes</option>
          <option value="lead_secured">✓ Lead Secured</option>
          <option value="follow_up_needed">⏳ Follow-up Needed</option>
          <option value="lost_opportunity">✕ Lost Opportunity</option>
          <option value="risk_only">⚠️ Critical Risk Only</option>
        </select>

        <!-- Frustration Filter -->
        <select 
          v-model="frustrationFilter" 
          @change="fetchInteractions"
          class="h-8 px-2.5 rounded-lg border border-border bg-background/50 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
        >
          <option value="all">All Frustration Levels</option>
          <option value="critical">🚨 Critical Frustration (≥70%)</option>
          <option value="elevated">⚠️ Elevated (40-69%)</option>
          <option value="normal">✓ Normal Sentiment (&lt;40%)</option>
        </select>

        <!-- Score Filter -->
        <select 
          v-model="scoreFilter" 
          class="h-8 px-2.5 rounded-lg border border-border bg-background/50 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
        >
          <option value="all">All QA Scores</option>
          <option value="high">High Quality (8-10)</option>
          <option value="medium">Moderate (5-7)</option>
          <option value="low">Needs Review (&lt;5)</option>
        </select>

        <!-- Export CSV Button -->
        <button 
          @click="exportCSV" 
          title="Export call logs to CSV"
          class="glass-button text-xs px-3 py-1.5 flex items-center gap-1.5 hover:bg-muted/50 border border-border/50 text-foreground transition-all"
        >
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
          Export CSV
        </button>

        <!-- Refresh -->
        <button @click="fetchInteractions" class="glass-button text-xs px-3 py-1.5 flex items-center gap-1.5 hover:bg-muted/50 border border-border/50">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" :class="{ 'animate-spin': loading }"><path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"/></svg>
        </button>
      </div>
    </div>

    <!-- Active Audio Player Bar (Sticky if playing) -->
    <div v-if="activePlayingId" class="glass-panel border border-primary/30 bg-primary/5 p-4 rounded-xl flex flex-col sm:flex-row items-center justify-between gap-4 animate-in fade-in slide-in-from-top-2 duration-300">
      <div class="flex items-center gap-3 w-full sm:w-auto">
        <button 
          @click="toggleAudioPlay(activePlayingCall)"
          class="w-9 h-9 rounded-full bg-primary text-primary-foreground flex items-center justify-center shadow hover:bg-primary/90 transition-all flex-shrink-0"
        >
          <svg v-if="isPlaying" width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="4" width="4" height="16"></rect><rect x="14" y="4" width="4" height="16"></rect></svg>
          <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
        </button>
        <div>
          <div class="text-xs font-semibold text-foreground flex items-center gap-2">
            <span>Audio Preview: {{ activePlayingCall?.caller }}</span>
            <span class="text-[10px] font-mono text-primary bg-primary/10 px-1.5 py-0.2 rounded border border-primary/20">{{ playbackSpeed }}x</span>
          </div>
          <p class="text-[11px] text-muted-foreground font-mono">Agent: {{ activePlayingCall?.agent_name }} · Duration: {{ activePlayingCall?.duration }}</p>
        </div>
      </div>

      <!-- Animated Soundwave Visualizer -->
      <div class="flex items-center gap-1 h-6 px-4">
        <div 
          v-for="bar in 24" 
          :key="bar" 
          class="w-1 bg-primary/70 rounded-full transition-all duration-150"
          :style="{ 
            height: isPlaying ? `${Math.max(4, Math.sin(bar + animTick) * 18 + 10)}px` : '4px',
            opacity: isPlaying ? 0.9 : 0.3
          }"
        ></div>
      </div>

      <!-- Controls -->
      <div class="flex items-center gap-2">
        <button 
          @click="cyclePlaybackSpeed" 
          class="text-[11px] font-mono font-semibold px-2 py-1 rounded bg-background/60 border border-border hover:bg-muted text-foreground"
          title="Playback speed"
        >
          {{ playbackSpeed }}x
        </button>
        <button 
          @click="stopAudioPlay" 
          class="p-1.5 rounded hover:bg-muted text-muted-foreground hover:text-foreground"
          title="Close player"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center p-12">
      <div class="animate-pulse flex flex-col items-center gap-4">
        <div class="h-10 w-10 rounded-full border-4 border-primary border-t-transparent animate-spin"></div>
        <p class="text-muted-foreground text-xs font-medium">Loading call interactions...</p>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="filteredInteractions.length === 0" class="glass-panel p-16 flex flex-col items-center justify-center text-center rounded-xl border border-border/50">
      <div class="w-14 h-14 rounded-full bg-primary/10 flex items-center justify-center mb-3 text-primary">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg>
      </div>
      <h3 class="text-lg font-semibold text-foreground mb-1">No Interactions Found</h3>
      <p class="text-xs text-muted-foreground max-w-sm">No call recordings matching your filters exist for this workspace yet.</p>
    </div>
    
    <!-- Interaction Cards -->
    <div v-else class="space-y-4">
      <div 
        v-for="interaction in filteredInteractions" 
        :key="interaction.id" 
        class="glass-panel group hover-glow p-5 transition-all duration-300 rounded-xl relative overflow-hidden border"
        :class="interaction.risk_flag ? 'border-rose-500/30 bg-rose-500/[0.02]' : 'border-border/50'"
      >
        <div class="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none"></div>
        <div class="relative">
          <!-- Card Header -->
          <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
            <div class="flex items-center gap-3.5">
              <button 
                @click="toggleAudioPlay(interaction)"
                :title="activePlayingId === interaction.id ? 'Close audio player' : 'Listen to call recording'"
                class="w-10 h-10 rounded-xl flex items-center justify-center shadow-sm transition-all group-hover:scale-105 cursor-pointer flex-shrink-0"
                :class="activePlayingId === interaction.id ? 'bg-primary text-primary-foreground' : 'bg-primary/10 text-primary hover:bg-primary/20'"
              >
                <svg v-if="activePlayingId === interaction.id" width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="4" width="4" height="16"></rect><rect x="14" y="4" width="4" height="16"></rect></svg>
                <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
              </button>
              <div>
                <div class="flex flex-wrap items-center gap-2">
                  <h3 class="font-semibold text-base text-foreground group-hover:text-primary transition-colors">
                    {{ interaction.caller }}
                  </h3>
                  <!-- Sentiment -->
                  <span v-if="interaction.sentiment" class="text-[9px] uppercase font-semibold px-1.5 py-0.5 rounded border" :class="interaction.sentiment === 'positive' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : interaction.sentiment === 'negative' ? 'bg-rose-500/10 text-rose-400 border-rose-500/20' : 'bg-muted text-muted-foreground border-border'">
                    {{ interaction.sentiment }}
                  </span>
                  <!-- Conversion Status Badge -->
                  <span 
                    v-if="interaction.conversion_status" 
                    class="text-[10px] font-medium px-2 py-0.5 rounded-full border flex items-center gap-1"
                    :class="getConversionBadgeClass(interaction.conversion_status)"
                  >
                    {{ formatConversionStatus(interaction.conversion_status) }}
                  </span>
                  <!-- Critical Risk Flag -->
                  <span 
                    v-if="interaction.risk_flag" 
                    class="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-rose-500/15 text-rose-400 border border-rose-500/30 flex items-center gap-1 animate-pulse"
                    :title="interaction.risk_reason || 'Critical risk detected'"
                  >
                    <span class="w-1.5 h-1.5 rounded-full bg-rose-500"></span>
                    At Risk
                  </span>
                  <!-- Frustration Indicator Badge -->
                  <span 
                    v-if="interaction.peak_frustration_score && interaction.peak_frustration_score >= 0.40" 
                    class="text-[10px] font-semibold px-2 py-0.5 rounded-full border flex items-center gap-1 font-mono"
                    :class="interaction.peak_frustration_score >= 0.70 
                      ? 'bg-rose-500/20 text-rose-300 border-rose-500/40 animate-pulse' 
                      : 'bg-amber-500/15 text-amber-300 border-amber-500/30'"
                    :title="`Peak Caller Frustration: ${Math.round(interaction.peak_frustration_score * 100)}%`"
                  >
                    <span>{{ interaction.peak_frustration_score >= 0.70 ? '🔥' : '⚠️' }}</span>
                    <span>{{ interaction.peak_frustration_score >= 0.70 ? 'Frustration' : 'Elevated' }} {{ Math.round(interaction.peak_frustration_score * 100) }}%</span>
                  </span>
                  <!-- DTMF Activity Badge -->
                  <button 
                    v-if="interaction.dtmf_events && interaction.dtmf_events.length > 0" 
                    @click.stop="toggleDtmfDetails(interaction)"
                    class="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 flex items-center gap-1 font-mono hover:bg-cyan-500/20 transition-all cursor-pointer"
                    :title="`DTMF Keypad Activity: ${interaction.dtmf_events.length} tone event(s). Click to toggle log.`"
                  >
                    <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8" cy="8" r="1"/><circle cx="12" cy="8" r="1"/><circle cx="16" cy="8" r="1"/><circle cx="8" cy="12" r="1"/><circle cx="12" cy="12" r="1"/><circle cx="16" cy="12" r="1"/><circle cx="8" cy="16" r="1"/><circle cx="12" cy="16" r="1"/><circle cx="16" cy="16" r="1"/></svg>
                    DTMF ({{ interaction.dtmf_events.length }})
                  </button>
                </div>
                <p class="text-[11px] font-mono text-muted-foreground mt-0.5">
                  {{ interaction.date }} • {{ interaction.duration }}
                  <span v-if="interaction.risk_reason" class="text-rose-400/90 ml-2 font-sans font-medium">— {{ interaction.risk_reason }}</span>
                </p>
              </div>
            </div>

            <!-- Agent & Interactive QA Badges -->
            <div class="flex items-center gap-2">
              <span class="px-2.5 py-1 rounded-md text-[11px] font-medium bg-background/80 border border-border text-muted-foreground flex items-center gap-1.5">
                <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
                {{ interaction.agent_name }}
              </span>
              <!-- Clickable QA Button -->
              <button 
                @click="openQaDetails(interaction)"
                :class="interaction.score >= 8 ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20 hover:bg-emerald-500/20' : interaction.score >= 6 ? 'bg-amber-500/10 text-amber-400 border-amber-500/20 hover:bg-amber-500/20' : 'bg-rose-500/10 text-rose-400 border-rose-500/20 hover:bg-rose-500/20'" 
                class="px-2.5 py-1 rounded-md text-[11px] font-semibold uppercase tracking-wider border font-mono transition-all flex items-center gap-1 cursor-pointer"
                title="Click to view full 4-point QA rubric"
              >
                <span>QA: {{ interaction.score }}/10</span>
                <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>
              </button>
              <button 
                @click="copyTranscript(interaction)"
                title="Copy Transcript"
                class="p-1.5 rounded-md hover:bg-muted text-muted-foreground hover:text-foreground transition-colors border border-border/50"
              >
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
              </button>
            </div>
          </div>

          <!-- Waveform Player (Appears when active/playing) -->
          <div v-if="activePlayingId === interaction.id" class="mb-4">
            <AudioWaveformPlayer 
              :ref="el => { if (el) playerRefs[interaction.id] = el }"
              :audio-url="getAudioUrl(interaction)"
              :waveform-data="interaction.waveform_data"
              :duration="getDurationSeconds(interaction)"
              :autoplay="true"
              @timeupdate="(sec, ms) => onPlayerTimeUpdate(interaction.id, ms)"
            />
          </div>

          <!-- DTMF Activity Drawer -->
          <div v-if="selectedDtmfInteractionId === interaction.id" class="mb-4 p-3 rounded-xl bg-cyan-500/5 border border-cyan-500/25 animate-in fade-in duration-200">
            <div class="flex items-center justify-between mb-2">
              <div class="flex items-center gap-1.5 text-xs font-semibold text-cyan-400 font-mono">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8" cy="8" r="1"/><circle cx="12" cy="8" r="1"/><circle cx="16" cy="8" r="1"/><circle cx="8" cy="12" r="1"/><circle cx="12" cy="12" r="1"/><circle cx="16" cy="12" r="1"/><circle cx="8" cy="16" r="1"/><circle cx="12" cy="16" r="1"/><circle cx="16" cy="16" r="1"/></svg>
                <span>RFC 4733 Telephony Tone Events</span>
              </div>
              <span class="text-[10px] text-muted-foreground font-mono">{{ interaction.dtmf_events.length }} event(s) recorded</span>
            </div>
            <div class="flex flex-wrap gap-2">
              <div 
                v-for="(evt, eIdx) in interaction.dtmf_events" 
                :key="eIdx" 
                class="px-2 py-1 rounded-lg bg-background/90 border text-[11px] font-mono flex items-center gap-1.5 shadow-sm"
                :class="evt.direction === 'inbound' ? 'border-cyan-500/30 text-cyan-300' : 'border-indigo-500/30 text-indigo-300'"
              >
                <span class="text-[9px] uppercase px-1 py-0.2 rounded font-semibold" :class="evt.direction === 'inbound' ? 'bg-cyan-500/20 text-cyan-400' : 'bg-indigo-500/20 text-indigo-400'">
                  {{ evt.direction === 'inbound' ? 'INBOUND' : 'OUTBOUND' }}
                </span>
                <span class="font-bold tracking-wider text-foreground">{{ evt.digits || evt.digit }}</span>
                <span v-if="evt.reason" class="text-[10px] text-muted-foreground font-sans">({{ evt.reason }})</span>
                <span v-if="evt.timestamp" class="text-[9px] text-muted-foreground font-mono">{{ new Date(evt.timestamp).toLocaleTimeString() }}</span>
              </div>
            </div>
          </div>

          <!-- Transcript Section -->
          <div v-if="interaction.transcript && interaction.transcript.length > 0" class="bg-background/80 rounded-xl p-4 border border-border/60 text-xs text-muted-foreground space-y-1.5 font-mono shadow-inner max-h-60 overflow-y-auto custom-scrollbar">
            <div 
              v-for="(msg, idx) in interaction.transcript" 
              :key="idx"
              @click="seekToTurn(interaction.id, msg.start_ms)"
              class="flex gap-2.5 p-2 rounded-lg transition-all cursor-pointer group/turn"
              :class="isTurnActive(interaction.id, msg) ? 'bg-primary/15 border border-primary/40 shadow-sm text-foreground' : 'hover:bg-muted/40'"
              :title="msg.start_ms !== undefined ? 'Click to jump audio to this turn' : ''"
            >
              <div class="flex items-center gap-1.5 min-w-[115px] flex-shrink-0">
                <span 
                  :class="msg.role === 'assistant' ? 'text-primary' : (msg.role === 'dtmf_caller' || msg.content?.includes('[CALLER KEYPAD INPUT]')) ? 'text-cyan-400' : msg.role === 'dtmf_outbound' ? 'text-indigo-400' : 'text-emerald-400'" 
                  class="font-semibold flex items-center gap-1 uppercase text-[10px]"
                >
                  <div class="w-1.5 h-1.5 rounded-full" :class="msg.role === 'assistant' ? 'bg-primary' : (msg.role === 'dtmf_caller' || msg.content?.includes('[CALLER KEYPAD INPUT]')) ? 'bg-cyan-400' : msg.role === 'dtmf_outbound' ? 'bg-indigo-400' : 'bg-emerald-400'"></div>
                  {{ msg.role === 'assistant' ? 'Alfie' : (msg.role === 'dtmf_caller' || msg.content?.includes('[CALLER KEYPAD INPUT]')) ? 'Keypad' : msg.role === 'dtmf_outbound' ? 'Agent DTMF' : 'Caller' }}
                </span>
                <span v-if="msg.start_ms !== undefined" class="text-[9px] font-mono text-muted-foreground/60 group-hover/turn:text-primary transition-colors">
                  {{ formatMs(msg.start_ms) }}
                </span>
              </div>
              <p class="leading-relaxed text-foreground/90 flex-1 font-sans text-xs" :class="(msg.role === 'dtmf_caller' || msg.content?.includes('[CALLER KEYPAD INPUT]')) ? 'text-cyan-300 font-mono font-medium' : msg.role === 'dtmf_outbound' ? 'text-indigo-300 font-mono font-medium' : ''">{{ msg.content }}</p>
            </div>
          </div>
          <div v-else class="bg-background/40 rounded-xl p-3 border border-border/50 text-xs text-muted-foreground italic font-mono">
            No audio transcript captured for this call session.
          </div>
        </div>
      </div>
    </div>

    <!-- QA Breakdown Modal -->
    <div v-if="selectedQaInteraction" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200">
      <div class="glass-panel border border-primary/30 w-full max-w-lg p-6 rounded-2xl shadow-2xl relative animate-in zoom-in-95 duration-200">
        <button 
          @click="selectedQaInteraction = null" 
          class="absolute top-4 right-4 p-1.5 rounded-lg hover:bg-muted text-muted-foreground hover:text-foreground"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
        </button>

        <div class="flex items-center gap-2 mb-1">
          <span class="text-xs font-mono uppercase text-primary bg-primary/10 px-2 py-0.5 rounded border border-primary/20">LLM-as-a-Judge Audit</span>
          <span :class="getConversionBadgeClass(selectedQaInteraction.conversion_status)" class="text-xs px-2 py-0.5 rounded-full border font-medium">
            {{ formatConversionStatus(selectedQaInteraction.conversion_status) }}
          </span>
        </div>
        <h3 class="text-lg font-bold text-foreground mb-1">Quality Assurance Rubric</h3>
        <p class="text-xs text-muted-foreground mb-5">{{ selectedQaInteraction.caller }} · {{ selectedQaInteraction.date }}</p>

        <!-- Rubric Progress Bars -->
        <div class="space-y-4">
          <!-- Intake Completeness -->
          <div>
            <div class="flex justify-between text-xs mb-1">
              <span class="font-medium text-foreground">Intake Completeness</span>
              <span class="font-mono text-primary font-semibold">{{ selectedQaInteraction.qa_breakdown?.intake_completeness_score || 85 }}%</span>
            </div>
            <div class="w-full bg-muted/60 h-2 rounded-full overflow-hidden">
              <div 
                class="bg-primary h-full rounded-full transition-all duration-500" 
                :style="{ width: `${selectedQaInteraction.qa_breakdown?.intake_completeness_score || 85}%` }"
              ></div>
            </div>
            <p class="text-[10px] text-muted-foreground mt-1">Verified caller contact identity, phone verification, and core problem intent.</p>
          </div>

          <!-- Empathy & Tone -->
          <div>
            <div class="flex justify-between text-xs mb-1">
              <span class="font-medium text-foreground">Empathy & Professional Tone</span>
              <span class="font-mono text-emerald-400 font-semibold">{{ selectedQaInteraction.qa_breakdown?.empathy_tone_score || 90 }}%</span>
            </div>
            <div class="w-full bg-muted/60 h-2 rounded-full overflow-hidden">
              <div 
                class="bg-emerald-500 h-full rounded-full transition-all duration-500" 
                :style="{ width: `${selectedQaInteraction.qa_breakdown?.empathy_tone_score || 90}%` }"
              ></div>
            </div>
            <p class="text-[10px] text-muted-foreground mt-1">Attentiveness, composed objection handling, and verbal backchanneling.</p>
          </div>

          <!-- Overall Quality Score -->
          <div>
            <div class="flex justify-between text-xs mb-1">
              <span class="font-medium text-foreground">Overall Effectiveness Score</span>
              <span class="font-mono text-cyan-400 font-semibold">{{ selectedQaInteraction.qa_breakdown?.overall_quality_score || (selectedQaInteraction.score * 10) }}%</span>
            </div>
            <div class="w-full bg-muted/60 h-2 rounded-full overflow-hidden">
              <div 
                class="bg-cyan-500 h-full rounded-full transition-all duration-500" 
                :style="{ width: `${selectedQaInteraction.qa_breakdown?.overall_quality_score || (selectedQaInteraction.score * 10)}%` }"
              ></div>
            </div>
          </div>
        </div>

        <!-- Caller Frustration Telemetry (Phase 19) -->
        <div 
          class="mt-4 p-3.5 rounded-xl border" 
          :class="(selectedQaInteraction.peak_frustration_score || 0) >= 0.70 
            ? 'bg-rose-500/10 border-rose-500/30' 
            : (selectedQaInteraction.peak_frustration_score || 0) >= 0.40 
              ? 'bg-amber-500/10 border-amber-500/30' 
              : 'bg-background/80 border-border/60'"
        >
          <div class="flex items-center justify-between mb-1.5">
            <span class="text-xs font-semibold flex items-center gap-1.5" :class="(selectedQaInteraction.peak_frustration_score || 0) >= 0.70 ? 'text-rose-400' : (selectedQaInteraction.peak_frustration_score || 0) >= 0.40 ? 'text-amber-400' : 'text-foreground'">
              <span>{{ (selectedQaInteraction.peak_frustration_score || 0) >= 0.70 ? '🚨 Critical Frustration Radar' : 'Caller Frustration Radar' }}</span>
            </span>
            <span class="font-mono text-xs font-bold" :class="(selectedQaInteraction.peak_frustration_score || 0) >= 0.70 ? 'text-rose-400' : (selectedQaInteraction.peak_frustration_score || 0) >= 0.40 ? 'text-amber-400' : 'text-emerald-400'">
              {{ Math.round((selectedQaInteraction.peak_frustration_score || 0) * 100) }}%
            </span>
          </div>
          <div class="w-full bg-muted/60 h-2 rounded-full overflow-hidden mb-2">
            <div 
              class="h-full rounded-full transition-all duration-500" 
              :class="(selectedQaInteraction.peak_frustration_score || 0) >= 0.70 ? 'bg-rose-500' : (selectedQaInteraction.peak_frustration_score || 0) >= 0.40 ? 'bg-amber-400' : 'bg-emerald-400'"
              :style="{ width: `${Math.min(100, Math.round((selectedQaInteraction.peak_frustration_score || 0) * 100))}%` }"
            ></div>
          </div>
          <div v-if="selectedQaInteraction.frustration_events && selectedQaInteraction.frustration_events.length > 0" class="space-y-1.5 mt-2 pt-2 border-t border-border/40">
            <div class="text-[10px] font-mono text-muted-foreground uppercase font-semibold">Detected Escalation Events:</div>
            <div v-for="(ev, idx) in selectedQaInteraction.frustration_events" :key="idx" class="text-[11px] font-mono p-2 rounded bg-background/60 border border-border/40 flex items-start justify-between gap-2">
              <div>
                <span class="text-rose-300 font-bold uppercase">{{ ev.reason?.replace('_', ' ') }}</span>
                <span v-if="ev.snippet" class="text-muted-foreground block text-[10px] italic mt-0.5">"{{ ev.snippet }}"</span>
              </div>
              <span class="text-rose-400 font-bold shrink-0">{{ Math.round((ev.score || 0.7) * 100) }}%</span>
            </div>
          </div>
        </div>

        <!-- Risk Warning if flagged -->
        <div v-if="selectedQaInteraction.risk_flag" class="mt-5 p-3 rounded-xl bg-rose-500/10 border border-rose-500/25">
          <div class="flex items-center gap-1.5 text-xs font-semibold text-rose-400 mb-0.5">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>
            <span>Critical Risk Flag Triggered</span>
          </div>
          <p class="text-xs text-rose-200/90 leading-relaxed">{{ selectedQaInteraction.risk_reason || 'Caller showed signs of dissatisfaction or high-value lost opportunity.' }}</p>
        </div>

        <div class="mt-6 flex justify-end">
          <button 
            @click="selectedQaInteraction = null" 
            class="px-4 py-2 rounded-xl bg-primary text-primary-foreground text-xs font-semibold hover:bg-primary/90 transition-colors"
          >
            Close Rubric
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import api from '../services/api';
import { useAuthStore } from '../stores/auth';
import AudioWaveformPlayer from '../components/AudioWaveformPlayer.vue';

const auth = useAuthStore();
const interactions = ref([]);
const loading = ref(true);
const searchQuery = ref('');
const scoreFilter = ref('all');
const conversionFilter = ref('all');
const frustrationFilter = ref('all');
const selectedQaInteraction = ref(null);
const selectedDtmfInteractionId = ref(null);
let searchTimer = null;

// Audio Player State & Turn Synchronization
const activePlayingId = ref(null);
const activePlayingCall = computed(() => interactions.value.find(i => i.id === activePlayingId.value));
const playerRefs = ref({});
const playbackMsById = ref({});
const isPlaying = ref(false);
const playbackSpeed = ref(1.0);
const animTick = ref(0);
let animInterval = null;

const getAudioUrl = (interaction) => {
  return interaction.audio_url || `/api/client/recordings/${interaction.id}/audio`;
};

const getDurationSeconds = (interaction) => {
  if (interaction.duration_seconds && typeof interaction.duration_seconds === 'number') {
    return interaction.duration_seconds;
  }
  if (typeof interaction.duration === 'string') {
    const m = interaction.duration.match(/(\d+)m/);
    const s = interaction.duration.match(/(\d+)s/);
    const mins = m ? parseInt(m[1]) : 0;
    const secs = s ? parseInt(s[1]) : 0;
    if (mins || secs) return mins * 60 + secs;
  }
  return 180;
};

const formatMs = (ms) => {
  if (!ms && ms !== 0) return '0:00';
  const totalSec = Math.floor(ms / 1000);
  const m = Math.floor(totalSec / 60);
  const s = totalSec % 60;
  return `${m}:${s < 10 ? '0' : ''}${s}`;
};

const onPlayerTimeUpdate = (callId, ms) => {
  playbackMsById.value[callId] = ms;
};

const isTurnActive = (callId, turn) => {
  if (activePlayingId.value !== callId) return false;
  const currentMs = playbackMsById.value[callId] || 0;
  if (turn.start_ms !== undefined && turn.end_ms !== undefined) {
    return currentMs >= turn.start_ms && currentMs <= turn.end_ms;
  }
  return false;
};

const seekToTurn = (callId, startMs) => {
  if (startMs === undefined) return;
  activePlayingId.value = callId;
  const player = playerRefs.value[callId];
  if (player && player.seekToMs) {
    player.seekToMs(startMs);
  }
};

const toggleAudioPlay = (interaction) => {
  if (!interaction) return;
  if (activePlayingId.value === interaction.id) {
    const player = playerRefs.value[interaction.id];
    if (player && player.togglePlay) {
      player.togglePlay();
    } else {
      activePlayingId.value = null;
      isPlaying.value = false;
    }
  } else {
    activePlayingId.value = interaction.id;
    isPlaying.value = true;
  }
};

const stopAudioPlay = () => {
  activePlayingId.value = null;
  isPlaying.value = false;
};

const cyclePlaybackSpeed = () => {
  const speeds = [1.0, 1.25, 1.5, 2.0];
  const nextIdx = (speeds.indexOf(playbackSpeed.value) + 1) % speeds.length;
  playbackSpeed.value = speeds[nextIdx];
};

const openQaDetails = (interaction) => {
  selectedQaInteraction.value = interaction;
};

const toggleDtmfDetails = (interaction) => {
  if (selectedDtmfInteractionId.value === interaction.id) {
    selectedDtmfInteractionId.value = null;
  } else {
    selectedDtmfInteractionId.value = interaction.id;
  }
};

const getConversionBadgeClass = (status) => {
  switch ((status || '').toLowerCase()) {
    case 'lead_secured':
      return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20';
    case 'follow_up_needed':
      return 'bg-amber-500/10 text-amber-400 border-amber-500/20';
    case 'lost_opportunity':
      return 'bg-rose-500/10 text-rose-400 border-rose-500/20';
    default:
      return 'bg-muted/80 text-muted-foreground border-border';
  }
};

const formatConversionStatus = (status) => {
  switch ((status || '').toLowerCase()) {
    case 'lead_secured':
      return '✓ Lead Secured';
    case 'follow_up_needed':
      return '⏳ Follow-up Needed';
    case 'lost_opportunity':
      return '✕ Lost Opportunity';
    default:
      return 'Inconclusive';
  }
};

const fetchInteractions = async () => {
  loading.value = true;
  try {
    const params = {};
    if (searchQuery.value) params.search = searchQuery.value;
    if (conversionFilter.value && conversionFilter.value !== 'all') {
      if (conversionFilter.value === 'risk_only') {
        params.risk_only = true;
      } else {
        params.conversion_status = conversionFilter.value;
      }
    }
    if (frustrationFilter.value && frustrationFilter.value !== 'all') {
      params.frustration_level = frustrationFilter.value;
    }
    const res = await api.get('/client/interactions', { params });
    interactions.value = res.data || [];
  } catch (err) {
    console.error("Failed to fetch interactions:", err);
  } finally {
    loading.value = false;
  }
};

const debouncedSearch = () => {
  if (searchTimer) clearTimeout(searchTimer);
  searchTimer = setTimeout(() => {
    fetchInteractions();
  }, 300);
};

const filteredInteractions = computed(() => {
  return interactions.value.filter(item => {
    // Score Filter
    if (scoreFilter.value === 'high' && item.score < 8) return false;
    if (scoreFilter.value === 'medium' && (item.score < 5 || item.score >= 8)) return false;
    if (scoreFilter.value === 'low' && item.score >= 5) return false;

    // Conversion Filter (Client-side fallback)
    if (conversionFilter.value === 'risk_only' && !item.risk_flag) return false;
    if (conversionFilter.value !== 'all' && conversionFilter.value !== 'risk_only') {
      if ((item.conversion_status || '').toLowerCase() !== conversionFilter.value.toLowerCase()) {
        return false;
      }
    }

    // Frustration Filter (Client-side fallback)
    if (frustrationFilter.value && frustrationFilter.value !== 'all') {
      const score = item.peak_frustration_score || 0;
      if (frustrationFilter.value === 'critical' && score < 0.70) return false;
      if (frustrationFilter.value === 'elevated' && (score < 0.40 || score >= 0.70)) return false;
      if (frustrationFilter.value === 'normal' && score >= 0.40) return false;
    }

    // Search Query (Client-side fallback)
    if (searchQuery.value) {
      const q = searchQuery.value.toLowerCase();
      const matchCaller = (item.caller || '').toLowerCase().includes(q);
      const matchAgent = (item.agent_name || '').toLowerCase().includes(q);
      const matchTranscript = (item.transcript || []).some(m => (m.content || '').toLowerCase().includes(q));
      const matchRisk = (item.risk_reason || '').toLowerCase().includes(q);
      if (!matchCaller && !matchAgent && !matchTranscript && !matchRisk) return false;
    }

    return true;
  });
});

// Copy transcript text to clipboard
const copyTranscript = async (interaction) => {
  const lines = (interaction.transcript || []).map(m => `[${m.role === 'assistant' ? 'Alfie' : 'Caller'}]: ${m.content}`).join('\n');
  const text = `Call: ${interaction.caller}\nDate: ${interaction.date}\nDuration: ${interaction.duration}\nScore: ${interaction.score}/10\nStatus: ${interaction.conversion_status || 'N/A'}\n\nTranscript:\n${lines}`;
  try {
    await navigator.clipboard.writeText(text);
    alert("Transcript copied to clipboard!");
  } catch (e) {
    console.error("Failed to copy:", e);
  }
};

// Export to CSV
const exportCSV = () => {
  if (interactions.value.length === 0) {
    alert("No interactions to export.");
    return;
  }

  const headers = ["Interaction ID", "Caller", "Date", "Duration", "Agent", "QA Score", "Conversion Status", "Risk Flag", "Risk Reason", "Full Transcript"];
  const csvRows = [headers.join(',')];

  interactions.value.forEach(item => {
    const transcriptText = (item.transcript || []).map(m => `${m.role}: ${m.content}`).join(' | ');
    const row = [
      `"${item.id || ''}"`,
      `"${item.caller || ''}"`,
      `"${item.date || ''}"`,
      `"${item.duration || ''}"`,
      `"${item.agent_name || ''}"`,
      `"${item.score || ''}"`,
      `"${item.conversion_status || ''}"`,
      `"${item.risk_flag ? 'YES' : 'NO'}"`,
      `"${item.risk_reason || ''}"`,
      `"${transcriptText.replace(/"/g, '""')}"`
    ];
    csvRows.push(row.join(','));
  });

  const blob = new Blob([csvRows.join('\n')], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.setAttribute('href', url);
  link.setAttribute('download', `alfie_call_interactions_${new Date().toISOString().split('T')[0]}.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

onMounted(() => {
  fetchInteractions();
  animInterval = setInterval(() => {
    if (isPlaying.value) {
      animTick.value += 0.2;
    }
  }, 100);
});

onUnmounted(() => {
  if (animInterval) clearInterval(animInterval);
});
</script>
