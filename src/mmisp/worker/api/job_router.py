"""
Encapsulates API calls for jobs
"""

from fastapi import APIRouter

job_router: APIRouter = APIRouter(prefix="/job")
