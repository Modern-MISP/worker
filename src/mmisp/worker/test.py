import pprint

from mmisp.worker.misp_database.misp_api import MispAPI
from mmisp.worker.misp_dataclasses.misp_attribute import MispEventAttribute


def run():
    misp_api: MispAPI = MispAPI()
    printer = pprint.PrettyPrinter(width=20)

    # Chris
    print('\n######## Chris #########\n')
    try:
        printer.pprint(misp_api.get_sharing_group(1))
    except Exception as exception:
        print(exception)

    # Amadeus
    print('\n######## Amadeus #########\n')
    try:
        #print(misp_api.get_event(10))
        attribute: MispEventAttribute = misp_api.get_event_attribute(272598)
        print(attribute.tags)
        printer.pprint(attribute)
    except Exception as exception:
        print(exception)


if __name__ == '__main__':
    run()