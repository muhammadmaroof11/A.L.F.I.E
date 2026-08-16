# User Requirements & Configuration Guidelines

This document outlines the API keys, infrastructure configurations, and credentials you need to provide to fully enable the external integrations for A.L.F.I.E.

## 1. Stripe Integration (Client Self-Serve Payments) 
**Status: ✅ COMPLETED (Test Mode Active)**
- Your local `.env` is fully populated with `STRIPE_PUBLISHABLE_KEY`, `STRIPE_SECRET_KEY`, and `STRIPE_WEBHOOK_SECRET`.
- **What’s next for Stripe:** When you form your official LLC/LTD and are ready to accept real money, you will simply replace these test keys with your live keys (`sk_live_...`). No code changes are required!

---

## 2. Deployment, Hosting & Domain (🚨 NEXT IMMEDIATE STEP)
**Status: ⏳ IN PROGRESS**
You have successfully acquired the domain: **`thealfieai.com`**

### What you need to provide next:
1. **Hosting Environment**: You will need a Virtual Private Server (VPS) to host the Docker containers. Recommended providers: **DigitalOcean (Droplet), Hetzner, or AWS EC2**. An Ubuntu 22.04 or 24.04 server with at least 4GB RAM is recommended.
2. **DNS Management Access**: Once the VPS is purchased, we will need to access your domain registrar (where you bought `thealfieai.com`) to point the DNS A-Records to your new VPS IP address.
3. **CORS & Environment Updates**: Before deployment, we will update `ALLOWED_ORIGINS` in your `.env` to include `https://thealfieai.com` and `https://app.thealfieai.com`.

---

## 3. Twilio Integration (PSTN Phone Numbers & Routing)
**Status: ❌ PENDING**

*Note: Internal agent-to-agent transfers currently use native LiveKit SIP, which is free. Twilio is primarily required for purchasing external phone numbers (DIDs) for your tenants.*

### Keys Needed (Add to `.env` later):
- `TWILIO_ACCOUNT_SID`: Found on your Twilio Console homepage.
- `TWILIO_AUTH_TOKEN`: Found on your Twilio Console homepage.

### Registration Guidelines for Twilio:
1. **Account Setup**: Go to [Twilio.com](https://www.twilio.com) and create an account.
2. **Regulatory Bundles**: If you plan to buy phone numbers in specific countries (e.g., Australia, UK), you will need to submit a Regulatory Bundle with your business identity documents in the Twilio console before they allow you to purchase local numbers.
3. **SIP Trunking**: 
   - Navigate to "Voice" -> "SIP Trunking" -> "Trunks".
   - Create a new trunk to connect Twilio calls to your LiveKit infrastructure.
   - Point the Origination URI to your LiveKit SIP ingress address (which will be hosted on your domain).
4. **Funding**: You must add a credit card to fund your Twilio balance to purchase numbers and pay for inbound PSTN per-minute usage.
