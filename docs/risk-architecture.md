# Risk Engine Architecture

## Signal Pipeline
1. **Rule Score:** Deterministic checks (e.g., Velocity > 5 in 1hr -> 100 points).
2. **ML Score:** Probabilistic output (0.0 to 1.0) scaled to 1-100.
3. **Graph Score:** Network exposure score (Distance to known bad actor).
4. **Behavior Score:** Deviation from historical baseline.
5. **Device/Location Risk:** Anomalous logins, impossible travel.

## Risk Fusion Engine
- Applies dynamic weights based on transaction type/context.
- `Final Score = (W1 * Rule) + (W2 * ML) + (W3 * Graph) + (W4 * Behavior)`
- Generates **Explainability Matrix**: Top 3 contributing factors for the final score, mapped for human readability.

## Decisions
- 0-30: Allow
- 31-70: Step-up Auth (MFA)
- 71-100: Block & Alert\n