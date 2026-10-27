<template>
  <div class="glass-panel p-6 rounded-xl relative overflow-hidden group border border-border/50 space-y-4">
    <h3 class="text-xs font-semibold uppercase tracking-wider text-muted-foreground flex items-center gap-2">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="text-primary">
        <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path>
      </svg>
      Specialized Industry Niche
    </h3>

    <div class="space-y-3">
      <div class="space-y-1.5">
        <label class="text-xs font-medium text-foreground">Vertical Persona Preset</label>
        <select
          :value="modelValue"
          @input="$emit('update:modelValue', $event.target.value)"
          class="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-xs focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-primary"
        >
          <option value="general">General Assistant & Customer Support</option>
          <option value="legal">Personal Injury Law & Legal Intake</option>
          <option value="clinic">Medical & Dental Clinic Reception</option>
          <option value="real_estate">Luxury Real Estate & Property Showing</option>
          <option value="car_rental">Luxury Fleet & Chauffeur Dispatch</option>
          <option value="hospitality">Fine Hospitality & Michelin Dining</option>
        </select>
      </div>

      <!-- Contextual Guidance Banner -->
      <div v-if="modelValue === 'legal' || modelValue === 'legal_intake'" class="p-3 bg-amber-500/10 border border-amber-500/20 rounded-lg text-xs text-amber-300 flex items-start gap-2">
        <span>⚖️</span>
        <span>Activates Statute of Limitations checks, liability merit screening, and warm partner transfer tools.</span>
      </div>
      <div v-else-if="modelValue === 'clinic' || modelValue === 'medical'" class="p-3 bg-sky-500/10 border border-sky-500/20 rounded-lg text-xs text-sky-300 flex items-start gap-2">
        <span>🩺</span>
        <span>Activates Insurance network verification (Delta, Aetna, Cigna) and clinical triage protocol.</span>
      </div>
      <div v-else-if="modelValue === 'car_rental' || modelValue === 'luxury_transfer'" class="p-3 bg-primary/10 border border-primary/20 rounded-lg text-xs text-primary flex items-start gap-2">
        <span>🚗</span>
        <span>Activates OSRM distance calculation, luxury fleet rate cards, and Stripe SMS deposits.</span>
      </div>
      <div v-else-if="modelValue === 'real_estate'" class="p-3 bg-emerald-500/10 border border-emerald-500/20 rounded-lg text-xs text-emerald-300 flex items-start gap-2">
        <span>🏡</span>
        <span>Activates MLS property search, buyer pre-qualification, and private showing calendar bookings.</span>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  modelValue: {
    type: String,
    default: 'general',
  },
});

defineEmits(['update:modelValue']);
</script>
