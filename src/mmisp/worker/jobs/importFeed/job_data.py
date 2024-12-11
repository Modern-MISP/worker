from pydantic import BaseModel

from mmisp.worker.jobs.processfreetext.attribute_types.attribute_type import AttributeType


class ImportFeedData(BaseModel):
    """Represents the input data for the ImportFeedJob.

    This class is used to store and validate the data provided for the ImportFeedJob. It contains
    the id that points to the feed to be imported. The `id` attribute is an integer of a feed in the database.

    Attributes:
        id (int): Id of the feed to be imported.
    """

    id: int


class ImportFeedResponse(BaseModel):
    """Represents the response of the ImportFeedJob.

    This class is used to represent the result of the ImportFeedJob. It contains information
    about the success of the operation and a list of attributes that were extracted during the import process.

    Attributes:
        success (bool): A boolean value indicating whether the feed import was successful.
        attributes (list[AttributeType]): A list of attributes extracted from the imported feed.
    """

    success: bool
    attributes: list[AttributeType]
