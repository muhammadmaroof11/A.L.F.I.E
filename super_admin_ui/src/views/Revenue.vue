<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
      <div class="flex flex-col space-y-1">
        <h2 class="text-2xl font-semibold tracking-tight">Revenue & Billing</h2>
        <p class="text-xs text-muted-foreground">Overview of financial performance and credit ledger across all tenants.</p>
      </div>
      <div class="flex items-center gap-2">
        <button @click="fetchRevenue" class="glass-button text-xs px-3 py-1.5 flex items-center gap-1.5 hover:bg-muted/50">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" :class="{ 'animate-spin': loading }"><path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"/></svg>
          Refresh
        </button>
        <button @click="exportCSV" class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-xs font-medium transition-colors border border-input bg-background shadow-sm hover:bg-accent hover:text-accent-foreground h-8 px-3 py-1.5 shrink-0">
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="mr-1.5"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" x2="12" y1="15" y2="3"/></svg>
          Export CSV
        </button>
      </div>
    </div>

    <!-- Stats strip -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="rounded-xl border bg-card text-card-foreground shadow-sm p-6 flex flex-col justify-between hover:shadow-md transition-shadow">
        <div class="flex items-center justify-between space-y-0 pb-2">
          <h3 class="tracking-tight text-xs font-medium uppercase text-muted-foreground">Total Revenue (MTD)</h3>
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-emerald-500"><line x1="12" y1="2" x2="12" y2="22"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
        </div>
        <div class="text-2xl font-bold font-mono tracking-tight text-emerald-500">${{ (summary.total_revenue_mtd || 0).toFixed(2) }}</div>
        <p class="text-[11px] text-muted-foreground mt-1">Active subscriptions & usage</p>
      </div>

      <div class="rounded-xl border bg-card text-card-foreground shadow-sm p-6 flex flex-col justify-between hover:shadow-md transition-shadow">
        <div class="flex items-center justify-between space-y-0 pb-2">
          <h3 class="tracking-tight text-xs font-medium uppercase text-muted-foreground">Projected (EOM)</h3>
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-blue-500"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
        </div>
        <div class="text-2xl font-bold font-mono tracking-tight text-blue-500">${{ (summary.projected_eom || 0).toFixed(2) }}</div>
        <p class="text-[11px] text-muted-foreground mt-1">Forecast based on current run rate</p>
      </div>

      <div class="rounded-xl border bg-card text-card-foreground shadow-sm p-6 flex flex-col justify-between hover:shadow-md transition-shadow">
        <div class="flex items-center justify-between space-y-0 pb-2">
          <h3 class="tracking-tight text-xs font-medium uppercase text-muted-foreground">Avg Rev Per Tenant</h3>
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-violet-500"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
        </div>
        <div class="text-2xl font-bold font-mono tracking-tight text-violet-500">${{ (summary.avg_rev_per_tenant || 0).toFixed(2) }}</div>
        <p class="text-[11px] text-muted-foreground mt-1">ARPU across active workspaces</p>
      </div>

      <div class="rounded-xl border bg-card text-card-foreground shadow-sm p-6 flex flex-col justify-between hover:shadow-md transition-shadow">
        <div class="flex items-center justify-between space-y-0 pb-2">
          <h3 class="tracking-tight text-xs font-medium uppercase text-muted-foreground">Pending Invoices</h3>
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-amber-500"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
        </div>
        <div class="text-2xl font-bold font-mono tracking-tight text-amber-500">${{ (summary.pending_invoices_amount || 0).toFixed(2) }}</div>
        <p class="text-[11px] text-muted-foreground mt-1">{{ summary.pending_invoices_count || 0 }} invoices awaiting settlement</p>
      </div>
    </div>

    <!-- Recent Transactions Table -->
    <div class="rounded-xl border bg-card text-card-foreground shadow-sm overflow-hidden">
      <div class="flex flex-col space-y-1.5 p-6 border-b bg-muted/20">
        <h3 class="font-semibold leading-none tracking-tight">Recent Financial Transactions</h3>
        <p class="text-xs text-muted-foreground">Historical records of subscription renewals, voucher redemptions, and manual top-ups.</p>
      </div>
      
      <div class="w-full overflow-auto">
        <table class="w-full caption-bottom text-sm">
          <thead class="[&_tr]:border-b bg-muted/50">
            <tr class="border-b transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted">
              <th class="h-10 px-4 text-left align-middle font-medium text-muted-foreground w-[20%]">Date & Time</th>
              <th class="h-10 px-4 text-left align-middle font-medium text-muted-foreground w-[25%]">Tenant Workspace</th>
              <th class="h-10 px-4 text-left align-middle font-medium text-muted-foreground w-[35%]">Description</th>
              <th class="h-10 px-4 text-left align-middle font-medium text-muted-foreground w-[10%]">Amount</th>
              <th class="h-10 px-4 text-left align-middle font-medium text-muted-foreground w-[10%]">Status</th>
            </tr>
          </thead>
          <tbody class="[&_tr:last-child]:border-0">
            <tr v-if="loading" class="border-b">
              <td colspan="5" class="p-8 text-center text-xs text-muted-foreground">Loading transactions...</td>
            </tr>
            <tr v-else-if="summary.recent_transactions?.length === 0" class="border-b">
              <td colspan="5" class="p-8 text-center text-xs text-muted-foreground">No financial transactions recorded yet.</td>
            </tr>
            <tr v-for="tx in summary.recent_transactions" :key="tx.id" class="border-b transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted">
              <td class="p-4 align-middle">
                <span class="font-mono text-xs text-muted-foreground">{{ tx.date }}</span>
              </td>
              <td class="p-4 align-middle font-medium text-foreground text-xs">
                {{ tx.tenant }}
              </td>
              <td class="p-4 align-middle text-muted-foreground text-xs">
                {{ tx.description }}
              </td>
              <td class="p-4 align-middle">
                <span :class="tx.amount >= 0 ? 'text-emerald-500' : 'text-rose-400'" class="font-mono font-semibold text-xs">
                  {{ tx.amount >= 0 ? '+' : '' }}${{ Math.abs(tx.amount).toFixed(2) }}
                </span>
              </td>
              <td class="p-4 align-middle">
                <span :class="tx.status === 'Paid' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 'bg-amber-500/10 text-amber-400 border-amber-500/20'" class="inline-flex items-center rounded-full border px-2 py-0.5 text-[10px] font-semibold">
                  {{ tx.status }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '../services/api';

const loading = ref(false);
const summary = ref({
  total_revenue_mtd: 0,
  projected_eom: 0,
  avg_rev_per_tenant: 0,
  pending_invoices_count: 0,
  pending_invoices_amount: 0,
  recent_transactions: []
});

const fetchRevenue = async () => {
  loading.value = true;
  try {
    const res = await api.get('/api/super/revenue/summary');
    summary.value = res.data || {};
  } catch (err) {
    console.error("Failed to load revenue summary:", err);
  } finally {
    loading.value = false;
  }
};

const exportCSV = () => {
  if (!summary.value.recent_transactions || summary.value.recent_transactions.length === 0) return;
  const headers = ["Date", "Tenant", "Description", "Amount", "Status"];
  const rows = summary.value.recent_transactions.map(t => [
    `"${t.date}"`,
    `"${t.tenant}"`,
    `"${t.description}"`,
    t.amount,
    `"${t.status}"`
  ]);
  const csvContent = "data:text/csv;charset=utf-8," + [headers.join(','), ...rows.map(e => e.join(','))].join('\n');
  const encodedUri = encodeURI(csvContent);
  const link = document.createElement("a");
  link.setAttribute("href", encodedUri);
  link.setAttribute("download", `alfie_revenue_report_${new Date().toISOString().slice(0, 10)}.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

onMounted(() => {
  fetchRevenue();
});
</script>

