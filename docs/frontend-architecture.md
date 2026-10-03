# Frontend Architecture (Next.js)

## Stack
- Next.js (App Router), React, TypeScript, Tailwind CSS.

## Pages & Components
- `/login`
- `/dashboard` (Global metrics)
- `/transactions` (Live feed)
- `/risk-dashboard` (Aggregated risk scores)
- `/fraud-dashboard` (Specific fraud metrics)
- `/customer-360/{id}`
- `/financial-health`
- `/merchant-intelligence`
- `/agent-intelligence`
- `/graph-explorer`
- `/alerts`
- `/cases`
- `/copilot` (Global widget or dedicated view)
- `/model-monitoring`
- `/simulation`
- `/audit-logs`
- `/settings`

## Core Mechanics
- **State Management:** Zustand, React Query for caching.
- **Real-time:** WebSocket connections authenticated via JWT. Listen for `alert.created`.
- **RBAC:** Component rendering blocked based on user's decoded JWT role permissions.\n