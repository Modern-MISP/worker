import uvicorn
from fastapi import FastAPI

import mmisp.worker.jobs.all_jobs  # noqa
from mmisp.worker.api.job_router import job_router
from mmisp.worker.api.worker_router import worker_router
from mmisp.worker.config import SystemConfigData, system_config_data

"""
The main module of the MMISP Worker application.
"""


"""setup logging"""
# logging.basicConfig(level=logging.DEBUG)


def init_app(*, init_db: bool = True) -> FastAPI:
    lifespan = None  # type: ignore
    if init_db:
        pass
        #        sessionmanager.init()
        #
        #        @asynccontextmanager
        #        async def lifespan(app: FastAPI) -> AsyncGenerator:
        #            await sessionmanager.create_all()
        #            yield
        #            if sessionmanager._engine is not None:
        #                await sessionmanager.close()

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
