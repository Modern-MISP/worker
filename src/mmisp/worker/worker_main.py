from mmisp.worker.controller.celery_client import celery_app


def main() -> None:
    worker = celery_app.Worker()
    worker.start()


if __name__ == "__main__":
    main()
