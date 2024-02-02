import pprint
import uuid

from mmisp.worker.misp_database.misp_api import MispAPI
from mmisp.worker.misp_database.misp_sql import MispSQL
from mmisp.worker.misp_dataclasses.misp_post import MispPost


def run():
    misp_api: MispAPI = MispAPI()
    printer = pprint.PrettyPrinter(width=20)


    # Amadeus
    print('\n######## Amadeus #########\n')
    try:
        database: MispSQL = MispSQL()
        post: MispPost = database.get_post(3)
        printer.pprint(post)
    except Exception as exception:
        print(exception)



if __name__ == '__main__':
    run()
