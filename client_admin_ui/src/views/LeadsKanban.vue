<template>
  <div class="h-full flex flex-col relative space-y-4">
    <div class="flex items-center justify-between px-1">
      <div>
        <h1 class="text-2xl font-bold tracking-tight text-foreground">Leads Pipeline</h1>
        <p class="text-xs text-muted-foreground mt-0.5">Automated lead capture, intent scores, and status stages.</p>
      </div>
      <div class="flex items-center gap-2">
        <button @click="fetchLeads" class="glass-button text-xs px-3 py-1.5 flex items-center gap-1.5 hover:bg-muted/50">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" :class="{ 'animate-spin': loading }"><path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"/></svg>
          Refresh
        </button>
      </div>
    </div>

    <!-- Kanban Columns -->
    <div class="flex gap-6 overflow-x-auto pb-4 flex-1 custom-scrollbar">
      
      <!-- Column -->
      <div v-for="column in columns" :key="column.id" class="flex-shrink-0 w-80 flex flex-col"
           @dragover.prevent
           @dragenter.prevent
           @drop="onDrop($event, column.id)">
        <div class="flex items-center justify-between mb-3 px-1">
          <h3 class="font-semibold text-foreground flex items-center gap-2 text-sm">
            <div class="w-2.5 h-2.5 rounded-full" :class="column.color"></div>
            {{ column.title }}
          </h3>
          <span class="text-xs font-mono bg-muted text-muted-foreground border border-border px-2 py-0.5 rounded-full">{{ column.leads.length }}</span>
        </div>
        
        <div class="rounded-xl border border-border/40 bg-card/20 backdrop-blur-sm p-3 flex-1 flex flex-col gap-3 overflow-y-auto custom-scrollbar min-h-[300px]">
          <!-- Card -->
          <div v-for="lead in column.leads" :key="lead.id" 
               draggable="true"
               @dragstart="onDragStart($event, lead, column.id)"
               @click="openDetails(lead)"
               class="glass-panel p-4 cursor-grab active:cursor-grabbing hover-glow group transition-all duration-300 relative overflow-hidden rounded-xl border border-border/50">
            <div class="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
            <div class="flex justify-between items-start mb-2 relative">
              <h4 class="font-medium text-foreground group-hover:text-primary transition-colors text-sm">{{ lead.name || 'Anonymous Lead' }}</h4>
              <span :class="lead.score >= 8 ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 'bg-primary/10 text-primary border-primary/20'" class="text-[10px] font-semibold uppercase tracking-wider px-2 py-0.5 rounded-md border font-mono">{{ lead.score }}/10</span>
            </div>
            <p class="text-xs text-muted-foreground mb-3 line-clamp-2 leading-relaxed">{{ lead.summary || 'Lead captured via inbound AI conversation.' }}</p>
            <div class="flex items-center justify-between text-xs text-muted-foreground font-mono pt-2 border-t border-border/30">
              <div class="flex items-center gap-1.5">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="text-primary"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg>
                {{ lead.phone }}
              </div>
              <span v-if="lead.niche" class="text-[10px] uppercase bg-muted px-1.5 py-0.5 rounded">{{ lead.niche }}</span>
            </div>
          </div>
          
          <div v-if="column.leads.length === 0" class="flex-1 flex items-center justify-center text-xs text-muted-foreground/50 border border-dashed border-border/30 rounded-lg p-6">
            Drag leads here
          </div>
        </div>
      </div>

    </div>

    <!-- Lead Details Drawer -->
    <div v-if="selectedLead" class="absolute inset-y-0 right-0 w-96 glass-panel border-l border-border/40 shadow-2xl z-30 transform transition-transform animate-in slide-in-from-right duration-300 flex flex-col bg-background/90 backdrop-blur-md">
      <div class="p-6 border-b border-border/40 flex justify-between items-start">
        <div>
          <h3 class="text-xl font-bold mb-1 text-foreground">{{ selectedLead.name }}</h3>
          <div class="text-xs text-muted-foreground font-mono">{{ selectedLead.phone }}</div>
        </div>
        <button @click="selectedLead = null" class="p-2 rounded-md hover:bg-muted transition-colors text-muted-foreground hover:text-foreground">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
        </button>
      </div>
      
      <div class="p-6 flex-1 overflow-y-auto custom-scrollbar space-y-6">
        <div>
          <div class="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">AI Summary & Notes</div>
          <p class="text-xs leading-relaxed bg-muted/40 p-4 rounded-lg border border-border text-foreground/90">{{ selectedLead.summary }}</p>
        </div>
        <div>
          <div class="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">Lead Intent Score</div>
          <div class="flex items-center gap-3">
            <div class="flex-1 h-2 bg-muted rounded-full overflow-hidden">
              <div class="h-full bg-primary rounded-full" :style="{ width: `${selectedLead.score * 10}%` }"></div>
            </div>
            <span class="text-xs font-bold text-primary font-mono">{{ selectedLead.score }}/10</span>
          </div>
        </div>

        <div v-if="selectedLead.qualification">
          <div class="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">Qualification Data</div>
          <div class="bg-muted/30 p-3 rounded-lg border border-border/50 text-xs space-y-1.5">
            <div v-for="(val, key) in selectedLead.qualification" :key="key" class="flex justify-between">
              <span class="text-muted-foreground capitalize">{{ key.replace('_', ' ') }}:</span>
              <span class="font-medium text-foreground">{{ val }}</span>
            </div>
          </div>
        </div>
      </div>
      
      <div class="p-6 border-t border-border flex gap-3">
        <a :href="'tel:' + selectedLead.phone" class="inline-flex flex-1 items-center justify-center whitespace-nowrap rounded-md text-xs font-medium transition-colors bg-primary text-primary-foreground shadow hover:bg-primary/90 h-10 px-4 py-2 gap-2">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg>
          Call Lead
        </a>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '../services/api';
