<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
      <div class="flex flex-col space-y-1">
        <h2 class="text-2xl font-semibold tracking-tight">Credits & Transactions</h2>
        <p class="text-sm text-muted-foreground">Manage tenant credit top-ups and audit transaction ledgers.</p>
      </div>
      <div class="flex items-center gap-2">
        <button @click="showTopupModal = true" class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 bg-blue-600 text-white shadow hover:bg-blue-600/90 h-9 px-4 py-2 shrink-0">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="mr-2 h-4 w-4"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
          Direct Credit Top-Up
        </button>
      </div>
    </div>

    <!-- Credit Transaction Audit Ledger -->
    <div class="rounded-xl border bg-card text-card-foreground shadow-sm">
      <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center p-6 border-b gap-4">
        <div>
          <h3 class="font-semibold leading-none tracking-tight">Credit Transaction Audit Ledger</h3>
          <p class="text-sm text-muted-foreground mt-1">Historical record of manual top-ups, voucher redemptions, and call usage.</p>
        </div>
        <button @click="fetchTransactions" class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-xs font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 border border-input bg-background shadow-sm hover:bg-accent hover:text-accent-foreground h-8 px-3 py-1">
          <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="mr-2"><path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/></svg>
          Refresh Ledger
        </button>
      </div>

      <div class="w-full overflow-auto">
        <table class="w-full caption-bottom text-sm">
          <thead class="[&_tr]:border-b bg-muted/50">
            <tr class="border-b transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted">
              <th class="h-10 px-4 text-left align-middle font-medium text-muted-foreground w-[20%]">Date & Time</th>
              <th class="h-10 px-4 text-left align-middle font-medium text-muted-foreground w-[20%]">Tenant ID</th>
              <th class="h-10 px-4 text-left align-middle font-medium text-muted-foreground w-[20%]">Amount ($)</th>
              <th class="h-10 px-4 text-left align-middle font-medium text-muted-foreground w-[40%]">Description / Type</th>
            </tr>
          </thead>
          <tbody class="[&_tr:last-child]:border-0">
            <tr v-if="transactions.length === 0">
              <td colspan="4" class="p-8 text-center text-muted-foreground">No credit transactions recorded yet.</td>
            </tr>
            <tr v-for="t in transactions" :key="t.id" class="border-b transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted">
              <td class="p-4 align-middle">
                <span class="text-xs text-muted-foreground">{{ t.created_at ? new Date(t.created_at).toLocaleString() : 'Just now' }}</span>
              </td>
              <td class="p-4 align-middle">
                <span class="font-mono text-xs font-medium text-foreground">{{ t.tenant_id }}</span>
              </td>
              <td class="p-4 align-middle">
                <span :class="['font-mono text-sm font-semibold tracking-tight', t.amount_usd >= 0 ? 'text-emerald-500' : 'text-rose-500']">
                  {{ t.amount_usd >= 0 ? '+' : '' }}${{ t.amount_usd.toFixed(2) }}
                </span>
              </td>
              <td class="p-4 align-middle">
                <div class="flex items-center gap-2">
                  <span class="inline-flex items-center rounded border border-transparent bg-secondary px-2 py-0.5 text-[10px] font-semibold text-secondary-foreground uppercase">
                    {{ t.transaction_type }}
                  </span>
                  <span class="text-xs text-muted-foreground truncate" :title="t.description">{{ t.description }}</span>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- DIRECT TOPUP MODAL -->
    <div v-if="showTopupModal" class="fixed inset-0 z-50 bg-background/80 backdrop-blur-sm flex items-center justify-center">
      <div class="fixed left-[50%] top-[50%] z-50 grid w-full max-w-md translate-x-[-50%] translate-y-[-50%] gap-4 border bg-background p-6 shadow-lg sm:rounded-lg">
        <div class="flex flex-col space-y-1.5 sm:text-left">
          <h2 class="text-lg font-semibold leading-none tracking-tight">Direct Tenant Credit Top-Up</h2>
          <p class="text-sm text-muted-foreground">Manually add credits to a specific tenant workspace.</p>
        </div>

        <form @submit.prevent="topupCredits" class="space-y-4 py-4">
          <div class="space-y-2">
            <label class="text-sm font-medium leading-none">Target Tenant ID</label>
            <input v-model="topupForm.tenant_id" type="text" class="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring font-mono" placeholder="e.g. alfie_realty_pk" required />
          </div>

          <div class="space-y-2">
            <label class="text-sm font-medium leading-none">Credit Amount ($ USD)</label>
            <input v-model.number="topupForm.amount_usd" type="number" step="5" class="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring font-mono" placeholder="50" required />
          </div>

          <div class="space-y-2">
            <label class="text-sm font-medium leading-none">Audit Note / Description</label>
            <input v-model="topupForm.description" type="text" class="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring" placeholder="e.g. Promotional bonus credits" required />
          </div>

          <div class="flex items-center justify-end gap-2 pt-4 border-t border-border mt-6">
            <button type="button" class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 border border-input bg-background shadow-sm hover:bg-accent hover:text-accent-foreground h-9 px-4 py-2" @click="showTopupModal = false">Cancel</button>
            <button type="submit" class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 bg-blue-600 text-white shadow hover:bg-blue-600/90 h-9 px-4 py-2" :disabled="savingTopup">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="mr-2 h-4 w-4 animate-spin" v-if="savingTopup"><path d="M21 12a9 9 0 1 1-6.219-8.56"/></svg>
              {{ savingTopup ? 'Processing...' : 'Apply Credit Top-Up' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '../services/api';

const transactions = ref([]);
const showTopupModal = ref(false);
const savingTopup = ref(false);

const topupForm = ref({
  tenant_id: '',
  amount_usd: 50,
  description: 'Manual Credit Topup'
});

const fetchTransactions = async () => {
  try {
    const res = await api.get('/api/super/credits/transactions');
    transactions.value = res.data || [];
  } catch (err) {
    console.error('Failed to fetch transactions:', err);
  }
};

const topupCredits = async () => {
  savingTopup.value = true;
  try {
    await api.post(`/api/super/tenants/${topupForm.value.tenant_id}/topup`, {
      amount_usd: topupForm.value.amount_usd,
      description: topupForm.value.description
    });
    showTopupModal.value = false;
    topupForm.value = { tenant_id: '', amount_usd: 50, description: 'Manual Credit Topup' };
    fetchTransactions();
    alert('Credit topup applied successfully!');
  } catch (err) {
    alert(err.response?.data?.detail || 'Failed to apply credit topup.');
  } finally {
    savingTopup.value = false;
  }
};

onMounted(() => {
  fetchTransactions();
});
</script>
