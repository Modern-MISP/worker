import uvicorn
from fastapi import FastAPI

from mmisp.worker.api.job_router import job_router
from mmisp.worker.api.worker_router import worker_router

app: FastAPI = FastAPI()
app.include_router(job_router.job_router)
app.include_router(worker_router.worker_router)


def main():
    uvicorn.run("main:app", port=5000, log_level="info")


if __name__ == "__main__":
    main()