# A.L.F.I.E GUI Setup Checklist

Follow these exact steps to complete the visual setup of the unified platform. 

### 1. Boot the Stack
Run this from your terminal:
```bash
cd platform
docker-compose up -d
```

---

### 2. Twenty CRM Setup (The Brain)
1. Open your browser and go to `http://localhost:3000`.
2. Follow the setup wizard to create your Admin workspace.
3. Generate the API Key:
   - Go to **Settings > API & Webhooks** (enable Advanced Mode if you don't see it).
   - Generate a new API Key.
   - Open `platform/.env` and replace `TWENTY_API_KEY=""` with your new key.
4. Create the Custom Objects:
   - Go to **Settings > Data Model**.
   - Click **+ New object**.
   - **Object 1:** 
     - Name: `Property` (Plural: `Properties`)
     - Fields: `title` (Text), `city` (Text), `price` (Number), `bedrooms` (Number), `status` (Select: Available, Sold)
   - **Object 2:** 
     - Name: `Vehicle` (Plural: `Vehicles`)
     - Fields: `make` (Text), `model` (Text), `category` (Text), `dailyRate` (Number), `status` (Select: Available, Rented)
   - **Object 3:**
     - Name: `InteractionLog` (Plural: `InteractionLogs`)
     - Fields: `leadId` (Relation -> Lead), `status` (Text), `duration` (Text), `recordingUrl` (Text), `summary` (Text), `transcript` (Raw JSON), `extractedData` (Raw JSON)
   - **Object 4:**
     - Name: `AgentConfig` (Plural: `AgentConfigs`)
     - Fields: 
       - `tenantId` (Text, Unique)
       - `niche` (Text)
       - `agentName` (Text)
       - `systemPrompt` (Text)
       - `greetingMessage` (Text) ← The opening line the AI says when the call connects
       - `humanAgentSipUri` (Text) ← SIP URI to transfer calls to (e.g. `sip:agent@yourdomain.com`)
       - `enabledTools` (Text) ← Comma-separated: `core_tools,real_estate_tools`
       - `llmModel` (Text)
       - `llmTemperature` (Number)
       - `llmMaxTokens` (Number)
       - `sttLanguage` (Text)
       - `sttModel` (Text)
       - `sttProfanityFilter` (Boolean)
       - `sttPunctuation` (Boolean)
       - `ttsProvider` (Text) ← `fish_audio` or `openai`
       - `ttsModel` (Text)
       - `ttsVoiceId` (Text)
       - `ttsLatencyMode` (Text)
       - `vadMinSilence` (Number)
       - `vadThreshold` (Number)
       - `allowInterruptions` (Boolean)
   - **Data Entry Required:** Add a record with `tenantId` = `alfie_realty_pk`, `niche` = `real_estate`, `agentName` = `Alfie`, `enabledTools` = `core_tools,real_estate_tools`, `llmModel` = `meta-llama/llama-3.1-8b-instruct`, `greetingMessage` = `Hello, this is Alfie from Alfie Realty. How can I help with your property search today?`. Leave numeric fields empty for safe defaults.

---

### 3. Appsmith Setup (The Two Dashboards)
Because we are building a multi-tenant platform, you will build **two** separate apps in Appsmith:

#### A. Super Admin Portal (For You)
This is where you provision new clients, tune the AI, and monitor global usage.
1. Create a new App named **Super Admin Portal**.
2. Connect the `twenty_db` PostgreSQL datasource.
3. Use **Generate Page from Data** on the `agent_configs` table. This generates the master control panel where you can edit the LLM temperatures, STT models, and TTS latency for any client visually.
4. **Building the Telemetry Dashboard:**
   - Create a Blank Page named "Analytics".
   - Drag in a **Chart Widget** (Bar Chart). Bind its data to a query: `SELECT tenant_id as x, count(*) as y FROM alfie_telemetry WHERE event_type = 'METRIC_UPDATE' GROUP BY tenant_id`.
   - Drag in a **Table Widget** for live debugging logs. Bind it to: `SELECT timestamp, tenant_id, call_id, event_type, data FROM alfie_telemetry ORDER BY timestamp DESC LIMIT 100`.

#### B. Client Admin Portal (For the Agencies)
This is what you sell to clients. It is restricted to their data.
1. Create a new App named **Client Admin Dashboard**.
2. Connect the `twenty_db` PostgreSQL datasource.
3. Use **Generate Page from Data** on `Property` or `Vehicle` tables.
4. **Building the Interaction Feed:** 
   - Create a new Blank Page.
   - Drag in a **List Widget**. Bind its data to a query: `SELECT * FROM interaction_logs WHERE lead_id = {{appsmith.URL.queryParams.leadId}}`.
   - Inside the List Widget item, drag an **Audio Widget** (bind URL to `{{currentItem.recordingUrl}}`).
   - Drag **Text Widgets** for `{{currentItem.summary}}` and `{{currentItem.duration}}`.

---

### 4. n8n Setup (The Automations)
1. Open your browser and go to `http://localhost:5678`.
2. Setup your admin account.
3. Go to **Workflows**.
4. In the top right corner, click the **...** menu and select **Import from File**.
5. Select the `platform/n8n_alfie_workflow.json` file in your repository.
6. The workflow will instantly appear! It's pre-configured to listen for webhooks at `http://n8n:5678/webhook/alfie-events`.
7. **Set n8n Environment Variables:** In n8n Settings > Environment Variables, add:
   - `TWENTY_API_KEY` = your Twenty CRM API key
   - `TWILIO_ACCOUNT_SID` = your Twilio SID (for SMS confirmations)
   - `TWILIO_FROM_NUMBER` = your Twilio phone number
8. **Add OpenAI credential** in n8n → Settings → Credentials → New → OpenAI API (used by the AI Summarize node).
9. **Set up Telemetry Pruning:** Create a new n8n Cron workflow: `Schedule Trigger` (every Sunday 00:00) → `Postgres Node` → SQL: `DELETE FROM alfie_telemetry WHERE timestamp < NOW() - INTERVAL '90 days'; DELETE FROM alfie_usage WHERE timestamp < NOW() - INTERVAL '180 days';`

---

### 5. Final Step: Run A.L.F.I.E
Restart your docker compose stack so the agent picks up the new `TWENTY_API_KEY`:
```bash
docker-compose down
docker-compose up -d --build
```
You are now ready to make phone calls!
