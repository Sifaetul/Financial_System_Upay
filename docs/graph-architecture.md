# Graph Intelligence Architecture

## Model
- **Nodes:** Customer, Account, Device, Location, Merchant, Agent, Beneficiary.
- **Relationships:** owns, uses, sends, receives, transacts, logs_in, connected_to.

## Graph Engine (NetworkX initial)
- Loads local sub-graphs from PostgreSQL relational data on demand.
- Future: Syncs to Neo4j for deep persistent graph traversal.

## Analysis Capabilities
- **Suspicious Clusters:** N accounts sharing 1 device.
- **Fraud Rings:** Cyclic transaction paths indicating money laundering.
- **Network Exposure:** Shortest path to flagged fraud node.
- *Important Rule:* Exposure must be treated as a risk signal, NOT automatically as confirmed fraud.\n