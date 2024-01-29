from mmisp.worker.misp_database.misp_api import MispAPI


def run():
    misp_api: MispAPI = MispAPI()
    print(misp_api.get_event_attribute(3))
    print(misp_api.get_event(10))
