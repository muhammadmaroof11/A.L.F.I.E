<template>
  <div class="glass-panel p-6 rounded-xl relative overflow-hidden group border border-border/50 space-y-5">
    <div>
      <h3 class="text-xs font-semibold uppercase tracking-wider text-muted-foreground flex items-center gap-2">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="text-primary">
          <polyline points="16 18 22 12 16 6"></polyline>
          <polyline points="8 6 2 12 8 18"></polyline>
        </svg>
        CRM & Webhook Integrations
      </h3>
      <p class="text-xs text-muted-foreground mt-0.5">
        Stream live leads, call recordings, and calendar bookings to your external tech stack.
      </p>
    </div>

    <div class="space-y-4">
      <!-- Webhook Alert URL -->
      <div class="space-y-1.5">
        <label class="text-xs font-medium text-foreground">Outbound Lead Webhook URL (POST)</label>
        <input
          v-model="integrations.webhook_url"
          type="url"
          placeholder="https://your-crm.com/api/webhooks/alfie"
          class="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-xs font-mono focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-primary"
        />
      </div>

      <!-- Webhook Secret -->
      <div class="space-y-1.5">
        <label class="text-xs font-medium text-foreground">HMAC Webhook Signing Secret</label>
        <input
          v-model="integrations.webhook_secret"
          type="password"
          placeholder="whsec_..."
          class="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-xs font-mono focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-primary"
        />
      </div>

      <!-- Cal.com API Keys -->
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
        <div class="space-y-1.5">
          <label class="text-xs font-medium text-foreground">Cal.com API Key</label>
          <input
            v-model="integrations.cal_com_api_key"
            type="password"
            placeholder="cal_live_..."
            class="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-xs font-mono focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-primary"
          />
        </div>
        <div class="space-y-1.5">
          <label class="text-xs font-medium text-foreground">Cal.com Event Type ID</label>
          <input
            v-model="integrations.cal_com_event_type_id"
            type="text"
            placeholder="e.g. 148920"
            class="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-xs font-mono focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-primary"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  integrations: {
    type: Object,
    required: true,
  },
});
</script>
