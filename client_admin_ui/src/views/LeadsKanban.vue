<template>
  <div class="h-full flex flex-col relative space-y-4">
    <!-- Header with Actions -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 px-1">
      <div>
        <h1 class="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2.5">
          <span>Leads Pipeline</span>
          <span class="text-xs font-mono font-normal bg-primary/10 text-primary border border-primary/20 px-2.5 py-0.5 rounded-full">
            {{ totalLeadsCount }} Active Leads
          </span>
        </h1>
        <p class="text-xs text-muted-foreground mt-0.5">Automated lead qualification, conversational intent scores, and status stages.</p>
      </div>

      <div class="flex flex-wrap items-center gap-2">
        <!-- Search -->
        <div class="relative">
          <svg class="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="Search leads, phone, niche..." 
            class="h-8 pl-8 pr-3 rounded-lg border border-border bg-background/50 text-xs w-48 sm:w-60 focus:outline-none focus:ring-1 focus:ring-primary placeholder:text-muted-foreground/60"
          />
        </div>

        <!-- Export CSV Button -->
        <button 
          @click="exportCSV" 
          title="Export all leads to CSV"
          class="glass-button text-xs px-3 py-1.5 flex items-center gap-1.5 hover:bg-muted/50 border border-border/50 text-foreground transition-all"
        >
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
          Export CSV
        </button>

        <!-- Refresh Button -->
        <button 
          @click="fetchLeads" 
          class="glass-button text-xs px-3 py-1.5 flex items-center gap-1.5 hover:bg-muted/50 border border-border/50"
        >
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" :class="{ 'animate-spin': loading }"><path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"/></svg>
          Refresh
        </button>
      </div>
    </div>

    <!-- Kanban Columns -->
    <div class="flex gap-5 overflow-x-auto pb-4 flex-1 custom-scrollbar">
      <!-- Column -->
      <div 
        v-for="column in filteredColumns" 
        :key="column.id" 
        class="flex-shrink-0 w-80 flex flex-col"
        @dragover.prevent
        @dragenter.prevent
        @drop="onDrop($event, column.id)"
      >
        <div class="flex items-center justify-between mb-3 px-1">
          <h3 class="font-semibold text-foreground flex items-center gap-2 text-sm">
            <div class="w-2.5 h-2.5 rounded-full" :class="column.color"></div>
            {{ column.title }}
          </h3>
          <span class="text-xs font-mono bg-muted text-muted-foreground border border-border px-2 py-0.5 rounded-full">
            {{ column.leads.length }}
          </span>
        </div>
        
        <div class="rounded-xl border border-border/40 bg-card/20 backdrop-blur-sm p-3 flex-1 flex flex-col gap-3 overflow-y-auto custom-scrollbar min-h-[350px]">
          <!-- Card -->
          <div 
            v-for="lead in column.leads" 
            :key="lead.id" 
            draggable="true"
            @dragstart="onDragStart($event, lead, column.id)"
            @click="openDetails(lead)"
            class="glass-panel p-4 cursor-grab active:cursor-grabbing hover-glow group transition-all duration-300 relative overflow-hidden rounded-xl border border-border/50 hover:border-primary/40 shadow-sm"
          >
            <div class="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
            
            <div class="flex justify-between items-start mb-2 relative">
              <div class="flex-1 pr-2">
                <h4 class="font-medium text-foreground group-hover:text-primary transition-colors text-sm truncate">
                  {{ lead.name || 'Anonymous Caller' }}
                </h4>
                <div class="flex items-center gap-1.5 text-[11px] text-muted-foreground font-mono mt-0.5">
                  <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="text-primary/70"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg>
                  <span>{{ lead.phone }}</span>
                </div>
              </div>
              <span 
                :class="lead.score >= 8 ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : lead.score >= 6 ? 'bg-primary/10 text-primary border-primary/20' : 'bg-muted text-muted-foreground border-border'" 
                class="text-[10px] font-semibold uppercase tracking-wider px-2 py-0.5 rounded-md border font-mono"
              >
                {{ lead.score }}/10
              </span>
            </div>

            <p class="text-xs text-muted-foreground mb-3 line-clamp-2 leading-relaxed">
              {{ lead.summary || 'Lead captured via inbound AI conversation.' }}
            </p>

            <!-- Qualification Highlights -->
            <div v-if="lead.qualification && Object.keys(lead.qualification).length > 0" class="flex flex-wrap gap-1 mb-2.5">
              <span 
                v-for="(val, key) in getTopQualifications(lead.qualification)" 
                :key="key"
                class="text-[9px] bg-background/60 text-muted-foreground border border-border/50 px-1.5 py-0.5 rounded truncate max-w-[200px]"
                :title="`${key}: ${val}`"
              >
                <strong class="font-medium text-foreground/80">{{ formatKey(key) }}:</strong> {{ val }}
              </span>
            </div>

            <!-- Card Footer -->
            <div class="flex items-center justify-between text-xs text-muted-foreground font-mono pt-2 border-t border-border/30">
              <span v-if="lead.niche" class="text-[10px] uppercase font-semibold tracking-wider bg-primary/10 text-primary px-1.5 py-0.5 rounded border border-primary/20">
                {{ lead.niche }}
              </span>
              <span v-else class="text-[10px] uppercase text-muted-foreground/60">Standard</span>

              <span v-if="lead.created_at" class="text-[10px] text-muted-foreground/60">
                {{ formatDate(lead.created_at) }}
              </span>
            </div>
          </div>
          
          <div v-if="column.leads.length === 0" class="flex-1 flex items-center justify-center text-xs text-muted-foreground/50 border border-dashed border-border/30 rounded-lg p-6">
            No leads in this stage
          </div>
        </div>
      </div>
    </div>

    <!-- Lead Details Drawer -->
    <div 
      v-if="selectedLead" 
      class="fixed inset-y-0 right-0 w-full sm:w-[440px] glass-panel border-l border-border/40 shadow-2xl z-50 transform transition-transform animate-in slide-in-from-right duration-300 flex flex-col bg-background/95 backdrop-blur-xl"
    >
      <div class="p-6 border-b border-border/40 flex justify-between items-start">
        <div class="flex-1 pr-4">
          <div class="flex items-center gap-2 mb-1">
            <h3 class="text-xl font-bold text-foreground truncate">{{ selectedLead.name }}</h3>
            <span v-if="selectedLead.niche" class="text-[10px] uppercase font-semibold bg-primary/10 text-primary border border-primary/20 px-2 py-0.5 rounded">
              {{ selectedLead.niche }}
            </span>
          </div>
          <div class="flex items-center gap-2 text-xs font-mono text-muted-foreground">
            <span>{{ selectedLead.phone }}</span>
            <button 
              @click="copyToClipboard(selectedLead.phone)" 
              class="text-primary hover:underline text-[11px]"
              title="Copy phone"
            >
              {{ copied ? 'Copied!' : 'Copy' }}
            </button>
          </div>
        </div>
        <button @click="selectedLead = null" class="p-2 rounded-md hover:bg-muted transition-colors text-muted-foreground hover:text-foreground">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
        </button>
      </div>
      
      <div class="p-6 flex-1 overflow-y-auto custom-scrollbar space-y-6 text-xs">
        <!-- Status Stage Selector -->
        <div>
          <label class="text-[11px] font-semibold text-muted-foreground uppercase tracking-wider block mb-2">Stage Status</label>
          <select 
            v-model="selectedLead.status" 
            @change="updateLeadStatus(selectedLead, selectedLead.status)"
            class="w-full bg-background/50 border border-border rounded-lg px-3 py-2 text-foreground font-medium text-xs focus:ring-1 focus:ring-primary focus:outline-none"
          >
            <option value="new">New Leads</option>
            <option value="contacted">Contacted</option>
            <option value="viewing">Viewing / Booked</option>
            <option value="closed">Closed / Won</option>
          </select>
        </div>

        <!-- Intent Score -->
        <div>
          <div class="text-[11px] font-semibold text-muted-foreground uppercase tracking-wider mb-2">Lead Intent Score</div>
          <div class="flex items-center gap-3 bg-muted/20 p-3 rounded-lg border border-border/40">
            <div class="flex-1 h-2.5 bg-muted rounded-full overflow-hidden">
              <div 
                class="h-full rounded-full transition-all duration-500" 
                :class="selectedLead.score >= 8 ? 'bg-emerald-500' : selectedLead.score >= 6 ? 'bg-primary' : 'bg-amber-500'" 
                :style="{ width: `${selectedLead.score * 10}%` }"
              ></div>
            </div>
            <span class="text-xs font-bold font-mono" :class="selectedLead.score >= 8 ? 'text-emerald-400' : 'text-primary'">
              {{ selectedLead.score }}/10 ({{ selectedLead.score >= 8 ? 'Hot' : selectedLead.score >= 6 ? 'Warm' : 'Standard' }})
            </span>
          </div>
        </div>

        <!-- AI Summary -->
        <div>
          <div class="text-[11px] font-semibold text-muted-foreground uppercase tracking-wider mb-2">AI Summary & Intake Notes</div>
          <div class="bg-muted/30 p-4 rounded-lg border border-border text-foreground/90 leading-relaxed font-sans">
            {{ selectedLead.summary }}
          </div>
        </div>

        <!-- Structured Qualification Data -->
        <div v-if="selectedLead.qualification && Object.keys(selectedLead.qualification).length > 0">
          <div class="text-[11px] font-semibold text-muted-foreground uppercase tracking-wider mb-2">Qualification Details</div>
          <div class="bg-muted/20 rounded-lg border border-border/50 divide-y divide-border/30 overflow-hidden">
            <div 
              v-for="(val, key) in selectedLead.qualification" 
              :key="key" 
              class="flex items-center justify-between p-2.5 text-xs"
            >
              <span class="text-muted-foreground font-medium capitalize">{{ formatKey(key) }}</span>
              <span class="font-mono text-foreground font-semibold text-right">{{ val }}</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Drawer Footer -->
      <div class="p-4 border-t border-border flex gap-3 bg-card/30">
        <a 
          :href="'tel:' + selectedLead.phone" 
          class="inline-flex flex-1 items-center justify-center whitespace-nowrap rounded-md text-xs font-medium transition-colors bg-primary text-primary-foreground shadow hover:bg-primary/90 h-9 px-4 py-2 gap-2"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg>
          Call Lead Direct
        </a>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import api from '../services/api';
