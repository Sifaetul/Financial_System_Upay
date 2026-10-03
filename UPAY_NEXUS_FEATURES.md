# UPAY NEXUS AI - Core Features & Internal Logic

This document provides a deep dive into every feature of the **UPAY NEXUS AI** platform, explaining the internal logic (Backend/AI) and the visual representation (Frontend).

---

## 1. Global Intelligence Command Center (Dashboard)
**Path:** `/dashboard`

### Screen Representation
- **System Optimal Beacon:** A pulsing green beacon indicating the realtime health of the risk engine.
- **Interactive Quick Actions:** Buttons to trigger Deep Network Scans or generate reports. Includes realistic loading states and success toasts.
- **Operational Telemetry (KPIs):** Hoverable cards showing Live Transactions, Active Alerts, Open Cases, and Critical Fraud Signals.
- **Priority Action Queue:** A color-coded, prioritized list of alerts.
- **Copilot Insights:** A glowing, premium dark-themed card summarizing the AI's current analysis of the platform's topology.

### Internal Core Logic
- The frontend fetches aggregated data via `Promise.all` from `/health`, `/investigation/alerts`, `/investigation/cases`, and `/transactions`.
- **System Health:** Validates the connectivity of the FastAPI backend, PostgreSQL (pgvector), and Redis caches.
- **AI Summary:** Evaluates the `activeAlerts` array length to deterministically generate a topological risk summary. If alerts exist, it recommends network investigation; otherwise, it confirms a baseline distribution.

---

## 2. Live Transaction Stream (Transactions)
**Path:** `/transactions`

### Screen Representation
- **Live Pulse Feed:** A "LIVE FEED ACTIVE" button that blinks to show real-time ingestion.
- **Dynamic Ingestion Animation:** Every 3 seconds, a new transaction drops at the top of the table, highlighted in green for 2 seconds before blending in.
- **AI Risk Score:** A visual progress bar (Green/Yellow/Red) showing the exact risk score.
- **Badges:** Transaction types (Transfer/Payment) and Statuses (BLOCKED/CLEARED) are shown with distinct icons.

### Internal Core Logic
- Connects to the backend `/transactions` REST API to fetch the historical transaction baseline.
- **Simulated Real-time Ingestion:** Uses a React `useEffect` interval loop. With a 30% probability every 3 seconds, it generates a synthetic transaction with a randomized risk score and prepends it to the React state array, simulating a WebSocket or SSE push from the Unified Risk Engine.
- **Blocking Logic:** If the AI Risk Score is >= 80, the transaction status is deterministically rendered as `BLOCKED`.

---

## 3. Platform Risk Overview (Risk)
**Path:** `/risk`

### Screen Representation
- **Global Risk Index:** A massive numeric score (e.g., 84.2/100) indicating the overall threat level of the financial platform.
- **Prioritized Case Queue:** A custom-built table that translates raw severity scores into actionable SLA (Service Level Agreement) badges.
  - `[🔥 Priority 1 (P1)]` -> SLA: 15 mins (Immediate Action)
  - `[⚠️ Priority 2 (P2)]` -> SLA: 1 hour (Elevated)
  - `[📈 Priority 3 (P3)]` -> SLA: 24 hours (Review)

### Internal Core Logic
- Fetches all investigation cases from `/investigation/cases`.
- **Variance Algorithm:** To ensure a realistic demo without all cases defaulting to a single priority, a pseudo-random deterministic modulo algorithm `(c.id.charCodeAt(0) % 3)` is applied to distribute cases evenly into P1, P2, and P3 tiers.
- Maps the Priority back to the visual `Severity` badge to ensure logical consistency across the table.

---

## 4. Active Cases Workspace (Investigations)
**Path:** `/investigations`

### Screen Representation
- **Dual-Pane Layout:** A master-detail view where the left side lists Active Cases and the right side shows case details.
- **Slide-over Evidence Panel:** Clicking "View Evidence" slides in a sleek side-panel detailing the primary risk signal (e.g., Anomalous Transaction Spike) and behavioral anomalies (e.g., New iPhone login, 8 outbound transfers).
- **Stateful Actions:** Clicking "Mark Safe & Close" replaces the button with a spinning "Closing..." state, then instantly grays out the case and marks it as `CLOSED`.

### Internal Core Logic
- Pulls case data from the backend.
- The "View Evidence" button leverages a React state `selectedEvidence` to conditionally render a Tailwind `translate-x` animated sidebar.
- **Case Resolution:** The "Mark Safe" button triggers a simulated asynchronous mutation (`setTimeout`), modifying the local case array state to `CLOSED`. This mimics a `PATCH /cases/{id}/status` request to the backend.

---

## 5. Customer 360 Intel (Customer Intelligence)
**Path:** `/customers`

### Screen Representation
- **Global Search:** A functional search bar where investigators can look up a customer ID, phone, or email.
- **Device Fingerprinting:** Shows the customer's known devices (e.g., MacBook Pro, iPhone) and marks them as `TRUSTED` or `UNVERIFIED`.
- **Live Behavioral Risk Gauge:** A massive visual gauge metric showing the user's engagement/risk score.
- **Continuous Analysis:** An AI text block explaining the customer's recent velocity against geographic baselines.

### Internal Core Logic
- The `handleSearch` function attempts to hit `/customers/{id}/360` on the backend.
- **Robust Fallback:** If the backend returns a 404 (because the specific synthetic ID isn't in the DB), the `catch` block intercepts it and injects a highly realistic `fallbackData` object. This ensures the demo never breaks or shows a blank screen, always presenting a fully fleshed-out profile.
- **Identity Synthesis:** The search query is dynamically injected into the fallback object so the UI reflects exactly what the user searched for.

---

## 6. Nexus AI Copilot
**Path:** `/copilot`

### Screen Representation
- **Chat Interface:** A highly polished chat window similar to ChatGPT or Claude.
- **Suggested Prompts:** Quick-action chips like "Analyze recent transactions" or "Scan network for fraud".
- **Typing Animation:** The AI responds with a realistic character-by-character typing effect.

### Internal Core Logic
- **Keyword-based Heuristics:** To avoid LLM timeouts during the live demo, the Copilot uses a sophisticated deterministic regex matcher.
  - If the prompt contains `network` or `ring`, it returns a simulated Graph Intelligence report about a 4-node fraud ring.
  - If the prompt contains `risk` or `score`, it explains the Unified Risk Engine's random forest models.
  - If the prompt contains `transaction`, it explains velocity anomalies.
- **State Management:** Uses React intervals to substring the response string, creating a seamless streaming text effect.

---

## 7. Model Monitoring & Governance
**Path:** `/monitoring` & `/governance/audit`

### Screen Representation
- **Monitoring:** Displays the F1-Score, Precision, Recall, and Latency of the underlying AI models (XGBoost, GraphSAGE).
- **Audit Log:** A searchable table of system events (e.g., Risk Engine Updated, Case Closed, User Logged In) with strict timestamps.

### Internal Core Logic
- These pages act as the "Admin / DevOps" view. They demonstrate the platform's compliance and operational maturity.
- Visualizes static telemetry data designed to look like Grafana or Datadog dashboards, reinforcing the "Enterprise Grade" nature of the application.
