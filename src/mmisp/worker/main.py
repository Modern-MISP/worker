import logging

import uvicorn
from fastapi import FastAPI

from mmisp.worker.api.job_router import job_router
from mmisp.worker.api.worker_router import worker_router
from mmisp.worker.api.worker_router.input_data import WorkerEnum
from mmisp.worker.config.system_config_data import SystemConfigData, system_config_data
from mmisp.worker.controller.worker_controller import WorkerController

"""
The main module of the MMISP Worker application.
"""

app: FastAPI = FastAPI()
"""The FastAPI instance."""

app.include_router(job_router.job_router)
app.include_router(worker_router.worker_router)

"""setup logging"""
logging.basicConfig(level=logging.DEBUG)




def main():
    """
    The entry point of the MMISP Worker application.
    Starts the enabled workers and sets up the API.
    """

    config: SystemConfigData = system_config_data

    for worker in WorkerEnum:
        if config.is_autostart_for_worker_enabled(worker):
            WorkerController.enable_worker(worker)

    uvicorn.run(f"{__name__}:app", port=int(config.api_port), log_level="info", host=config.api_host)


if __name__ == "__main__":
    main()
