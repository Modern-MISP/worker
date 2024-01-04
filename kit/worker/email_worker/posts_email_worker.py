from kit.worker.worker import Worker


class PostsEmailWorker(Worker):

    def run(self, event_id: int, post_id: int, title: str, message: str):
        pass
