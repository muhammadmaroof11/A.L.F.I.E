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
             :class="tier === 'payg' ? 'bg-secondary' : tier === 'plus' ? 'bg-blue-500' : 'bg-purple-500'"></div>
        
        <div class="p-6 flex-grow">
          <div class="flex items-center justify-between mb-4">
            <h3 class="font-semibold text-xl text-foreground">Current Plan</h3>
            <span :class="['inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold', 
                 tier === 'payg' ? 'bg-secondary text-secondary-foreground' : 
                 tier === 'plus' ? 'bg-blue-500/10 text-blue-500' : 
                 'bg-purple-500/10 text-purple-500']">
              {{ tier === 'payg' ? 'Pay-As-You-Go' : tier === 'plus' ? 'Plus Plan' : 'Pro Plan' }}
            </span>
          </div>
          
          <div class="space-y-4">
            <div class="flex items-end gap-2">
              <span class="text-4xl font-bold text-foreground">{{ tier === 'payg' ? '$0' : tier === 'plus' ? '$99' : '$299' }}</span>
              <span class="text-muted-foreground mb-1">/ month</span>
            </div>
            
            <p class="text-sm text-muted-foreground">
              {{ tier === 'payg' ? 'You pay only for what you use at $0.15/min.' : 
                 tier === 'plus' ? 'You have 1,000 minutes included every month. Overage at $0.12/min.' : 
                 'You have 4,000 minutes included every month. Overage at $0.09/min.' }}
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
                <span class="font-mono">{{ includedMinutes }} / {{ tier === 'plus' ? '1000' : '4000' }}</span>
              </div>
              <div class="h-2 w-full bg-secondary rounded-full overflow-hidden">
                <div class="h-full bg-blue-500 rounded-full" :style="{ width: ((includedMinutes / (tier === 'plus' ? 1000 : 4000)) * 100) + '%' }"></div>
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
          <button class="text-sm font-medium text-amber-500 hover:underline">Add Credits</button>
        </div>
      </div>
    </div>
    
    <div v-else class="flex items-center justify-center p-12">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '../services/api';

const loading = ref(true);
const tier = ref('payg');
const includedMinutes = ref(0);
const creditBalance = ref(0.0);

const fetchBilling = async () => {
  try {
    const tenantId = localStorage.getItem('tenant_id');
    const res = await api.get(`/api/client/billing/subscription?tenant_id=${tenantId}`);
    tier.value = res.data.subscription_tier;
    includedMinutes.value = res.data.included_minutes_balance;
    creditBalance.value = res.data.credit_balance;
  } catch (err) {
    console.error("Failed to load billing", err);
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchBilling();
});
</script>
