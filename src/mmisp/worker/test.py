import pprint
import uuid

from mmisp.worker.misp_database.misp_api import MispAPI
from mmisp.worker.misp_dataclasses.misp_event_attribute import MispEventAttribute


def run():
    misp_api: MispAPI = MispAPI()
    printer = pprint.PrettyPrinter(width=20)

    # Chris
    print('\n######## Chris #########\n')
    try:
        respone:dict =misp_api.create_attribute(MispEventAttribute(id=272745,
                                                                    event_id=2,
                                                                    object_id=0,
                                                                    object_relation=None,
                                                                    category="Internal reference",
                                                                    type="hex",
                                                                    value1=12345678900,
                                                                    value2="filler",
                                                                    to_ids=False,
                                                                    uuid=str(uuid.uuid4()),
                                                                    timestamp=1706092974,
                                                                    distribution=0,
                                                                    sharing_group_id=0,
                                                                    comment="filler",
                                                                    deleted=False,
                                                                    disable_correlation=False,
                                                                    first_seen=None,
                                                                    last_seen=None,
                                                                    value="12345678900"))
        printer.pprint(respone)
    except Exception as exception:
        print("failed")
        print(exception)

    """
    # Amadeus
    print('\n######## Amadeus #########\n')
    try:
        # print(misp_api.get_event(10))
        attribute: MispEventAttribute = misp_api.get_event_attribute(272598)
        printer.pprint(attribute)
    except Exception as exception:
        print(exception)
    """

if __name__ == '__main__':
    run()
