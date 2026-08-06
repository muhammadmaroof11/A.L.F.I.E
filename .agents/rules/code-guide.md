---
trigger: always_on
description: Mandatory rules for STATE.md synchronization and Zero Secret Exposure
---

# Code & State Governance Rules

1. **STATE.md Synchronization**: Whenever making changes to backend APIs, schemas, Super Admin UI, Client Admin UI, or scripts, always update `STATE.md` in the project root to reflect current state and track pending synchronization items across the platform.
2. **Zero Secret Exposure**: Never expose sensitive keys or secrets in any file or git history. Always reference `.env` or Docker secrets (`/run/secrets/` or `secrets/` directory).