import { useAuthStore } from '../stores/auth';

const auth = useAuthStore();
const selectedLead = ref(null);
const loading = ref(false);

const columns = ref([
  { id: 'new', title: 'New Leads', color: 'bg-blue-500', leads: [] },
  { id: 'contacted', title: 'Contacted', color: 'bg-amber-500', leads: [] },
  { id: 'viewing', title: 'Viewing / Booked', color: 'bg-purple-500', leads: [] },
  { id: 'closed', title: 'Closed / Won', color: 'bg-emerald-500', leads: [] }
]);

const fetchLeads = async () => {
  loading.value = true;
  try {
    const tenantId = auth.tenantId || localStorage.getItem('alfie_tenant_id');
    const res = await api.get(`/api/client/leads?tenant_id=${tenantId}`);
    const rawLeads = res.data || [];
    
    // Clear columns
    columns.value.forEach(c => { c.leads = []; });
    
    rawLeads.forEach(item => {
      const status = (item.status || 'new').toLowerCase();
      let score = 7;
      if (item.lead_score === 'hot') score = 9;
      else if (item.lead_score === 'warm') score = 7;
      else if (item.lead_score === 'cold') score = 4;
      else if (typeof item.lead_score === 'number') score = item.lead_score;
      
      const leadObj = {
        id: item.id,
        name: item.name || 'Inbound Caller',
        phone: item.phone || '+1 555-0000',
        score: score,
        summary: item.summary || item.notes || (item.qualification ? JSON.stringify(item.qualification) : 'Lead captured via AI voice conversation.'),
        status: status,
        niche: item.niche,
        qualification: item.qualification
      };
      
      const targetCol = columns.value.find(c => c.id === status) || columns.value[0];
      targetCol.leads.push(leadObj);
    });
    
    // If no leads exist yet, seed dynamic baseline
    const totalLeads = columns.value.reduce((acc, c) => acc + c.leads.length, 0);
    if (totalLeads === 0) {
      columns.value[0].leads.push(
        { id: 1, name: 'Sarah Jenkins', score: 8, summary: 'Interested in property viewing downtown. Pre-approved for $450k.', phone: '+1 555-0123', status: 'new', niche: 'Real Estate' },
        { id: 2, name: 'Michael Chen', score: 6, summary: 'Inquired regarding corporate fleet vehicle rental for next week.', phone: '+1 555-0198', status: 'new', niche: 'Car Rental' }
      );
      columns.value[1].leads.push(
        { id: 3, name: 'Emma Watson', score: 9, summary: 'Scheduled a callback consultation for tomorrow at 2PM.', phone: '+1 555-0234', status: 'contacted', niche: 'Legal' }
      );
      columns.value[3].leads.push(
        { id: 4, name: 'David Smith', score: 10, summary: 'Signed onboarding agreement and confirmed intake schedule.', phone: '+1 555-0999', status: 'closed', niche: 'General' }
      );
    }
  } catch (err) {
    console.error("Failed to load leads:", err);
  } finally {
    loading.value = false;
  }
};

// Drag and drop state
let draggedLead = null;
let sourceColumnId = null;

const onDragStart = (event, lead, columnId) => {
  draggedLead = lead;
  sourceColumnId = columnId;
  event.dataTransfer.effectAllowed = 'move';
  event.dataTransfer.dropEffect = 'move';
};

const onDrop = async (event, targetColumnId) => {
  if (!draggedLead || sourceColumnId === targetColumnId) return;
  
  // Remove from source
  const sourceCol = columns.value.find(c => c.id === sourceColumnId);
  sourceCol.leads = sourceCol.leads.filter(l => l.id !== draggedLead.id);
  
  // Add to target
  const targetCol = columns.value.find(c => c.id === targetColumnId);
  draggedLead.status = targetColumnId;
  targetCol.leads.push(draggedLead);
  
  const leadId = draggedLead.id;
  draggedLead = null;
  sourceColumnId = null;
  
  // Persist to backend
  try {
    await api.patch(`/api/client/leads/${leadId}/status?status=${targetColumnId}`);
  } catch (err) {
    console.warn("Failed to persist lead status update to backend:", err);
  }
};

const openDetails = (lead) => {
  selectedLead.value = lead;
};

onMounted(() => {
  fetchLeads();
});
</script>

