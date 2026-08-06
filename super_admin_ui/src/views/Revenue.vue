<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
      <div class="flex flex-col space-y-1">
        <h2 class="text-2xl font-semibold tracking-tight">Revenue & Billing</h2>
        <p class="text-sm text-muted-foreground">Overview of financial performance across all tenants.</p>
      </div>
      <div class="flex items-center gap-2">
        <button class="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring border border-input bg-background shadow-sm hover:bg-accent hover:text-accent-foreground h-9 px-4 py-2 shrink-0">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="mr-2 h-4 w-4"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" x2="12" y1="15" y2="3"/></svg>
          Export CSV
        </button>
      </div>
    </div>

    <!-- Stats strip -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="rounded-xl border bg-card text-card-foreground shadow-sm p-6 flex flex-col justify-between hover:shadow-md transition-shadow">
        <div class="flex items-center justify-between space-y-0 pb-2">
          <h3 class="tracking-tight text-sm font-medium">Total Revenue (MTD)</h3>
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-emerald-500"><line x1="12" x2="12" y1="2" y2="22"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
        </div>
        <div class="text-2xl font-bold tracking-tight text-emerald-500">$4,290.00</div>
        <p class="text-xs text-muted-foreground mt-1">+12.5% from last month</p>
      </div>

      <div class="rounded-xl border bg-card text-card-foreground shadow-sm p-6 flex flex-col justify-between hover:shadow-md transition-shadow">
        <div class="flex items-center justify-between space-y-0 pb-2">
          <h3 class="tracking-tight text-sm font-medium">Projected (EOM)</h3>
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-blue-500"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
        </div>
        <div class="text-2xl font-bold tracking-tight text-blue-500">$6,150.00</div>
        <p class="text-xs text-muted-foreground mt-1">+8.2% from last month</p>
      </div>

      <div class="rounded-xl border bg-card text-card-foreground shadow-sm p-6 flex flex-col justify-between hover:shadow-md transition-shadow">
        <div class="flex items-center justify-between space-y-0 pb-2">
          <h3 class="tracking-tight text-sm font-medium">Avg Rev Per Tenant</h3>
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-violet-500"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
        </div>
        <div class="text-2xl font-bold tracking-tight text-violet-500">$186.50</div>
        <p class="text-xs text-muted-foreground mt-1">+2.4% from last month</p>
      </div>

      <div class="rounded-xl border bg-card text-card-foreground shadow-sm p-6 flex flex-col justify-between hover:shadow-md transition-shadow">
        <div class="flex items-center justify-between space-y-0 pb-2">
          <h3 class="tracking-tight text-sm font-medium">Pending Invoices</h3>
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-amber-500"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
        </div>
        <div class="text-2xl font-bold tracking-tight text-amber-500">$420.00</div>
        <p class="text-xs text-muted-foreground mt-1">4 invoices pending</p>
      </div>
    </div>

    <div class="rounded-xl border bg-card text-card-foreground shadow-sm">
      <div class="flex flex-col space-y-1.5 p-6 border-b">
        <h3 class="font-semibold leading-none tracking-tight">Recent Transactions</h3>
        <p class="text-sm text-muted-foreground">Latest payments processed.</p>
      </div>
      
      <div class="w-full overflow-auto">
        <table class="w-full caption-bottom text-sm">
          <thead class="[&_tr]:border-b bg-muted/50">
            <tr class="border-b transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted">
              <th class="h-10 px-4 text-left align-middle font-medium text-muted-foreground w-[15%]">Date</th>
              <th class="h-10 px-4 text-left align-middle font-medium text-muted-foreground w-[25%]">Tenant</th>
              <th class="h-10 px-4 text-left align-middle font-medium text-muted-foreground w-[35%]">Description</th>
              <th class="h-10 px-4 text-left align-middle font-medium text-muted-foreground w-[15%]">Amount</th>
              <th class="h-10 px-4 text-left align-middle font-medium text-muted-foreground w-[10%]">Status</th>
            </tr>
          </thead>
          <tbody class="[&_tr:last-child]:border-0">
            <tr class="border-b transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted">
              <td class="p-4 align-middle">
                <span class="font-mono text-xs text-muted-foreground">2026-08-05</span>
              </td>
              <td class="p-4 align-middle font-medium text-foreground">
                Alfie Realty PK
              </td>
              <td class="p-4 align-middle text-muted-foreground">
                Monthly Subscription Base
              </td>
              <td class="p-4 align-middle">
                <span class="font-semibold text-foreground">$50.00</span>
              </td>
              <td class="p-4 align-middle">
                <span class="inline-flex items-center rounded-full border border-transparent bg-emerald-500/10 px-2.5 py-0.5 text-xs font-semibold text-emerald-500">Paid</span>
              </td>
            </tr>

            <tr class="border-b transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted">
              <td class="p-4 align-middle">
                <span class="font-mono text-xs text-muted-foreground">2026-08-04</span>
              </td>
              <td class="p-4 align-middle font-medium text-foreground">
                DriveFast Rentals
              </td>
              <td class="p-4 align-middle text-muted-foreground">
                Overage Charges (2,000 mins)
              </td>
              <td class="p-4 align-middle">
                <span class="font-semibold text-foreground">$120.00</span>
              </td>
              <td class="p-4 align-middle">
                <span class="inline-flex items-center rounded-full border border-transparent bg-emerald-500/10 px-2.5 py-0.5 text-xs font-semibold text-emerald-500">Paid</span>
              </td>
            </tr>
            
            <tr class="border-b transition-colors hover:bg-muted/50 data-[state=selected]:bg-muted">
              <td class="p-4 align-middle">
                <span class="font-mono text-xs text-muted-foreground">2026-08-02</span>
              </td>
              <td class="p-4 align-middle font-medium text-foreground">
                HomeFinders Ltd
              </td>
              <td class="p-4 align-middle text-muted-foreground">
                Monthly Subscription Base
              </td>
              <td class="p-4 align-middle">
                <span class="font-semibold text-foreground">$50.00</span>
              </td>
              <td class="p-4 align-middle">
                <span class="inline-flex items-center rounded-full border border-transparent bg-amber-500/10 px-2.5 py-0.5 text-xs font-semibold text-amber-500">Pending</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
</script>