import { useAuthStore } from '../stores/auth';

const auth = useAuthStore();
const selectedLead = ref(null);
const loading = ref(false);
const searchQuery = ref('');
const copied = ref(false);

const columns = ref([
  { id: 'new', title: 'New Leads', color: 'bg-blue-500', leads: [] },
  { id: 'contacted', title: 'Contacted', color: 'bg-amber-500', leads: [] },
  { id: 'viewing', title: 'Viewing / Booked', color: 'bg-purple-500', leads: [] },
  { id: 'closed', title: 'Closed / Won', color: 'bg-emerald-500', leads: [] }
]);

const totalLeadsCount = computed(() => {
  return columns.value.reduce((sum, col) => sum + col.leads.length, 0);
});

// Filter leads across all columns based on search query
const filteredColumns = computed(() => {
  const q = searchQuery.value.trim().toLowerCase();
  if (!q) return columns.value;

  return columns.value.map(col => ({
    ...col,
    leads: col.leads.filter(l => {
      const matchName = (l.name || '').toLowerCase().includes(q);
      const matchPhone = (l.phone || '').toLowerCase().includes(q);
      const matchNiche = (l.niche || '').toLowerCase().includes(q);
      const matchSummary = (l.summary || '').toLowerCase().includes(q);
      const matchQual = l.qualification ? JSON.stringify(l.qualification).toLowerCase().includes(q) : false;
      return matchName || matchPhone || matchNiche || matchSummary || matchQual;
    })
  }));
});

