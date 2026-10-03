# End-to-End Data Flow

## Primary Transaction Flow

```mermaid
sequenceDiagram
    participant Source
    participant API as API Gateway
    participant DB as PostgreSQL
    participant Redis as Event Broker
    participant Feat as Feature Extractor
    participant Engine as Intelligence Engines (Rule/ML/Graph)
    participant Risk as Risk Fusion
    participant UI as Dashboard

    Source->>API: POST /transactions (Transaction Created)
    API->>API: Validate Payload
    API->>DB: Save Transaction (Status: Pending)
    API->>Redis: Publish `transaction.created`
    API-->>Source: 202 Accepted

    Redis->>Feat: Consume `transaction.created`
    Feat->>Feat: Extract Features (Velocity, Location, etc.)
    Feat->>Redis: Publish `features.extracted`

    Redis->>Engine: Consume `features.extracted`
    Engine->>Engine: Run Rules, ML Inference, Graph Traversal
    Engine->>Redis: Publish `signals.generated`

    Redis->>Risk: Consume `signals.generated`
    Risk->>Risk: Normalize, Weight, Fusion
    Risk->>DB: Save Final Risk Score & Decision
    Risk->>Redis: Publish `risk.calculated`
    
    Redis->>UI: WebSocket emit `alert.created` (if high risk)
```\n