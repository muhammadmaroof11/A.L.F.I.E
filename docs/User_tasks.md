# A.L.F.I.E Setup Checklist

Follow these exact steps to complete the setup of the unified A.L.F.I.E platform. We have moved from low-code tools to custom, high-performance Vue.js dashboards for maximum control.

### 1. Boot the Stack
Before running these commands, ensure Docker Desktop is open and running on your machine.

Run this from your terminal to start the AI agent, backend APIs, and the PostgreSQL database:
```bash
docker compose up -d
```

---

### 2. Run Database Migrations
Since we have added the new Email & Password authentication flow and the multitenancy schema, you must initialize the database:

```bash
docker compose exec alfie-agent python scripts/migrate_db.py
```
*This script will safely create the necessary tables (`alfie_tenants`, `alfie_telemetry`, etc.) and add the `email` and `password_hash` columns.*

---

### 3. Start the UI Dashboards
We have built two separate Vue.js applications for you and your clients. Open two new terminal windows and start both development servers.

**Terminal 1 (Super Admin Portal):**
```bash
cd super_admin_ui
npm install
npm run dev -- --port 5173
```
This is your master control panel. Access it at `http://localhost:5173/`. Use it to provision new client tenants, assign their email/passwords, and monitor global usage and agent behavior.

**Terminal 2 (Client Admin Portal):**
```bash
cd client_admin_ui
npm install
npm run dev -- --port 5174
```
This is what you sell to your clients. Access it at `http://localhost:5174/`. 
Clients can now log in securely using the Email Address and Password you provisioned for them in the Super Admin Portal.

---

### 4. Provision Your First Tenant
1. Open the **Super Admin Portal** (`http://localhost:5173/`).
2. Go to the **Tenants & Provisioning** tab.
3. Click **Provision Tenant** and fill in the details:
   - **Company Name:** (e.g., Alfie Realty)
   - **Email Address:** (e.g., admin@alfierealty.com)
   - **Password:** (e.g., SecurePass123!)
   - **Niche:** Real Estate
4. Click **Provision**. Note down the generated API Key for SDK integrations (the UI login will use the Email and Password).

---

### 5. Verify the Client Experience
1. Open the **Client Admin Portal** (`http://localhost:5174/`).
2. Log in using the Email Address and Password you just provisioned.
3. Navigate through the beautiful Aurora-themed dashboard to view Analytics, Lead Interactions, and configure the Agent's AI settings.

---

### 6. Setup n8n Automations (Optional)
If you are still using n8n for background CRON jobs or specific webhook integrations (like deleting old telemetry data):
1. Open your browser and go to `http://localhost:5678`.
2. Go to **Workflows** > **Import from File**.
3. Select `platform/n8n_alfie_workflow.json`.
4. Ensure your **Environment Variables** (like `TWILIO_ACCOUNT_SID`) are set in n8n's settings.