const formatKey = (key) => {
  return String(key).replace(/_/g, ' ');
};

const formatDate = (isoStr) => {
  if (!isoStr) return '';
  try {
    const d = new Date(isoStr);
    return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
  } catch (e) {
    return '';
  }
};

const getTopQualifications = (qualObj) => {
  if (!qualObj || typeof qualObj !== 'object') return {};
  const entries = Object.entries(qualObj).slice(0, 2);
  return Object.fromEntries(entries);
};

const copyToClipboard = async (text) => {
  try {
    await navigator.clipboard.writeText(text);
    copied.value = true;
    setTimeout(() => { copied.value = false; }, 2000);
  } catch (err) {
    console.error("Clipboard copy failed:", err);
  }
};

const fetchLeads = async () => {
  loading.value = true;
  try {
    // JWT token carries tenant_id automatically; optional fallback passed
    const tenantId = auth.tenantId || localStorage.getItem('alfie_tenant_id');
    const url = tenantId ? `/api/client/leads?tenant_id=${tenantId}` : '/api/client/leads';
    const res = await api.get(url);
    const rawLeads = Array.isArray(res.data) ? res.data : (res.data?.items || []);
    
    // Clear columns
    columns.value.forEach(c => { c.leads = []; });
    
    rawLeads.forEach(item => {
      const status = (item.status || 'new').toLowerCase();
      let score = 7;
      if (item.lead_score === 'hot') score = 9;
      else if (item.lead_score === 'warm') score = 7;
      else if (item.lead_score === 'cold') score = 4;
      else if (typeof item.lead_score === 'number') score = item.lead_score;
      
      let qual = item.qualification;
      if (typeof qual === 'string') {
        try { qual = JSON.parse(qual); } catch (e) { qual = {}; }
      }
      
      const leadObj = {
        id: item.id,
        name: item.name || 'Inbound Caller',
        phone: item.phone || '+1 555-0000',
        score: score,
        summary: item.summary || item.notes || (qual && Object.keys(qual).length > 0 ? JSON.stringify(qual) : 'Lead captured via AI voice conversation.'),
        status: status,
        niche: item.niche,
        qualification: qual,
        created_at: item.created_at
      };
      
      const targetCol = columns.value.find(c => c.id === status) || columns.value[0];
      targetCol.leads.push(leadObj);
    });
    
    // If no leads exist in DB yet, provide realistic industry baselines
    const totalLeads = columns.value.reduce((acc, c) => acc + c.leads.length, 0);
    if (totalLeads === 0) {
      columns.value[0].leads.push(
        { 
          id: 'lead-mock-1', 
          name: 'Sarah Jenkins', 
          score: 8, 
          summary: 'Interested in downtown commercial office space. Pre-approved budget: $450k.', 
          phone: '+1 (555) 012-3456', 
          status: 'new', 
          niche: 'Real Estate',
          qualification: { budget: '$450,000', timeline: '30 days', property_type: 'Office Suite' },
          created_at: new Date().toISOString()
        },
        { 
          id: 'lead-mock-2', 
          name: 'Michael Chen', 
          score: 9, 
          summary: 'Rear-end collision on Highway 101. Seeking personal injury intake consultation.', 
          phone: '+1 (555) 019-8877', 
          status: 'new', 
          niche: 'Personal Injury',
          qualification: { incident_date: 'Yesterday', injury_type: 'Whiplash', insurance: 'State Farm' },
          created_at: new Date().toISOString()
        }
      );
      columns.value[1].leads.push(
        { 
          id: 'lead-mock-3', 
          name: 'Elena Rostova', 
          score: 9, 
          summary: 'Executive airport transfer inquiry for 4 passengers with flight tracking.', 
          phone: '+1 (555) 023-4411', 
          status: 'contacted', 
          niche: 'Chauffeur Fleet',
          qualification: { vehicle: 'Cadillac Escalade', pickup_date: 'Friday 6PM', passengers: '4' },
          created_at: new Date().toISOString()
        }
      );
      columns.value[3].leads.push(
        { 
          id: 'lead-mock-4', 
          name: 'David Smith', 
          score: 10, 
          summary: 'Confirmed intake assessment and submitted initial documentation.', 
          phone: '+1 (555) 099-9876', 
          status: 'closed', 
          niche: 'Medical Clinic',
          qualification: { procedure: 'Consultation', insurance_verified: 'Yes' },
          created_at: new Date().toISOString()
        }
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
    await api.patch(`/api/client/leads/${leadId}/status`, { status: targetColumnId });
  } catch (err) {
    console.warn("Failed to persist lead status update to backend:", err);
  }
};

const updateLeadStatus = async (lead, newStatus) => {
  if (!lead) return;
  // Move between columns in memory
  for (const col of columns.value) {
    col.leads = col.leads.filter(l => l.id !== lead.id);
  }
  const targetCol = columns.value.find(c => c.id === newStatus) || columns.value[0];
  targetCol.leads.push(lead);
  
  try {
    await api.patch(`/api/client/leads/${lead.id}/status`, { status: newStatus });
  } catch (err) {
    console.warn("Failed to update status on backend:", err);
  }
};

const openDetails = (lead) => {
  selectedLead.value = lead;
};

// Export to CSV
const exportCSV = () => {
  const allLeads = [];
  columns.value.forEach(col => {
    col.leads.forEach(l => {
      allLeads.push({
        id: l.id,
        name: l.name || '',
        phone: l.phone || '',
        score: l.score || '',
        status: col.title,
        niche: l.niche || '',
        summary: (l.summary || '').replace(/"/g, '""'),
        qualification: l.qualification ? JSON.stringify(l.qualification).replace(/"/g, '""') : ''
      });
    });
  });

  if (allLeads.length === 0) {
    alert("No leads to export.");
    return;
  }

  const headers = ["Lead ID", "Caller Name", "Phone", "Score", "Stage Status", "Vertical Niche", "Summary & Notes", "Qualification Details"];
  const csvRows = [headers.join(',')];

  allLeads.forEach(item => {
    const row = [
      `"${item.id}"`,
      `"${item.name}"`,
      `"${item.phone}"`,
      `"${item.score}"`,
      `"${item.status}"`,
      `"${item.niche}"`,
      `"${item.summary}"`,
      `"${item.qualification}"`
    ];
    csvRows.push(row.join(','));
  });

  const blob = new Blob([csvRows.join('\n')], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.setAttribute('href', url);
  link.setAttribute('download', `alfie_leads_export_${new Date().toISOString().split('T')[0]}.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

onMounted(() => {
  fetchLeads();
});
</script>
