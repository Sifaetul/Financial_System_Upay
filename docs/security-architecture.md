# Security & RBAC Architecture

## Authentication
- JWT with short expiration (15m). HttpOnly cookie for Refresh token (7d).

## RBAC Matrix
| Role | Alerts | Cases | AI Copilot | System Config | Transactions |
|------|--------|-------|------------|---------------|--------------|
| Admin | R/W | R/W | Yes | R/W | R/W |
| Investigator | R/W | R/W | Yes | No | R/O |
| Risk Analyst | Read | Read | No | R/W (Rules) | R/O |
| Customer Support | Read | No | No | No | R/O (Masked)|
| ML/AI Analyst | Read | Read | Yes | R/W (Models)| R/O |

## Core Protections
- **SQL Injection:** Prevented via SQLAlchemy ORM.
- **Rate Limiting:** Redis-based token bucket per IP/User.
- **Secrets Management:** Environment variables, no hardcoded credentials.
- **Input Validation:** Strict Pydantic schemas.
- **Data Privacy:** Sensitive data masking on API output.
- **Audit Logging:** Immutably logs all sensitive actions.\n