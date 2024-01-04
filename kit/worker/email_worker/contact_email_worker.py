from kit.worker.worker import Worker


class ContactEmailWorker(Worker):

    def run(self, event_id: int, message: str, creator_only: bool):
        pass
