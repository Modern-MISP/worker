# import os

# from mmisp.worker.config import ENV_PREFIX
# from mmisp.worker.controller.celery_client import celery_app
# from mmisp.worker.jobs.correlation.plugins.correlation_plugin_factory import correlation_plugin_factory
# from mmisp.worker.jobs.enrichment.plugins.enrichment_plugin_factory import enrichment_plugin_factory
# from mmisp.worker.plugins.loader import PluginLoader

import asyncio
import json

import websockets

MASTER_URL = "ws://localhost:8000/worker/ws"
MASTER_KEY = "worker-client-secret"

header = {"Authorization": f"Bearer {MASTER_KEY}"}


subprocesses = {}


async def listen_and_act():
    async with websockets.connect(MASTER_URL, additional_headers=header) as websocket:
        print("Connected to master.")
        while True:
            message = await websocket.recv()
            command = json.loads(message)
            print(f"[Master] {message}")

            if message == "start":
                # Start a subprocess (e.g., dummy worker.py or echo)
                print("Starting subprocess...")
                proc = await asyncio.create_subprocess_exec("python", "-c", "print('hello from worker')")

                await proc.wait()
                await websocket.send("Subprocess done.")

            elif message == "ping":
                await websocket.send("pong")


def main() -> None:
    asyncio.run(listen_and_act())


if __name__ == "__main__":
    asyncio.run(listen_and_act())


# def main() -> None:
#    # load enrichment plugins
#    enrichment_plugin_env = f"{ENV_PREFIX}_ENRICHMENT_PLUGIN_DIRECTORY"
#    correlation_plugin_dir = os.environ.get(enrichment_plugin_env, None)
#    if correlation_plugin_dir is not None:
#        PluginLoader.load_plugins_from_directory(correlation_plugin_dir, enrichment_plugin_factory)
#
#    # load correlation plugins
#    correlation_plugin_env = f"{ENV_PREFIX}_CORRELATION_PLUGIN_DIRECTORY"
#    correlation_plugin_dir = os.environ.get(correlation_plugin_env, None)
#    if correlation_plugin_dir is not None:
#        PluginLoader.load_plugins_from_directory(correlation_plugin_dir, correlation_plugin_factory)
#
#    worker = celery_app.Worker()
#    worker.start()  # type: ignore
#
#
# if __name__ == "__main__":
# V    main()
