# Unified Platform Architecture Documentation

## Overview
This document records the research and integration architecture for combining Twenty CRM, Appsmith, and n8n onto a single shared PostgreSQL database, forming the backbone for the A.L.F.I.E. Voice AI agent.

## Core Database: PostgreSQL
Instead of maintaining separate databases (MongoDB for ALFIE, MySQL for CRM, Postgres for automation), the entire unified platform will use a single **PostgreSQL 15+** instance.
- **Database Namespaces:** We will provision separate logical databases within the same Postgres container:
  - `twenty_db`: Owned by Twenty CRM (stores metadata, leads, and custom objects like Properties).
  - `appsmith_db`: Owned by Appsmith (for internal state). Appsmith will also be configured with a *Datasource* connection to `twenty_db` to read/write real estate and car rental records directly.
  - `n8n_db`: Owned by n8n (for workflow execution state).

## 1. Twenty CRM Integration
- **Role:** The primary UI for basic CRM functions (Pipelines, Leads, Tasks) and the master schema owner for custom objects.
- **Docker Compose Setup:**
  - Standard `twentycrm/twenty:latest` image.
  - Environment variable `PG_DATABASE_URL=postgres://user:pass@postgres_host:5432/twenty_db`.
  - Requires a Redis container alongside it.
- **ALFIE Hook:** ALFIE will query Twenty's auto-generated GraphQL API for checking vehicle/property availability and making bookings.

## 2. Appsmith Integration
- **Role:** High-end custom dashboard builder. Because Twenty's UI is geared towards CRM pipelines, Appsmith is used for niche-specific views (e.g., an interactive map of Real Estate properties or a Gantt chart of Car Rental fleet availability).
- **Docker Compose Setup:**
  - Standard `appsmith/appsmith-ce` image.
  - Will connect to the shared Postgres instance for its internal state via `APPSMITH_KEYCLOAK_DB_URL=jdbc:postgresql://postgres_host:5432/appsmith_db`.
- **ALFIE Hook:** Appsmith acts purely as a "Read/Write" visualization layer over the exact same tables ALFIE is using in Twenty.

## 3. n8n Integration
- **Role:** The workflow automation engine. Necessary for routing webhooks to external third parties (like sending a Twilio SMS or syncing leads to an external Google Sheet if a real estate agent demands it).
- **Docker Compose Setup:**
  - Standard `n8nio/n8n:latest` image.
  - `DB_TYPE=postgresdb`, pointing to the shared Postgres instance (`n8n_db`).
- **ALFIE Hook:** ALFIE (or Twenty) fires webhooks upon successful bookings. n8n catches these webhooks and executes complex external integrations.

## Execution Sequence
1. **Infrastructure:** Stand up a single `postgres:15` container with an init script to create the three databases (`twenty_db`, `appsmith_db`, `n8n_db`).
2. **Platform Boot:** Start Twenty, Appsmith, and n8n within the same Docker network.
3. **Data Model:** Create "Properties" and "Vehicles" custom objects in Twenty.
4. **Appsmith Linking:** Create a Postgres Datasource in Appsmith pointing to `twenty_db` to build custom UI.
5. **ALFIE Refactoring:** Update A.L.F.I.E tools to hit Twenty's GraphQL API instead of MongoDB.
