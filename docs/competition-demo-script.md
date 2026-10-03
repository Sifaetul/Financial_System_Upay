# UPAY NEXUS AI — Competition Demo Script

## 1. Introduction
"Welcome to UPAY NEXUS AI. We built a real-time, event-driven intelligence layer for modern fintech applications. One event goes in, and multiple intelligence domains process it instantly to deliver an explainable decision."

## 2. Normal Transaction Scenario
- Open the **Transactions** view.
- Run `python scripts/demo/run_scenario.py --scenario normal_transaction`.
- Show the transaction arrive in real-time.
- Click into the **Risk Intelligence** view to show a normal risk score with no fraud signals.

## 3. Fraud Ring Scenario
- Run `python scripts/demo/run_scenario.py --scenario fraud_ring`.
- Show multiple transactions arriving with the same suspicious device ID.
- Show the **Network Intelligence** graph, highlighting the shared device linking multiple accounts.
- Show the **Fraud Intelligence** signals automatically flagging the fan-in pattern.

## 4. Real-time Alerting
- Observe the **Dashboard** as an alert pops up dynamically via WebSocket without page refresh.
- Click the alert to transition into the **Investigations** workflow.

## 5. Case Management & AI Copilot
- Open the newly generated case.
- Show the chronological evidence timeline (combining graph, transaction, and behavioral signals).
- Ask the **AI Copilot**: "Summarize the evidence for this case."
- Demonstrate the Copilot using secure, authorized retrieval to explain the fraud ring.

## 6. What-If Simulation
- Navigate to **Competition Intelligence**.
- Load the fraud-ring decision into the Simulator.
- Tweak the velocity threshold to demonstrate how the risk score would have changed.

## 7. Resilience & Observability
- Open the **Monitoring** tab.
- Manually kill the Redis container (`docker stop ai_dev_fest-redis-1`).
- Show the dashboard API degrades gracefully (Readiness becomes DEGRADED, Liveness stays HEALTHY).
- Restart Redis and show automatic recovery.
- Emphasize the architectural robustness.

## 8. Conclusion
"This proves UPAY NEXUS AI is a production-ready, highly observable, cross-domain intelligence platform that operates safely under degraded conditions while maintaining absolute explainability."
