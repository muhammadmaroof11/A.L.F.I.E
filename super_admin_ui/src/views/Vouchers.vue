<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
      <div class="flex flex-col space-y-1">
        <h2 class="text-2xl font-semibold tracking-tight">Promotional Vouchers</h2>
        <p class="text-sm text-muted-foreground">Manage promotional voucher codes redeemable by tenants in their admin portals.</p>
      </div>
      <div class="flex items-center gap-2">
        <button @click="showVoucherModal = true" class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 bg-emerald-600 text-white shadow hover:bg-emerald-600/90 h-9 px-4 py-2 shrink-0">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="mr-2 h-4 w-4"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
          Create Voucher Code
        </button>
      </div>
    </div>

    <!-- Active Vouchers Grid -->
    <div class="rounded-xl border bg-card text-card-foreground shadow-sm">
      <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center p-6 border-b gap-4">
        <div>
          <h3 class="font-semibold leading-none tracking-tight">Active Voucher Codes</h3>
          <p class="text-sm text-muted-foreground mt-1">Codes available for redemption.</p>
        </div>
        <button @click="fetchVouchers" class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-xs font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 border border-input bg-background shadow-sm hover:bg-accent hover:text-accent-foreground h-8 px-3 py-1">
          <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="mr-2"><path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/></svg>
          Refresh
        </button>
      </div>

      <div class="w-full overflow-auto">
        <table class="w-full caption-bottom text-sm">
          <thead class="[&_tr]:border-b bg-muted/50">
            <tr class="border-b transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted">
              <th class="h-10 px-4 text-left align-middle font-medium text-muted-foreground w-[25%]">Voucher Code</th>
              <th class="h-10 px-4 text-left align-middle font-medium text-muted-foreground w-[25%]">Credit Value ($)</th>
              <th class="h-10 px-4 text-left align-middle font-medium text-muted-foreground w-[20%]">Redemptions / Limit</th>
              <th class="h-10 px-4 text-left align-middle font-medium text-muted-foreground w-[15%]">Status</th>
              <th class="h-10 px-4 text-right align-middle font-medium text-muted-foreground w-[15%]">Actions</th>
            </tr>
          </thead>
          <tbody class="[&_tr:last-child]:border-0">
            <tr v-if="vouchers.length === 0">
              <td colspan="5" class="p-8 text-center text-muted-foreground">No active voucher codes generated yet. Click "Create Voucher Code" to issue your first voucher.</td>
            </tr>
            <tr v-for="v in vouchers" :key="v.id" class="border-b transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted">
              <td class="p-4 align-middle">
                <div class="flex items-center gap-2">
                  <span class="text-base">🎟️</span>
                  <span class="font-mono text-sm font-semibold tracking-wider text-blue-500 uppercase">{{ v.code }}</span>
                </div>
              </td>
              <td class="p-4 align-middle">
                <span class="font-mono text-sm font-bold text-emerald-500">+${{ v.credit_amount_usd.toFixed(2) }} USD</span>
              </td>
              <td class="p-4 align-middle">
                <span class="text-xs text-muted-foreground">
                  <strong class="text-foreground font-medium">{{ v.times_redeemed }}</strong> / {{ v.max_redemptions }} used
                </span>
                <div class="w-full bg-secondary h-1.5 rounded-full mt-1.5 overflow-hidden">
                  <div class="bg-blue-500 h-full rounded-full" :style="{ width: `${(v.times_redeemed / v.max_redemptions) * 100}%` }"></div>
                </div>
              </td>
              <td class="p-4 align-middle">
                <span :class="['inline-flex items-center rounded-full border border-transparent px-2.5 py-0.5 text-xs font-semibold uppercase', v.status === 'active' ? 'bg-emerald-500/10 text-emerald-500' : 'bg-muted text-muted-foreground']">
                  {{ v.status }}
                </span>
              </td>
              <td class="p-4 align-middle text-right">
                <button @click="deleteVoucher(v.id)" class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-xs font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 hover:bg-rose-500/10 text-rose-500 h-8 px-3">
                  Deactivate
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- CREATE VOUCHER MODAL -->
    <div v-if="showVoucherModal" class="fixed inset-0 z-50 bg-background/80 backdrop-blur-sm flex items-center justify-center">
      <div class="fixed left-[50%] top-[50%] z-50 grid w-full max-w-md translate-x-[-50%] translate-y-[-50%] gap-4 border bg-background p-6 shadow-lg sm:rounded-lg">
        <div class="flex flex-col space-y-1.5 sm:text-left">
          <h2 class="text-lg font-semibold leading-none tracking-tight">Create Promotional Voucher</h2>
          <p class="text-sm text-muted-foreground">Issue a new voucher code for tenants to redeem.</p>
        </div>

        <form @submit.prevent="createVoucher" class="space-y-4 py-4">
          <div class="space-y-2">
            <label class="text-sm font-medium leading-none">Voucher Code</label>
            <div class="relative">
              <span class="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground">🎟️</span>
              <input v-model="voucherForm.code" type="text" class="flex h-9 w-full rounded-md border border-input bg-transparent pl-9 pr-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring font-mono uppercase" placeholder="e.g. WELCOME100" required />
            </div>
          </div>

          <div class="space-y-2">
            <label class="text-sm font-medium leading-none">Credit Value (USD)</label>
            <div class="relative">
              <span class="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground font-mono">$</span>
              <input v-model.number="voucherForm.credit_amount_usd" type="number" step="1" min="1" class="flex h-9 w-full rounded-md border border-input bg-transparent pl-7 pr-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring font-mono" placeholder="100" required />
            </div>
          </div>

          <div class="space-y-2">
            <label class="text-sm font-medium leading-none">Max Redemptions Limit</label>
            <input v-model.number="voucherForm.max_redemptions" type="number" min="1" class="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring font-mono" placeholder="50" required />
          </div>

          <div class="flex items-center justify-end gap-2 pt-4 border-t border-border mt-6">
            <button type="button" class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 border border-input bg-background shadow-sm hover:bg-accent hover:text-accent-foreground h-9 px-4 py-2" @click="showVoucherModal = false">Cancel</button>
            <button type="submit" class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 bg-emerald-600 text-white shadow hover:bg-emerald-600/90 h-9 px-4 py-2" :disabled="savingVoucher">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="mr-2 h-4 w-4 animate-spin" v-if="savingVoucher"><path d="M21 12a9 9 0 1 1-6.219-8.56"/></svg>
              {{ savingVoucher ? 'Generating...' : 'Issue Voucher' }}
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

const vouchers = ref([]);
const showVoucherModal = ref(false);
const savingVoucher = ref(false);

const voucherForm = ref({
  code: '',
  credit_amount_usd: 50,
  max_redemptions: 100
});

const fetchVouchers = async () => {
  try {
    const res = await api.get('/api/super/vouchers');
    vouchers.value = res.data || [];
  } catch (err) {
    console.error('Failed to fetch vouchers:', err);
  }
};

const createVoucher = async () => {
  savingVoucher.value = true;
  try {
    await api.post('/api/super/vouchers', voucherForm.value);
    showVoucherModal.value = false;
    voucherForm.value = { code: '', credit_amount_usd: 50, max_redemptions: 100 };
    fetchVouchers();
  } catch (err) {
    alert(err.response?.data?.detail || 'Failed to create voucher.');
  } finally {
    savingVoucher.value = false;
  }
};

const deleteVoucher = async (id) => {
  if (!confirm('Are you sure you want to deactivate this voucher?')) return;
  try {
    await api.delete(`/api/super/vouchers/${id}`);
    fetchVouchers();
  } catch (err) {
    alert(err.response?.data?.detail || 'Failed to delete voucher.');
  }
};

onMounted(() => {
  fetchVouchers();
});
</script>
