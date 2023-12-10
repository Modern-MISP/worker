from fastapi import FastAPI

from api.job_router import job_router
from api.worker_router import worker_router

app: FastAPI = FastAPI()
app.include_router(job_router.router)
app.include_router(worker_router.router)
