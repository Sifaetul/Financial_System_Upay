from .websockets import router as ws_router
from fastapi import APIRouter
from .endpoints import health
from .endpoints import auth
from .endpoints import transactions
from .endpoints import risk
from .endpoints import fraud
from .endpoints import graph
from .endpoints import customer
from .endpoints import financial
from .endpoints import merchant
from .endpoints import agent
from .endpoints import investigation
from .endpoints import copilot

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
api_router.include_router(risk.router, prefix="/risk", tags=["risk"])

api_router.include_router(fraud.router, prefix="/fraud", tags=["fraud"])

api_router.include_router(graph.router, prefix="/graph", tags=["graph"])

api_router.include_router(customer.router, prefix="/customers", tags=["customers"])

api_router.include_router(financial.router, prefix="/customers", tags=["financial"])

api_router.include_router(merchant.router, prefix="/merchants", tags=["merchants"])
api_router.include_router(agent.router, prefix="/agents", tags=["agents"])

api_router.include_router(ws_router, prefix="/ws", tags=["websockets"])

api_router.include_router(investigation.router, prefix="/investigation", tags=["investigation"])
api_router.include_router(copilot.router, prefix='/copilot', tags=['copilot'])

from app.api.competition_api import router as competition_router
api_router.include_router(competition_router, prefix="", tags=["competition"])
