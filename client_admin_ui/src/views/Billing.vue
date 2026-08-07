<template>
  <div class="space-y-6 max-w-5xl mx-auto pb-12 animate-in fade-in slide-in-from-bottom-4 duration-500">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold tracking-tight text-foreground">Billing & Plans</h1>
        <p class="text-muted-foreground mt-2">Manage your subscription, view your usage, and configure payment methods.</p>
      </div>
    </div>

    <!-- Current Plan Overview -->
    <div v-if="!loading" class="grid gap-6 md:grid-cols-2">
      <!-- Plan Details -->
      <div class="rounded-xl glass-panel border border-border/60 shadow-lg overflow-hidden flex flex-col relative">
        <div class="absolute top-0 left-0 w-full h-1" 
             :class="tier === 'payg' ? 'bg-secondary' : tier === 'plus' ? 'bg-blue-500' : tier === 'pro' ? 'bg-purple-500' : 'bg-emerald-500'"></div>
        
        <div class="p-6 flex-grow">
          <div class="flex items-center justify-between mb-4">
            <h3 class="font-semibold text-xl text-foreground">Current Plan</h3>
            <span :class="['inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold', 
                 tier === 'payg' ? 'bg-secondary text-secondary-foreground' : 
                 tier === 'plus' ? 'bg-blue-500/10 text-blue-500' : 
                 tier === 'pro' ? 'bg-purple-500/10 text-purple-500' : 'bg-emerald-500/10 text-emerald-500']">
              {{ tier === 'payg' ? 'Pay-As-You-Go' : tier === 'plus' ? 'Plus Plan' : tier === 'pro' ? 'Pro Plan' : 'Enterprise Custom Plan' }}
            </span>
          </div>
          
          <div class="space-y-4">
            <div class="flex items-end gap-2">
              <span class="text-4xl font-bold text-foreground">{{ tier === 'payg' ? '$0' : tier === 'plus' ? '$99' : tier === 'pro' ? '$299' : `$${customPrice}` }}</span>
              <span class="text-muted-foreground mb-1">/ month</span>
            </div>
            
            <p class="text-sm text-muted-foreground">
              {{ tier === 'payg' ? 'You pay only for what you use at $0.15/min.' : 
                 tier === 'plus' ? 'You have 1,000 minutes included every month. Overage at $0.12/min.' : 
                 tier === 'pro' ? 'You have 4,000 minutes included every month. Overage at $0.09/min.' :
                 `You have ${customMinutes} minutes included every month. Overage at $${customPerMinuteRate.toFixed(2)}/min.` }}
            </p>
          </div>
        </div>
        
        <div class="p-4 bg-muted/30 border-t border-border/40 text-center">
          <button class="text-sm font-medium text-primary hover:underline">Change Plan (Coming Soon)</button>
        </div>
      </div>

      <!-- Usage & Limits -->
      <div class="rounded-xl glass-panel border border-border/60 shadow-lg overflow-hidden flex flex-col">
        <div class="p-6 flex-grow">
          <h3 class="font-semibold text-lg text-foreground mb-6">Monthly Usage</h3>
          
          <div class="space-y-6">
            <!-- Included Minutes (if applicable) -->
            <div v-if="tier !== 'payg'">
              <div class="flex justify-between text-sm mb-2">
                <span class="font-medium text-foreground">Included Minutes Remaining</span>
                <span class="font-mono">{{ includedMinutes }} / {{ tier === 'plus' ? '1000' : tier === 'pro' ? '4000' : customMinutes }}</span>
              </div>
              <div class="h-2 w-full bg-secondary rounded-full overflow-hidden">
                <div class="h-full bg-blue-500 rounded-full" :style="{ width: ((includedMinutes / (tier === 'plus' ? 1000 : tier === 'pro' ? 4000 : customMinutes)) * 100) + '%' }"></div>
              </div>
            </div>

            <!-- PayG / Overage Balance -->
            <div>
              <div class="flex justify-between text-sm mb-2">
                <span class="font-medium text-foreground">Prepaid Credit Balance</span>
                <span class="font-mono text-amber-500 font-bold">${{ creditBalance.toFixed(2) }}</span>
              </div>
              <p class="text-xs text-muted-foreground">Credits are consumed when included minutes are exhausted, or if you are on the Pay-As-You-Go plan.</p>
            </div>
          </div>
        </div>
        <div class="p-4 bg-muted/30 border-t border-border/40 text-center">
          <button @click="showTopUpModal = true" class="text-sm font-medium text-amber-500 hover:underline">Add Credits</button>
        </div>
      </div>
    </div>
    
    <!-- Top Up Modal -->
    <div v-if="showTopUpModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-background/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div class="bg-card w-full max-w-sm rounded-xl shadow-2xl border border-border/60 overflow-hidden flex flex-col">
        <div class="px-6 py-4 border-b border-border/40 flex justify-between items-center bg-muted/20">
          <h3 class="text-lg font-semibold text-foreground">Top Up Credits</h3>
          <button @click="showTopUpModal = false" class="text-muted-foreground hover:text-foreground transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
          </button>
        </div>
        <div class="p-6 space-y-4">
          <div class="space-y-2">
            <label class="text-sm font-semibold text-foreground">Amount (USD)</label>
            <select v-model="topUpAmount" class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-500">
              <option :value="50">$50.00</option>
              <option :value="100">$100.00</option>
              <option :value="250">$250.00</option>
              <option :value="500">$500.00</option>
            </select>
          </div>
        </div>
        <div class="px-6 py-4 border-t border-border/40 bg-muted/20 flex justify-end gap-3">
          <button @click="showTopUpModal = false" class="px-4 py-2 text-sm font-medium text-foreground bg-secondary hover:bg-secondary/80 rounded-md transition-colors">Cancel</button>
          <button @click="checkout" :disabled="processing" class="px-4 py-2 text-sm font-medium text-primary-foreground bg-amber-600 hover:bg-amber-700 rounded-md transition-colors shadow-sm disabled:opacity-50">
            {{ processing ? 'Processing...' : 'Checkout with Stripe' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import api from '../services/api';

const route = useRoute();
const loading = ref(true);
const tier = ref('payg');
const includedMinutes = ref(0);
const creditBalance = ref(0.0);
const customPrice = ref(0.0);
const customMinutes = ref(0);
const customPerMinuteRate = ref(0.15);

const showTopUpModal = ref(false);
const topUpAmount = ref(100);
const processing = ref(false);

const fetchBilling = async () => {
  try {
    const tenantId = localStorage.getItem('tenant_id');
    const res = await api.get(`/api/client/billing/subscription?tenant_id=${tenantId}`);
    tier.value = res.data.subscription_tier;
    includedMinutes.value = res.data.included_minutes_balance;
    creditBalance.value = res.data.credit_balance;
    customPrice.value = res.data.custom_monthly_price;
    customMinutes.value = res.data.custom_included_minutes;
    customPerMinuteRate.value = res.data.custom_per_minute_rate;
  } catch (err) {
    console.error("Failed to load billing", err);
  } finally {
    loading.value = false;
  }
};

const checkout = async () => {
  processing.value = true;
  try {
    const tenantId = localStorage.getItem('tenant_id');
    const res = await api.post(`/api/client/billing/create-checkout-session?tenant_id=${tenantId}`, {
      amount_usd: topUpAmount.value,
      description: `Alfie Credit Top-Up ($${topUpAmount.value})`
    });
    if (res.data.checkout_url) {
      window.location.href = res.data.checkout_url;
    }
  } catch (err) {
    alert(err.response?.data?.detail || "Failed to create checkout session");
  } finally {
    processing.value = false;
  }
};

onMounted(() => {
  fetchBilling();
  
  if (route.query.success) {
    alert("Payment successful! Your credits have been added.");
    // Ideally clear query param, but basic alert is ok for now.
  }
});
</script>
