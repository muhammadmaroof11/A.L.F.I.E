<template>
  <div class="h-full flex flex-col">
    <div class="flex gap-6 overflow-x-auto pb-4 flex-1">
      
      <!-- Column -->
      <div v-for="column in columns" :key="column.id" class="flex-shrink-0 w-80 flex flex-col">
        <div class="flex items-center justify-between mb-4 px-1">
          <h3 class="font-semibold text-white flex items-center gap-2">
            <div class="w-2 h-2 rounded-full" :class="column.color"></div>
            {{ column.title }}
          </h3>
          <span class="text-xs font-medium bg-white/10 text-clientMuted px-2 py-0.5 rounded-full">{{ column.leads.length }}</span>
        </div>
        
        <div class="glass-panel p-2 flex-1 flex flex-col gap-2 bg-clientSurface/20 overflow-y-auto custom-scrollbar">
          <!-- Card -->
          <div v-for="lead in column.leads" :key="lead.id" class="bg-clientSurface border border-white/5 p-4 rounded-xl shadow-lg cursor-grab hover:border-white/20 transition-colors">
            <div class="flex justify-between items-start mb-2">
              <h4 class="font-medium text-white">{{ lead.name }}</h4>
              <span class="text-xs font-medium px-2 py-1 rounded-md bg-white/5 text-clientMuted">{{ lead.score }}/10</span>
            </div>
            <p class="text-xs text-clientMuted mb-4 line-clamp-2">{{ lead.summary }}</p>
            <div class="flex items-center gap-2 text-xs text-clientMuted">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg>
              {{ lead.phone }}
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const columns = ref([
  {
    id: 'new',
    title: 'New Leads',
    color: 'bg-blue-400',
    leads: [
      { id: 1, name: 'Sarah Jenkins', score: 8, summary: 'Interested in a 3-bedroom property in downtown. Pre-approved for $450k.', phone: '+1 555-0123' },
      { id: 2, name: 'Michael Chen', score: 6, summary: 'Looking to sell his current property before buying.', phone: '+1 555-0198' }
    ]
  },
  {
    id: 'contacted',
    title: 'Contacted',
    color: 'bg-amber-400',
    leads: [
      { id: 3, name: 'Emma Watson', score: 9, summary: 'Scheduled a viewing for tomorrow at 2PM.', phone: '+1 555-0234' }
    ]
  },
  {
    id: 'viewing',
    title: 'Viewing Scheduled',
    color: 'bg-purple-400',
    leads: []
  },
  {
    id: 'closed',
    title: 'Closed',
    color: 'bg-emerald-400',
    leads: [
      { id: 4, name: 'David Smith', score: 10, summary: 'Offer accepted on 123 Main St.', phone: '+1 555-0999' }
    ]
  }
]);
</script>
