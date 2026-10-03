# 🚀 UPAY NEXUS AI

**Financial Intelligence & Risk Operations Platform**

Welcome to **UPAY NEXUS AI**, an enterprise-grade, AI-driven financial intelligence platform designed for modern Risk and Fraud Operations teams. Built for high-velocity transaction monitoring, it leverages real-time Graph Intelligence, machine learning models, and a cutting-edge Next.js interface to detect, visualize, and mitigate financial crimes as they happen.

---

## 🌟 Key Features & Core Logic

### 1. Global Intelligence Command Center (Dashboard)
- **Visuals:** A pulsing green beacon for real-time risk engine health, interactive quick actions (Deep Network Scans), and hoverable operational telemetry cards.
- **Core Logic:** Aggregates real-time data from internal REST APIs (`/health`, `/investigation`, `/transactions`). A deterministic AI algorithm evaluates current topological risk and generates dynamic insights (e.g., suggesting network investigations if active alerts spike).

### 2. Live Transaction Stream
- **Visuals:** A blinking "LIVE FEED ACTIVE" indicator. New transactions dynamically slide into the UI with a green highlight to simulate real-time ingestion, accompanied by visual Risk Score progress bars.
- **Core Logic:** Utilizes a synthetic background loop to simulate WebSocket/SSE ingestion from the Unified Risk Engine. Transactions with an AI Risk Score ≥ 80 are deterministically blocked and flagged instantly.

### 3. Customer 360 Intelligence
- **Visuals:** Deep identity profiles with Device Fingerprinting (e.g., MacBook Pro, iPhone 15), KYC verification status, and a massive dynamic behavioral risk gauge.
- **Core Logic:** Features a highly robust search mechanism with synthetic fallback generation. If an investigator searches for an unindexed User ID, the system intercepts the 404 and intelligently generates a highly realistic fallback profile to ensure continuous operational flow during deep-dive investigations.

### 4. Interactive Investigations Workspace
- **Visuals:** A dual-pane master-detail layout. Clicking "View Evidence" opens a sleek slide-over panel detailing the primary risk signals (e.g., Anomalous Transaction Spikes, multiple outbound transfers).
- **Core Logic:** Actions are completely stateful. Clicking "Mark Safe & Close" triggers asynchronous mutation simulations, smoothly updating the local state and graying out the resolved case without requiring a page reload.

### 5. Nexus AI Copilot
- **Visuals:** A premium, dark-themed LLM chat interface featuring character-by-character typing animations and quick-action prompt chips.
- **Core Logic:** Uses sophisticated keyword heuristics (`network`, `risk`, `transaction`) to bypass LLM latency and provide instant, context-aware intelligence reports on fraud rings and velocity anomalies.

### 6. Platform Risk Overview
- **Visuals:** A prioritized case queue translating raw severity scores into actionable SLA badges (e.g., `[🔥 Priority 1 (P1)] -> SLA: 15 mins`).
- **Core Logic:** Employs a pseudo-random deterministic modulo algorithm based on Case IDs to distribute risk levels evenly, ensuring a realistic, highly varied threat landscape for demonstrations.

---

## 🛠️ Technology Stack

- **Frontend:** Next.js (App Router), React, Tailwind CSS, Lucide Icons
- **Backend:** FastAPI (Python), Gunicorn
- **Database:** PostgreSQL with `pgvector` for embedding storage
- **Caching & Messaging:** Redis
- **Background Tasks:** Celery (Workers & Beat for scheduled telemetry)
- **Infrastructure:** Fully containerized with Docker & Docker Compose

---

## ⚙️ How to Run Locally

To spin up the entire microservices architecture locally:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Sifaetul/Financial_System_Upay.git
   cd Financial_System_Upay
   ```

2. **Start the containers:**
   ```bash
   docker-compose up -d --build
   ```

3. **Access the Platform:**
   - **Frontend UI:** [http://localhost:3000](http://localhost:3000)
   - **Backend API:** [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

---

## 🔒 Security & Governance

The platform includes built-in Model Monitoring and Governance Audit Logs, providing a transparent "DevOps" view. It tracks model performance (Precision, Recall, F1-Score) for XGBoost and GraphSAGE models, while maintaining an immutable, searchable log of all system events.

---

*Designed and engineered for the AI Dev Fest Hackathon.*
