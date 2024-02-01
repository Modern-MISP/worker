import pprint
import uuid

from mmisp.worker.misp_database.misp_api import MispAPI



def run():
    misp_api: MispAPI = MispAPI()
    printer = pprint.PrettyPrinter(width=20)


    # Amadeus
    print('\n######## Amadeus #########\n')
    try:
        # print(misp_api.get_event(10))
        #attribute: MispEventAttribute = misp_api.get_event_attribute(272598)
        printer.pprint(attribute)
    except Exception as exception:
        print(exception)



if __name__ == '__main__':
    run()
