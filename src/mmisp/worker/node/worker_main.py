import asyncio
import atexit
import signal
import sys
import types

from mmisp.plugins import loader
from mmisp.worker.node.client_connection_manager import ClientConnectionManager
from mmisp.worker.node.config import node_config
from mmisp.worker.node.queue_manager import (
    all_jobs_pkgs,
    get_currently_listened_queues,
    start_all_workers,
    start_worker,
    stop_all_workers,
    stop_worker,
)


def handle_signal(signum: int, frame: types.FrameType | None) -> None:
    sys.exit(0)


atexit.register(stop_all_workers)
signal.signal(signal.SIGINT, handle_signal)
signal.signal(signal.SIGTERM, handle_signal)

client = ClientConnectionManager()


async def pong(data: dict) -> None:
    await client.send_msg_nowait("pong", data["conversation_id"])


async def currently_listened_queues(data: dict) -> None:
    ans = get_currently_listened_queues()
    await client.send_msg_nowait(ans, data["conversation_id"])


async def add_queue(data: dict) -> None:
    start_worker(data["queue_name"])
    await client.send_msg_nowait("Ok", data["conversation_id"])


async def remove_queue(data: dict) -> None:
    stop_worker(data["queue_name"])
    await client.send_msg_nowait("Ok", data["conversation_id"])


async def remove_all_queues(data: dict) -> None:
    stop_all_workers()
    await client.send_msg_nowait("Ok", data["conversation_id"])


async def reset_queues(data: dict) -> None:
    queues = get_currently_listened_queues()
    should = node_config.workers if node_config.workers != ["ALL"] else all_jobs_pkgs

    for q in queues:
        if q not in should:
            stop_worker(q)
    for q in should:
        if q not in queues:
            start_worker(q)

    await client.send_msg_nowait("Ok", data["conversation_id"])


client.dispatch["ping"] = pong
client.dispatch["currently_listened_queues"] = currently_listened_queues
client.dispatch["add_queue"] = add_queue
client.dispatch["remove_queue"] = remove_queue
client.dispatch["remove_all_queues"] = remove_all_queues
client.dispatch["reset_queues"] = reset_queues


def main() -> None:
    asyncio.run(client.try_connect())
    if node_config.correlation_plugin_dir is not None:
        loader.load_plugins_from_directory(*node_config.correlation_plugin_dir)
    if node_config.enrichment_plugin_dir is not None:
        loader.load_plugins_from_directory(*node_config.enrichment_plugin_dir)
    if "ALL" in node_config.workers:
        start_all_workers()
    else:
        for job in node_config.workers:
            start_worker(job)

    asyncio.run(client.connect())


if __name__ == "__main__":
    main()
