import importlib.resources
import subprocess

worker_queue: dict[str, subprocess.Popen] = {}
jobs_pkg = "mmisp.worker.jobs"
all_jobs_pkgs = list(
    i.name
    for i in importlib.resources.files(jobs_pkg).iterdir()
    if i.is_dir() and all([i.joinpath("__init__.py").is_file(), i.joinpath("worker.py").is_file()])
)


def stop_worker(name: str) -> None:
    if name in worker_queue:
        if worker_queue[name].poll() is None:
            process = worker_queue[name]
            print("Process is still running")
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print(f"Timeout wait for process {name}, killing")
                process.kill()
        else:
            print("Process already terminated")
            worker_queue.pop(name)
    else:
        print("No process in dict")


def get_currently_listened_queues() -> list[str]:
    for name in list(worker_queue.keys()):
        if worker_queue[name].poll() is not None:
            worker_queue.pop(name)
    return list(worker_queue.keys())


def start_worker(name: str) -> None:
    if name not in all_jobs_pkgs:
        print("start_worker Name not valid")
        return

    if name in worker_queue:
        print("Already process in dict, check running")
        if worker_queue[name].poll() is None:
            print("Process is still running")
        else:
            print("Process terminated, starting again")
            worker_queue.pop(name)
            start_worker(name)
    else:
        print("Starting streaq for", name)
        module_name = f"{jobs_pkg}.{name}.worker.queue"
        worker_queue[name] = subprocess.Popen(["streaq", module_name])


def start_all_workers() -> None:
    for job in all_jobs_pkgs:
        start_worker(job)


def stop_all_workers() -> None:
    for name in list(worker_queue.keys()):
        stop_worker(name)
