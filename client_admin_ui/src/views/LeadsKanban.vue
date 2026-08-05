<template>
  <div class="h-full flex flex-col relative">
    <div class="flex gap-6 overflow-x-auto pb-4 flex-1 custom-scrollbar">
      
      <!-- Column -->
      <div v-for="column in columns" :key="column.id" class="flex-shrink-0 w-80 flex flex-col"
           @dragover.prevent
           @dragenter.prevent
           @drop="onDrop($event, column.id)">
        <div class="flex items-center justify-between mb-4 px-1">
          <h3 class="font-display font-semibold text-white flex items-center gap-2">
            <div class="w-2.5 h-2.5 rounded-full shadow-[0_0_8px_currentColor]" :class="column.color"></div>
            {{ column.title }}
          </h3>
          <span class="text-xs font-medium bg-surface text-textSecondary border border-border px-2 py-0.5 rounded-full">{{ column.leads.length }}</span>
        </div>
        
        <div class="glass p-3 rounded-xl flex-1 flex flex-col gap-3 bg-surface/30 overflow-y-auto custom-scrollbar border border-border/50">
          <!-- Card -->
          <div v-for="lead in column.leads" :key="lead.id" 
               draggable="true"
               @dragstart="onDragStart($event, lead, column.id)"
               @click="openDetails(lead)"
               class="bg-surface border border-border p-4 rounded-xl shadow-lg cursor-grab active:cursor-grabbing hover:border-accent/50 hover:bg-surfaceHover transition-all hover:-translate-y-0.5 group">
            <div class="flex justify-between items-start mb-2">
              <h4 class="font-medium text-white group-hover:text-accent transition-colors">{{ lead.name }}</h4>
              <span class="text-[10px] font-bold uppercase tracking-wider px-2 py-1 rounded-md bg-accent/10 text-accent border border-accent/20">{{ lead.score }}/10</span>
            </div>
            <p class="text-xs text-textSecondary mb-4 line-clamp-2 leading-relaxed">{{ lead.summary }}</p>
            <div class="flex items-center gap-2 text-xs text-textMuted font-mono">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg>
              {{ lead.phone }}
            </div>
          </div>
        </div>
      </div>

    </div>

    <!-- Lead Details Drawer -->
    <div v-if="selectedLead" class="absolute inset-y-0 right-0 w-96 glass-elevated border-l border-border shadow-2xl z-30 transform transition-transform animate-in slide-in-from-right duration-300 flex flex-col">
      <div class="p-6 border-b border-border flex justify-between items-start bg-background/50">
        <div>
          <h3 class="text-2xl font-display font-bold text-white mb-1">{{ selectedLead.name }}</h3>
          <div class="text-sm text-textSecondary font-mono">{{ selectedLead.phone }}</div>
        </div>
        <button @click="selectedLead = null" class="p-2 rounded-full hover:bg-surface transition-colors text-textMuted hover:text-white">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
        </button>
      </div>
      <div class="p-6 flex-1 overflow-y-auto custom-scrollbar space-y-6">
        <div>
          <div class="text-xs font-bold text-textMuted uppercase tracking-wider mb-2">AI Summary</div>
          <p class="text-sm text-textPrimary leading-relaxed bg-surface p-4 rounded-xl border border-border">{{ selectedLead.summary }}</p>
        </div>
        <div>
          <div class="text-xs font-bold text-textMuted uppercase tracking-wider mb-2">Intent Score</div>
          <div class="flex items-center gap-3">
            <div class="flex-1 h-2 bg-surface rounded-full overflow-hidden">
              <div class="h-full bg-gradient-accent rounded-full" :style="{ width: `${selectedLead.score * 10}%` }"></div>
            </div>
            <span class="text-sm font-bold text-accent">{{ selectedLead.score }}/10</span>
          </div>
        </div>
      </div>
      <div class="p-6 border-t border-border bg-background/50 flex gap-3">
        <button class="flex-1 btn-glow px-4 py-2.5 rounded-lg text-sm font-medium text-white transition-all flex justify-center items-center gap-2">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg>
          Call Lead
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const selectedLead = ref(null);

const columns = ref([
  {
    id: 'new',
    title: 'New Leads',
    color: 'bg-blue-400 text-blue-400',
    leads: [
      { id: 1, name: 'Sarah Jenkins', score: 8, summary: 'Interested in a 3-bedroom property in downtown. Pre-approved for $450k.', phone: '+1 555-0123' },
      { id: 2, name: 'Michael Chen', score: 6, summary: 'Looking to sell his current property before buying.', phone: '+1 555-0198' }
    ]
  },
  {
    id: 'contacted',
    title: 'Contacted',
    color: 'bg-amber text-amber',
    leads: [
      { id: 3, name: 'Emma Watson', score: 9, summary: 'Scheduled a viewing for tomorrow at 2PM.', phone: '+1 555-0234' }
    ]
  },
  {
    id: 'viewing',
    title: 'Viewing Scheduled',
    color: 'bg-purple-400 text-purple-400',
    leads: []
  },
  {
    id: 'closed',
    title: 'Closed',
    color: 'bg-accentSecondary text-accentSecondary',
    leads: [
      { id: 4, name: 'David Smith', score: 10, summary: 'Offer accepted on 123 Main St.', phone: '+1 555-0999' }
    ]
  }
]);

// Drag and drop state
let draggedLead = null;
let sourceColumnId = null;

const onDragStart = (event, lead, columnId) => {
  draggedLead = lead;
  sourceColumnId = columnId;
  event.dataTransfer.effectAllowed = 'move';
  event.dataTransfer.dropEffect = 'move';
};

const onDrop = (event, targetColumnId) => {
  if (!draggedLead || sourceColumnId === targetColumnId) return;
  
  // Remove from source
  const sourceCol = columns.value.find(c => c.id === sourceColumnId);
  sourceCol.leads = sourceCol.leads.filter(l => l.id !== draggedLead.id);
  
  // Add to target
  const targetCol = columns.value.find(c => c.id === targetColumnId);
  targetCol.leads.push(draggedLead);
  
  draggedLead = null;
  sourceColumnId = null;
};

const openDetails = (lead) => {
  selectedLead.value = lead;
};
</script>
