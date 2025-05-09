from collections.abc import AsyncGenerator
from contextlib import AsyncExitStack, asynccontextmanager

import uvicorn
from fastapi import FastAPI

import mmisp.worker.jobs.all_jobs  # noqa
from mmisp.worker.api.job_router import job_router
from mmisp.worker.api.worker_router import worker_router
from mmisp.worker.config import SystemConfigData, system_config_data
from mmisp.worker.jobs.all_queues import all_queues

"""
The main module of the MMISP Worker application.
"""


"""setup logging"""
# logging.basicConfig(level=logging.DEBUG)


def init_app(*, init_db: bool = True) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator:
        async with AsyncExitStack() as stack:
            for q in all_queues.values():
                await stack.enter_async_context(q)
            yield

    app: FastAPI = FastAPI(lifespan=lifespan)

    app.include_router(job_router)
    app.include_router(worker_router)

    return app


def main() -> None:
    """
    The entry point of the MMISP Worker application.
    Starts the enabled workers and sets up the API.
    """

    config: SystemConfigData = system_config_data

    uvicorn.run(f"{__name__}:app", port=int(config.api_port), log_level="info", host=config.api_host)


app = init_app()
"""The FastAPI instance."""

if __name__ == "__main__":
    main()
