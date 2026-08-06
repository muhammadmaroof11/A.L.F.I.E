<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
      <div class="flex flex-col space-y-1">
        <h2 class="text-2xl font-semibold tracking-tight">Tenant Workspaces</h2>
        <p class="text-sm text-muted-foreground">Manage client accounts, personas, and custom configurations.</p>
      </div>
      <div class="flex items-center gap-3 w-full sm:w-auto">
        <div class="relative w-full sm:w-64">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
          <input type="text" class="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50 pl-9" placeholder="Search tenants..." v-model="searchQuery" />
        </div>
        <button @click="openProvisionModal" class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground shadow hover:bg-primary/90 h-9 px-4 py-2 shrink-0">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="mr-2 h-4 w-4"><path d="M5 12h14"/><path d="M12 5v14"/></svg>
          New Tenant
        </button>
      </div>
    </div>

    <!-- Stats strip -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="rounded-xl glass-panel text-card-foreground p-6 flex flex-col justify-between hover-glow group transition-all duration-300">
        <h3 class="tracking-tight text-sm font-medium text-muted-foreground group-hover:text-primary transition-colors">Total Tenants</h3>
        <div class="text-3xl font-bold font-mono mt-2">{{ totalCount }}</div>
      </div>
      <div class="rounded-xl glass-panel text-card-foreground p-6 flex flex-col justify-between hover-glow group transition-all duration-300">
        <h3 class="tracking-tight text-sm font-medium text-muted-foreground group-hover:text-emerald-500 transition-colors">Active</h3>
        <div class="text-3xl font-bold font-mono mt-2 text-emerald-500 drop-shadow-[0_0_10px_rgba(16,185,129,0.3)]">{{ activeCount }}</div>
      </div>
      <div class="rounded-xl glass-panel text-card-foreground p-6 flex flex-col justify-between hover-glow group transition-all duration-300">
        <h3 class="tracking-tight text-sm font-medium text-muted-foreground group-hover:text-primary transition-colors">Available Niches</h3>
        <div class="text-3xl font-bold font-mono mt-2 text-primary drop-shadow-[0_0_10px_rgba(var(--primary),0.3)]">{{ personas.length }}</div>
      </div>
      <div class="rounded-xl glass-panel text-card-foreground p-6 flex flex-col justify-between hover-glow group transition-all duration-300">
        <h3 class="tracking-tight text-sm font-medium text-muted-foreground group-hover:text-rose-500 transition-colors">Suspended</h3>
        <div class="text-3xl font-bold font-mono mt-2 text-rose-500 drop-shadow-[0_0_10px_rgba(244,63,94,0.3)]">{{ suspendedCount }}</div>
      </div>
    </div>

    <div v-if="loading" class="flex items-center justify-center h-32 text-muted-foreground">
      Loading tenants...
    </div>

    <!-- Data Table -->
    <div v-else class="rounded-xl glass-panel shadow-sm overflow-hidden">
      <div class="w-full overflow-auto">
        <table class="w-full caption-bottom text-sm">
          <thead class="[&_tr]:border-b border-white/5 bg-background/50 backdrop-blur-md">
            <tr class="border-b border-white/5 transition-colors">
              <th class="h-12 px-6 text-left align-middle font-semibold text-muted-foreground w-[30%]">Tenant / Email</th>
              <th class="h-12 px-6 text-left align-middle font-semibold text-muted-foreground">Status</th>
              <th class="h-12 px-6 text-left align-middle font-semibold text-muted-foreground">Niche Persona</th>
              <th class="h-12 px-6 text-left align-middle font-semibold text-muted-foreground">Credit Limit</th>
              <th class="h-12 px-6 text-left align-middle font-semibold text-muted-foreground">Created Date</th>
              <th class="h-12 px-6 text-right align-middle font-semibold text-muted-foreground">Actions</th>
            </tr>
          </thead>
          <tbody class="[&_tr:last-child]:border-0">
            <tr v-if="filteredTenants.length === 0">
              <td colspan="6" class="p-8 text-center text-muted-foreground font-mono">No tenants found matching your criteria.</td>
            </tr>
            <tr v-for="tenant in filteredTenants" :key="tenant.tenant_id" :class="['border-b border-white/5 transition-all duration-300 hover:bg-primary/5 hover:shadow-[inset_0_0_20px_rgba(var(--primary),0.05)] group', tenant.status === 'suspended' ? 'opacity-50 grayscale' : '']">
              <td class="p-4 align-middle">
                <div class="flex items-center gap-3">
                  <div class="w-8 h-8 rounded-md flex items-center justify-center text-xs font-bold text-white shrink-0 shadow-sm" :style="getAvatarGradient(tenant.name)">
                    {{ getInitials(tenant.name) }}
                  </div>
                  <div class="flex flex-col">
                    <span class="font-medium text-foreground">{{ tenant.name }}</span>
                    <span class="text-xs text-muted-foreground">{{ tenant.email || tenant.tenant_id.substring(0, 18) + '...' }}</span>
                  </div>
                </div>
              </td>
              <td class="p-4 align-middle">
                <div :class="['inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2', tenant.status === 'active' ? 'border-transparent bg-emerald-500/10 text-emerald-500 hover:bg-emerald-500/20' : 'border-transparent bg-rose-500/10 text-rose-500 hover:bg-rose-500/20']">
                  {{ tenant.status === 'active' ? 'Active' : 'Suspended' }}
                </div>
              </td>
              <td class="p-4 align-middle">
                <div class="inline-flex items-center rounded-full border border-transparent bg-secondary px-2.5 py-0.5 text-xs font-semibold text-secondary-foreground transition-colors hover:bg-secondary/80">
                  {{ tenant.niche }}
                </div>
              </td>
              <td class="p-4 align-middle">
                <div class="flex flex-col">
                  <span class="font-mono text-amber-500 font-medium">${{ tenant.credit_limit_usd.toFixed(2) }}</span>
                  <span class="text-[10px] text-muted-foreground uppercase tracking-wider">Monthly Limit</span>
                </div>
              </td>
              <td class="p-4 align-middle text-muted-foreground text-xs">
                {{ formatDate(tenant.created_at) }}
              </td>
              <td class="p-4 align-middle text-right">
                <div class="flex items-center justify-end gap-2">
                  <button @click="openCustomizationModal(tenant)" class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-xs font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 border border-input bg-background shadow-sm hover:bg-accent hover:text-accent-foreground h-8 px-3">
                    <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="mr-2"><path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/></svg>
                    Customize
                  </button>
                  <button v-if="tenant.status === 'active'" @click="toggleStatus(tenant)" class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-xs font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 border border-transparent bg-transparent hover:bg-rose-500/10 text-rose-500 h-8 w-8 px-0" title="Suspend Tenant">
                    <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>
                  </button>
                  <button v-else @click="toggleStatus(tenant)" class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-xs font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 border border-transparent bg-transparent hover:bg-emerald-500/10 text-emerald-500 h-8 w-8 px-0" title="Reactivate Tenant">
                    <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Per-Tenant Customization Modal -->
    <div v-if="selectedCustomTenant" class="fixed inset-0 z-50 bg-background/80 backdrop-blur-md flex items-center justify-center">
      <div class="fixed left-[50%] top-[50%] z-50 grid w-full max-w-2xl translate-x-[-50%] translate-y-[-50%] gap-4 glass-panel p-8 shadow-2xl sm:rounded-2xl max-h-[90vh] overflow-y-auto border border-white/10">
        <div class="flex flex-col space-y-1.5 sm:text-left">
          <h2 class="text-lg font-semibold leading-none tracking-tight">Customize Tenant Agent: {{ selectedCustomTenant.name }}</h2>
          <p class="text-sm text-muted-foreground">Override system prompt, conversational LLM, voice ID, and speaking rates for this client.</p>
        </div>
        
        <form @submit.prevent="saveCustomConfig" class="space-y-4 py-4">
          <div class="space-y-2">
            <label class="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">Client Custom System Prompt / Behavior Override</label>
            <textarea class="flex min-h-[80px] w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring font-mono text-xs" v-model="customForm.system_prompt_override" rows="5" placeholder="Add specific client rules (e.g. Always emphasize 5% discount for upfront payments...)"></textarea>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div class="space-y-2">
              <label class="text-sm font-medium leading-none">Conversational LLM Model</label>
              <select class="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring" v-model="customForm.llm_model">
                <option value="meta-llama/llama-3.3-70b-instruct">Llama 3.3 70B Instruct (Human-Like)</option>
                <option value="meta-llama/llama-3.1-8b-instruct">Llama 3.1 8B Instruct (Ultra Fast)</option>
                <option value="anthropic/claude-3.5-sonnet">Claude 3.5 Sonnet (High Empathy)</option>
                <option value="openai/gpt-4o">GPT-4o Omnimodal</option>
                <option value="qwen/qwen-2.5-72b-instruct">Qwen 2.5 72B (Multilingual)</option>
              </select>
            </div>

            <div class="space-y-2">
              <div class="flex items-center justify-between">
                <label class="text-sm font-medium leading-none">Temperature (Warmth)</label>
                <span class="font-mono text-xs text-muted-foreground">{{ customForm.llm_temperature }}</span>
              </div>
              <input type="range" class="w-full accent-primary" min="0" max="1" step="0.05" v-model.number="customForm.llm_temperature">
            </div>
          </div>

          <div class="space-y-2">
            <label class="text-sm font-medium leading-none">Discover & Select Fish Audio Voice</label>
            <select class="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring" @change="e => { if(e.target.value) customForm.tts_voice_id = e.target.value; }">
              <option value="">-- Select from Fish Audio Discover --</option>
              <option v-for="voice in fishAudioVoices" :key="voice.id" :value="voice.id">
                {{ voice.title }} (by {{ voice.author }})
              </option>
            </select>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div class="space-y-2">
              <label class="text-sm font-medium leading-none">Fish Audio Voice ID</label>
              <input type="text" class="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring font-mono text-xs text-amber-500" v-model="customForm.tts_voice_id" placeholder="Voice ID string..." />
            </div>

            <div class="space-y-2">
              <div class="flex items-center justify-between">
                <label class="text-sm font-medium leading-none">Speaking Speed Rate</label>
                <span class="font-mono text-xs text-muted-foreground">{{ customForm.speaking_rate }}x</span>
              </div>
              <input type="range" class="w-full accent-primary" min="0.5" max="2.0" step="0.1" v-model.number="customForm.speaking_rate">
            </div>
          </div>

          <div class="space-y-2">
            <label class="text-sm font-medium leading-none">Greeting Message Override</label>
            <input type="text" class="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring" v-model="customForm.greeting_message" placeholder="e.g., Hello! Thank you for calling Alfie Realty. How can I help you today?" />
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div class="space-y-2">
              <label class="text-sm font-medium leading-none">STT Streaming Language</label>
              <select class="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring" v-model="customForm.stt_language">
                <option value="en-US">English (US)</option>
                <option value="en-UK">English (UK)</option>
                <option value="ur-PK">Urdu (PK)</option>
                <option value="ar">Arabic</option>
              </select>
            </div>

            <div class="space-y-2">
              <label class="text-sm font-medium leading-none">Max Call Duration (Minutes)</label>
              <input type="number" class="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring" v-model.number="customForm.max_call_duration_min" />
            </div>
          </div>

          <div class="flex items-center justify-end gap-2 pt-4 border-t border-border mt-6">
            <button type="button" class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 border border-input bg-background shadow-sm hover:bg-accent hover:text-accent-foreground h-9 px-4 py-2" @click="selectedCustomTenant = null">Cancel</button>
            <button type="submit" class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground shadow hover:bg-primary/90 h-9 px-4 py-2" :disabled="savingCustom">
              {{ savingCustom ? 'Saving Customization...' : 'Save Changes' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Provisioning Form Modal -->
    <div v-if="showProvisionModal" class="fixed inset-0 z-50 bg-background/80 backdrop-blur-md flex items-center justify-center">
      <div class="fixed left-[50%] top-[50%] z-50 grid w-full max-w-lg translate-x-[-50%] translate-y-[-50%] gap-4 glass-panel p-8 shadow-2xl sm:rounded-2xl border border-white/10">
        <div class="flex flex-col space-y-1.5 sm:text-left">
          <h2 class="text-lg font-semibold leading-none tracking-tight">Provision New Tenant</h2>
          <p class="text-sm text-muted-foreground">Assign company workspace, credentials, and niche agent.</p>
        </div>

        <form @submit.prevent="provisionTenant" class="space-y-4 py-4">
          <div class="space-y-2">
            <label class="text-sm font-medium leading-none">Company / Tenant Name</label>
            <input type="text" class="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring" v-model="provisionForm.name" placeholder="e.g., Alfie Realty PK" required />
          </div>

          <div class="space-y-2">
            <label class="text-sm font-medium leading-none">Assign Niche Agent Persona</label>
            <select class="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring" v-model="provisionForm.niche" required>
              <option value="" disabled>Select a niche persona</option>
              <option v-for="persona in personas" :key="persona.id" :value="persona.niche_name">
                {{ formatTitle(persona.niche_name) }} ({{ persona.niche_name }})
              </option>
            </select>
          </div>

          <div class="space-y-2">
            <label class="text-sm font-medium leading-none">Client Admin Email Address</label>
            <input type="email" class="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring" v-model="provisionForm.email" placeholder="admin@clientcompany.com" required />
          </div>

          <div class="space-y-2">
            <label class="text-sm font-medium leading-none">Client Admin Password</label>
            <input type="password" class="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring" v-model="provisionForm.password" placeholder="••••••••••••" required />
          </div>

          <div class="space-y-2">
            <label class="text-sm font-medium leading-none">Credit Limit (USD)</label>
            <input type="number" step="0.01" class="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring font-mono" v-model.number="provisionForm.credit_limit_usd" required />
          </div>

          <div class="flex items-center justify-end gap-2 pt-4 border-t border-border mt-6">
            <button type="button" class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 border border-input bg-background shadow-sm hover:bg-accent hover:text-accent-foreground h-9 px-4 py-2" @click="showProvisionModal = false">Cancel</button>
            <button type="submit" class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground shadow hover:bg-primary/90 h-9 px-4 py-2" :disabled="provisioning">
              {{ provisioning ? 'Provisioning...' : 'Provision Tenant' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Provision Success Modal (Show API Key ONCE) -->
    <div v-if="successResult" class="fixed inset-0 z-[100] bg-background/90 backdrop-blur-xl flex items-center justify-center">
      <div class="fixed left-[50%] top-[50%] z-50 grid w-full max-w-lg translate-x-[-50%] translate-y-[-50%] gap-4 glass-panel p-8 shadow-[0_0_50px_rgba(16,185,129,0.15)] sm:rounded-2xl border border-emerald-500/30">
        <div class="flex flex-col space-y-1.5 sm:text-left">
          <h2 class="text-xl font-semibold leading-none tracking-tight text-emerald-500 flex items-center gap-2">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
            Tenant Provisioned!
          </h2>
          <p class="text-sm text-muted-foreground mt-2">Copy and securely store the raw API key below.</p>
        </div>

        <div class="bg-rose-500/10 border-l-4 border-rose-500 p-4 rounded-md mt-4 text-sm text-rose-500">
          <strong>Security Warning:</strong> This raw API key will <u class="font-semibold">never</u> be shown again. Make sure to copy it now!
        </div>

        <div class="space-y-4 py-4">
          <div class="space-y-2">
            <label class="text-sm font-medium leading-none">Generated Tenant API Key</label>
            <div class="flex gap-2">
              <input type="text" class="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm font-mono text-amber-500" :value="successResult.api_key" readonly />
              <button class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring border border-input bg-background shadow-sm hover:bg-accent hover:text-accent-foreground h-9 px-4 py-2 shrink-0" @click="copyToClipboard(successResult.api_key)">Copy</button>
            </div>
          </div>

          <div class="space-y-2">
            <label class="text-sm font-medium leading-none">SIP Room Metadata (JSON)</label>
            <textarea class="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm shadow-sm font-mono text-xs text-muted-foreground" :value="successResult.sip_room_metadata" readonly rows="3"></textarea>
          </div>
        </div>

        <div class="flex items-center justify-end gap-2 pt-4 mt-2">
          <button class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring bg-primary text-primary-foreground shadow hover:bg-primary/90 h-9 px-4 py-2 w-full" @click="closeSuccessModal">Done & Close</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import api from '../services/api';

const tenants = ref([]);
const personas = ref([]);
const fishAudioVoices = ref([]);
const loading = ref(true);
const searchQuery = ref('');

const showProvisionModal = ref(false);
const provisioning = ref(false);
const successResult = ref(null);

const selectedCustomTenant = ref(null);
const savingCustom = ref(false);

const customForm = ref({
  system_prompt_override: '',
  llm_model: 'meta-llama/llama-3.3-70b-instruct',
  llm_temperature: 0.3,
  speaking_rate: 1.0,
  tts_voice_id: '224a2257dd4943209a683d27a5e41439',
  greeting_message: '',
  stt_language: 'en-US',
  max_call_duration_min: 15
});

const provisionForm = ref({
  name: '',
  niche: 'real_estate',
  email: '',
  password: '',
  credit_limit_usd: 50.00
});

const formatTitle = (str) => {
  if (!str) return '';
  return str.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
};

const formatDate = (isoStr) => {
  if (!isoStr) return 'N/A';
  return new Date(isoStr).toLocaleDateString();
};

const getInitials = (name) => {
  if (!name) return '??';
  const parts = name.trim().split(' ');
  if (parts.length >= 2) return (parts[0][0] + parts[1][0]).toUpperCase();
  return name.substring(0, 2).toUpperCase();
};

const getAvatarGradient = (name) => {
  const gradients = [
    'background:linear-gradient(135deg,#3B82F6,#8B5CF6);',
    'background:linear-gradient(135deg,#F59E0B,#EF4444);',
    'background:linear-gradient(135deg,#22C55E,#06B6D4);',
    'background:linear-gradient(135deg,#8B5CF6,#EC4899);'
  ];
  let hash = 0;
  for (let i = 0; i < (name || '').length; i++) hash += name.charCodeAt(i);
  return gradients[hash % gradients.length];
};

const fetchTenants = async () => {
  loading.value = true;
  try {
    const res = await api.get('/api/super/tenants');
    tenants.value = res.data;
  } catch (err) {
    console.error('Failed to fetch tenants:', err);
  } finally {
    loading.value = false;
  }
};

const fetchPersonas = async () => {
  try {
    const res = await api.get('/api/super/personas');
    personas.value = res.data;
  } catch (err) {
    console.error('Failed to fetch personas:', err);
  }
};

const fetchVoices = async () => {
  try {
    const res = await api.get('/api/super/fish-audio/voices');
    fishAudioVoices.value = res.data?.items || [];
  } catch (err) {
    console.error('Failed to fetch voices:', err);
  }
};

const totalCount = computed(() => tenants.value.length);
const activeCount = computed(() => tenants.value.filter(t => t.status === 'active').length);
const suspendedCount = computed(() => tenants.value.filter(t => t.status === 'suspended').length);

const filteredTenants = computed(() => {
  if (!searchQuery.value.trim()) return tenants.value;
  const q = searchQuery.value.toLowerCase();
  return tenants.value.filter(t => 
    (t.name && t.name.toLowerCase().includes(q)) ||
    (t.email && t.email.toLowerCase().includes(q)) ||
    (t.niche && t.niche.toLowerCase().includes(q))
  );
});

const openProvisionModal = () => {
  provisionForm.value = {
    name: '',
    niche: personas.value.length > 0 ? personas.value[0].niche_name : 'real_estate',
    email: '',
    password: '',
    credit_limit_usd: 50.00
  };
  showProvisionModal.value = true;
};

const openCustomizationModal = (tenant) => {
  selectedCustomTenant.value = tenant;
  const cfg = tenant.tenant_config || {};
  customForm.value = {
    system_prompt_override: cfg.system_prompt_override || '',
    llm_model: cfg.llm_model || 'meta-llama/llama-3.3-70b-instruct',
    llm_temperature: cfg.llm_temperature !== undefined ? cfg.llm_temperature : 0.3,
    speaking_rate: cfg.speaking_rate !== undefined ? cfg.speaking_rate : 1.0,
    tts_voice_id: cfg.tts_voice_id || '224a2257dd4943209a683d27a5e41439',
    greeting_message: cfg.greeting_message || '',
    stt_language: cfg.stt_language || 'en-US',
    max_call_duration_min: cfg.max_call_duration_min || 15
  };
};

const saveCustomConfig = async () => {
  if (!selectedCustomTenant.value) return;
  savingCustom.value = true;
  try {
    await api.put(`/api/super/tenants/${selectedCustomTenant.value.tenant_id}/config`, customForm.value);
    alert(`Successfully saved custom configuration for ${selectedCustomTenant.value.name}!`);
    selectedCustomTenant.value = null;
    fetchTenants();
  } catch (err) {
    alert(err.response?.data?.detail || 'Failed to save tenant customization.');
  } finally {
    savingCustom.value = false;
  }
};

const provisionTenant = async () => {
  provisioning.value = true;
  try {
    const res = await api.post('/api/super/provision', provisionForm.value);
    successResult.value = res.data;
    showProvisionModal.value = false;
    fetchTenants();
  } catch (err) {
    alert(err.response?.data?.detail || 'Failed to provision tenant.');
  } finally {
    provisioning.value = false;
  }
};

const toggleStatus = async (tenant) => {
  const newStatus = tenant.status === 'active' ? 'suspended' : 'active';
  if (!confirm(`Are you sure you want to change status of ${tenant.name} to ${newStatus}?`)) return;
  try {
    await api.patch(`/api/super/tenants/${tenant.tenant_id}`, { status: newStatus });
    fetchTenants();
  } catch (err) {
    alert(err.response?.data?.detail || 'Failed to update tenant status.');
  }
};

const copyToClipboard = (text) => {
  navigator.clipboard.writeText(text);
  alert('Copied to clipboard!');
};

const closeSuccessModal = () => {
  successResult.value = null;
};

onMounted(() => {
  fetchTenants();
  fetchPersonas();
  fetchVoices();
});
</script>
