"""Aggregate all v1 routers."""
from fastapi import APIRouter

from app.api.v1 import analysis, auth, cases, chat, er_status, report

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(cases.router)
api_router.include_router(analysis.router)
api_router.include_router(report.router)
api_router.include_router(er_status.router)
api_router.include_router(chat.router)
