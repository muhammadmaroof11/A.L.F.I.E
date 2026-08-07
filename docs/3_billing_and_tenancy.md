# Tenancy & Sovereign Billing

A.L.F.I.E. is built to be a profitable SaaS out of the box. Billing is isolated, hierarchical, and heavily customizable.

## The Financial Ledger
Every action that costs compute (LLM tokens, STT streaming, TTS generation) is tracked against a tenant's credit pool.
We maintain two states of capital:
1. **Included Minutes:** Renewed monthly based on the subscription tier.
2. **Prepaid Credit Balance:** Burned only when included minutes reach 0, or if the tenant is on a strict Pay-As-You-Go plan.

## The Midnight Sweeper (`worker.py`)
Billing isn't a passive endpoint; it is an active mechanical sweeper.
We utilize **ARQ (Redis-backed)** to run `arq.cron` jobs at exactly `00:00 UTC` daily.
- The `process_subscription_renewals` task scans the `alfie_tenants` table.
- If a tenant's `subscription_cycle_end` has passed, it deducts the base monthly price from their credit balance, resets their included minutes, logs the transaction in `alfie_credit_transactions`, and pushes the cycle end date forward 30 days.

## Custom Override Dynamics
Not all enterprise clients fit into Tier 1 or Tier 2. 
The Super Admin UI provides a Custom Configuration overlay. If a tenant complains about pricing, the Super Admin can isolate their account and manually override:
- `custom_monthly_price`
- `custom_included_minutes`
- `custom_per_minute_rate`

The backend billing processor detects if `subscription_tier = 'custom'` and seamlessly routes the mathematical logic to these bespoke variables.

## Stripe Webhook Integration
To prevent the platform owner from manually invoicing clients, the Client Admin portal includes a Self-Serve Top-Up UI.
1. The user selects an amount (e.g., $100) and hits Checkout.
2. The backend generates a Stripe Checkout Session with `metadata: { tenant_id: <uuid> }`.
3. The user pays via Stripe.
4. Stripe fires the `checkout.session.completed` event to `/api/webhooks/stripe`.
5. The backend validates the cryptographic signature, writes to `alfie_credit_transactions`, and adds exactly $100.00 to the tenant's `credit_limit_usd` available balance in real time.
