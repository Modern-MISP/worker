import json
import logging
from typing import Self
from uuid import UUID

import requests
from requests import PreparedRequest, Request, Response, Session, TooManyRedirects, codes
from sqlalchemy.ext.asyncio import AsyncSession

from mmisp.api_schemas.attributes import (
    AddAttributeBody,
    GetAttributeAttributes,
    GetAttributeResponse,
    SearchAttributesAttributesDetails,
    SearchAttributesBody,
    SearchAttributesResponse,
)
from mmisp.api_schemas.events import AddEditGetEventDetails
from mmisp.api_schemas.objects import ObjectResponse, ObjectWithAttributesResponse
from mmisp.api_schemas.server import Server
from mmisp.api_schemas.sharing_groups import (
    GetAllSharingGroupsResponse,
    GetAllSharingGroupsResponseResponseItem,
    ViewUpdateSharingGroupLegacyResponse,
)
from mmisp.api_schemas.tags import TagCreateBody
from mmisp.api_schemas.users import GetUsersElement
from mmisp.lib.distribution import AttributeDistributionLevels
from mmisp.util.uuid import uuid
from mmisp.worker.exceptions.misp_api_exceptions import APIException, InvalidAPIResponse
from mmisp.worker.misp_database import misp_api_utils
from mmisp.worker.misp_database.misp_api_config import MispAPIConfigData, misp_api_config_data
from mmisp.worker.misp_database.misp_sql import get_api_authkey
from mmisp.worker.misp_dataclasses.misp_user import MispUser

_log = logging.getLogger(__name__)


class MispAPI:
    """
    This class is used to communicate with the MISP API.

    it encapsulates the communication with the MISP API and provides methods to retrieve and send data.
    the data is parsed and validated by the MispAPIParser and MispAPIUtils classes,
    and returns the data as MMISP dataclasses.
    """

    __HEADERS: dict = {"Accept": "application/json", "Content-Type": "application/json", "Authorization": ""}
    __LIMIT: int = 1000

    def __init__(self: Self, db: AsyncSession) -> None:
        self.__config: MispAPIConfigData = misp_api_config_data
        self._db = db

    def __setup_api_session(self: Self) -> Session:
        """
        This method is used to set up the session for the API.

        :return:  returns the session that was set up
        :rtype: Session
        """
        print("Auth Key is:", self.__config.key)
        if not self.__config.key:
            raise ValueError("Authorization cannot be empty")

        session = Session()
        session.headers.update(self.__HEADERS)
        session.headers.update({"Authorization": f"{self.__config.key}"})
        return session

    async def __setup_remote_api_session(self: Self, server_id: int) -> Session:
        """
        This method is used to set up the session for the remote API.

        :param server_id: server id of the remote server to set up the session for
        :type server_id: int
        :return: returns the session to the specified server that was set up
        :rtype: Session
        """

        key: str | None = await get_api_authkey(self._db, server_id)
        if key is None:
            raise APIException(f"API key for server {server_id} is not available.")

        session = Session()
        session.headers.update(self.__HEADERS)
        session.headers.update({"Authorization": f"{key}"})
        return session

    async def __get_session(self: Self, server: Server | None = None) -> Session:
        """
        This method is used to get the session for the given server_id
        if a session for the given server_id already exists, it returns the existing session,
        otherwise it sets up a new session and returns it.

        :param server: server to get the session for, if no server is given, the own API is used
        :type server: Server
        :return: returns a session to the specified server
        :rtype: Session
        """

        server_id: int = server.id if server is not None else 0
        if server_id == 0:
            return self.__setup_api_session()
        else:
            return await self.__setup_remote_api_session(server_id)

    def __get_url(self: Self, path: str, server: Server | None = None) -> str:
        """
        This method is used to get the url for the given server, adding the given path to the url.

        if no server is given, it uses the default url from the config,
        otherwise it uses the url of the given server.

        :param path: path to add to the url
        :type path: str
        :param server: remote server to get the url for
        :type server: Server
        :return: returns the url for the given server with the path added
        :rtype: str
        """
        url: str
        if server:
            url = server.url
        else:
            if self.__config.url.endswith("/"):
                url = self.__config.url[:-1]
            else:
                url = self.__config.url

        return self.__join_path(url, path)

    @staticmethod
    def __join_path(url: str, path: str) -> str:
        """
        This method is used to join the given path to the given url.
        it checks if the path starts with a slash, if it does not, it also adds a slash to the url.

        :param url: url to join the path to
        :type url: str
        :param path: path to join to the url
        :type path: str
        :return: returns the url with the path added
        :rtype: str
        """

        if path.startswith("/"):
            return url + path
        else:
            return f"{url}/{path}"

    async def __send_request(self: Self, request: PreparedRequest, server: Server | None = None, **kwargs) -> dict:
        """
        This method is used to send the given request and return the response.

        :param request: the request to send
        :type request: PreparedRequest
        :param kwargs: keyword arguments
        :type kwargs: dict[str, Any]
        :return: returns the response of the request
        :rtype: dict
        """
        print("Request is: ", request)
        print(request.method)
        print(request.headers)
        print(request.url)
        if request.method == "POST":
            print(request.body)
        response: Response

        if "timeout" not in kwargs:
            kwargs["timeout"] = (self.__config.connect_timeout, self.__config.read_timeout)

        try:
            response = (await self.__get_session(server)).send(request, **kwargs)
        except (ConnectionError, TimeoutError, TooManyRedirects) as api_exception:
            _log.warning(f"API not available. The request could not be made. ==> {api_exception}")
            raise APIException(f"API not available. The request could not be made. ==> {api_exception}")

        try:
            response.raise_for_status()
        except requests.HTTPError as http_err:
            # Füge hier eine detaillierte Fehlerausgabe hinzu
            error_details = (
                f"HTTP Error occurred: {http_err}\n"
                f"URL: {request.url}\n"
                f"Status Code: {response.status_code}\n"
                f"Response Text: {response.text}\n"
                f"Headers: {response.headers}"
            )
            _log.error(error_details)
            raise APIException(error_details) from http_err

        if response.status_code != codes.ok:
            raise requests.HTTPError(response, response.text)

        return misp_api_utils.decode_json_response(response)

    async def get_user(self: Self, user_id: int, server: Server | None = None) -> MispUser:
        """
        Returns the user with the given user_id.

        :param user_id: id of the user
        :type user_id: int
        :param server: the server to get the user from, if no server is given, the own API is used
        :type server: Server
        :return: returns the user with the given user_id
        :rtype: MispUser
        """
        url: str = self.__get_url(f"/admin/users/view/{user_id}", server)

        request: Request = Request("GET", url)
        prepared_request: PreparedRequest = (await self.__get_session(server)).prepare_request(request)
        response: dict = await self.__send_request(prepared_request, server)
        get_user_element_responds: GetUsersElement = GetUsersElement.model_validate(response)
        user_dict: dict = get_user_element_responds.User.model_dump()
        user_dict["role"] = get_user_element_responds.Role.model_dump()

        try:
            return MispUser.model_validate(user_dict)
        except ValueError as value_error:
            raise InvalidAPIResponse(f"Invalid API response. MISP user could not be parsed: {value_error}")

    async def get_object(self: Self, object_id: int, server: Server | None = None) -> ObjectWithAttributesResponse:
        """
        Returns the object with the given object_id.

        :param object_id:  id of the object
        :type object_id: int
        :param server: the server to get the object from, if no server is given, the own API is used
        :type server: Server
        :return: The object
        :rtype: ObjectWithAttributesResponse
        """
        if object_id == 0:
            #  for correlation to give back an empty object
            return ObjectWithAttributesResponse(
                id=0, uuid="", name="", distribution=AttributeDistributionLevels.OWN_ORGANIZATION, sharing_group_id=0
            )

        url: str = self.__get_url(f"objects/view/{object_id}", server)

        request: Request = Request("GET", url)
        prepared_request: PreparedRequest = (await self.__get_session(server)).prepare_request(request)
        response: dict = await self.__send_request(prepared_request, server)

        try:
            return ObjectResponse.model_validate(response).Object
        except ValueError as value_error:
            raise InvalidAPIResponse(
                f"Invalid API response. MISP ObjectWithAttributesResponse could not be parsed: {value_error}"
            )

    async def get_sharing_group(
        self: Self, sharing_group_id: int, server: Server | None = None
    ) -> ViewUpdateSharingGroupLegacyResponse:
        """
        Returns the sharing group with the given sharing_group_id

        :param sharing_group_id: id of the sharing group to get from the API
        :type sharing_group_id: int
        :param server: the server to get the sharing group from, if no server is given, the own API is used
        :type server: Server
        :return: returns the sharing group that got requested
        :rtype: ViewUpdateSharingGroupLegacyResponse
        """

        url: str = self.__get_url(f"/sharing_groups/view/{sharing_group_id}", server)
        request: Request = Request("GET", url)
        prepared_request: PreparedRequest = (await self.__get_session(server)).prepare_request(request)
        response: dict = await self.__send_request(prepared_request, server)
        try:
            return ViewUpdateSharingGroupLegacyResponse.parse_obj(response)
        except ValueError as value_error:
            raise InvalidAPIResponse(
                f"Invalid API response. MISP ViewUpdateSharingGroupLegacyResponse could not be parsed: {value_error}"
            )

    async def get_event(self: Self, event_id: int | UUID, server: Server | None = None) -> AddEditGetEventDetails:
        """
        Returns the event with the given event_id from the given server,
         the own API is used if no server is given.

        :param event_id: the id of the event to get
        :type event_id: int
        :param server: the server to get the event from, if no server is given, the own API is used
        :type server: Server
        :return: returns the event with the given event_id from the given server
        :rtype: AddEditGetEventDetails
        """
        url: str = self.__get_url(f"/events/view/{event_id}", server)
        request: Request = Request("GET", url)
        prepared_request: PreparedRequest = (await self.__get_session(server)).prepare_request(request)
        response: dict = await self.__send_request(prepared_request, server)
        try:
            return AddEditGetEventDetails.parse_obj(response["Event"])
        except ValueError as value_error:
            raise InvalidAPIResponse(
                f"Invalid API response. AddEditGetEventDetails"
                f"{json.dumps(response['Event'])} could not be parsed: {value_error}"
            )

    async def get_sharing_groups(
        self: Self, server: Server | None = None
    ) -> list[GetAllSharingGroupsResponseResponseItem]:
        """
        Returns all sharing groups from the given server, if no server is given, the own API is used.

        :param server: the server to get the sharing groups from, if no server is given, the own API is used
        :type server: Server
        :return: returns all sharing groups from the given server
        :rtype: list[GetAllSharingGroupsResponseResponseItem]
        """
        url: str = self.__get_url("/sharing_groups", server)

        request: Request = Request("GET", url)
        prepared_request: PreparedRequest = (await self.__get_session(server)).prepare_request(request)
        response: dict = await self.__send_request(prepared_request, server)
        print(f"get_sharing_groups: response={response}")

        try:
            return GetAllSharingGroupsResponse.parse_obj(response).response
        except ValueError as value_error:
            raise InvalidAPIResponse(f"Invalid API response. MISP Sharing Group could not be parsed: {value_error}")

    async def get_attribute(self: Self, attribute_id: int, server: Server | None = None) -> GetAttributeAttributes:
        """
        Returns the attribute with the given attribute_id.

        :param attribute_id: the id of the attribute to get
        :type attribute_id: int
        :param server: the server to get the attribute from, if no server is given, the own API is used
        :type server: Server
        :return: returns the attribute with the given attribute_id
        :rtype: GetAttributeAttributes
        """

        url: str = self.__get_url(f"/attributes/{attribute_id}", server)

        request: Request = Request("GET", url)
        prepared_request: PreparedRequest = (await self.__get_session(server)).prepare_request(request)
        response: dict = await self.__send_request(prepared_request, server)

        try:
            return GetAttributeResponse.parse_obj(response).Attribute
        except ValueError as value_error:
            raise InvalidAPIResponse(f"Invalid API response. MISP Attribute could not be parsed: {value_error}")

    async def get_event_attributes(
        self: Self, event_id: int, server: Server | None = None
    ) -> list[SearchAttributesAttributesDetails]:
        """
        Returns all attribute object of the given event, represented by given event_id.

        :param event_id: of the event
        :type event_id: int
        :param server: the server to get the attribute from, if no server is given, the own API is used
        :type server: Server
        :return: a list of all attributes
        :rtype: list[SearchAttributesAttributesDetails]
        """

        url: str = self.__get_url("/attributes/restSearch", server)
        body: SearchAttributesBody = SearchAttributesBody(
            eventid=event_id, with_attachments=True, include_event_uuid=True
        )
        request: Request = Request("POST", url, json=body.model_dump(mode="json"))
        prepared_request: PreparedRequest = (await self.__get_session(server)).prepare_request(request)
        response: dict = await self.__send_request(prepared_request, server)

        try:
            return SearchAttributesResponse.model_validate(response).response.Attribute
        except ValueError as value_error:
            raise InvalidAPIResponse(f"Invalid API response. Event Attributes could not be parsed: {value_error}")

    async def create_attribute(self: Self, attribute: AddAttributeBody, server: Server | None = None) -> int:
        """
        creates the given attribute on the server

        :param attribute: contains the required attributes to creat an attribute
        :type attribute: AddAttributeBody
        :param server: the server to create the attribute on, if no server is given, the own API is used
        :type server: Server
        :return: The attribute id if the creation was successful. -1 otherwise.
        :rtype: int
        """
        if attribute.uuid is None:
            attribute.uuid = uuid()

        if attribute.deleted is None:
            attribute.deleted = False

        url: str = self.__get_url(f"/attributes/add/{attribute.event_id}", server)

        request: Request = Request("POST", url, json=attribute.model_dump(mode="json"))
        prepared_request: PreparedRequest = (await self.__get_session(server)).prepare_request(request)
        response: dict = await self.__send_request(prepared_request, server)
        if "Attribute" in response:
            return int(response["Attribute"]["id"])

        return -1

    async def create_tag(self: Self, tag: TagCreateBody, server: Server | None = None) -> int:
        """
        Creates the given tag on the server
        :param tag: The tag to create.
        :type tag: TagCreateBody
        :param server: The server to create the tag on. If no server is given, the own MMISP-API Server is used.
        :type server: Server
        :return: the id of the created tag
        :rtype: int
        """

        url: str = self.__get_url("/tags/add", server)
        request: Request = Request("POST", url, json=tag.model_dump(mode="json"))
        prepared_request: PreparedRequest = (await self.__get_session(server)).prepare_request(request)

        response: dict = await self.__send_request(prepared_request, server)
        return int(response["Tag"]["id"])

    async def attach_attribute_tag(
        self: Self, attribute_id: int, tag_id: int, local: bool, server: Server | None = None
    ) -> bool:
        """
        Attaches a tag to an attribute

        :param attribute_id: The ID of the attribute.
        :type attribute_id: int
        :param tag_id: The ID of the tag.
        :type tag_id: int
        :param local: If the tag is to be attached only locally.
        :type local: bool
        :param server: the server to attach the tag to the attribute on, if no server is given, the own API is used
        :type server: Server
        :return: true if the attachment was successful
        :rtype: bool
        """

        url: str = self.__get_url(
            f"/attributes/addTag/{attribute_id}/{tag_id}/local:{local}",
            server,
        )
        request: Request = Request("POST", url)
        prepared_request: PreparedRequest = (await self.__get_session(server)).prepare_request(request)
        await self.__send_request(prepared_request, server)

        return True

    async def attach_event_tag(
        self: Self, event_id: int, tag_id: int, local: bool, server: Server | None = None
    ) -> bool:
        """
        Attaches a tag to an event

        :param event_id: The ID of the event.
        :type event_id: int
        :param tag_id: The ID of the tag.
        :type tag_id: int
        :param local: If the tag is to be attached only locally.
        :type local: bool
        :param server: the server to attach the tag to the event on, if no server is given, the own API is used
        :type server: Server
        :return:
        :rtype: bool
        """

        url: str = self.__get_url(f"/events/addTag/{event_id}/{tag_id}/local:{local}", server)
        request: Request = Request("POST", url)
        prepared_request: PreparedRequest = (await self.__get_session(server)).prepare_request(request)

        await self.__send_request(prepared_request, server)
        return True

    async def modify_event_tag_relationship(
        self: Self, event_tag_id: int, relationship_type: str, server: Server | None = None
    ) -> bool:
        """
        Modifies the relationship of the given tag to the given event
        Endpoint documented at: https://www.misp-project.org/2022/10/10/MISP.2.4.164.released.html/

        :param event_tag_id: The ID of the event-tag assignment.
        :type event_tag_id: int
        :param relationship_type: The relationship type to set.
        :type relationship_type: str
        :param server: the server to modify the relationship on, if no server is given, the own API is used
        :type server: Server
        :return: returns true if the modification was successful
        :rtype: bool
        """

        url: str = self.__get_url(f"/tags/modifyTagRelationship/event/{event_tag_id}", server)
        body: dict = {"Tag": {"relationship_type": relationship_type}}

        request: Request = Request("POST", url, json=body)
        prepared_request: PreparedRequest = (await self.__get_session(server)).prepare_request(request)

        response: dict = await self.__send_request(prepared_request, server)
        print(response)
        return response["saved"] == "true" and response["success"] == "true"

    async def modify_attribute_tag_relationship(
        self: Self, attribute_tag_id: int, relationship_type: str, server: Server | None = None
    ) -> bool:
        """
        Modifies the relationship of the given tag to the given attribute
        Endpoint documented at: https://www.misp-project.org/2022/10/10/MISP.2.4.164.released.html/

        :param attribute_tag_id: The ID of the attribute-tag assignment.
        :type attribute_tag_id: int
        :param relationship_type: The relationship type to set.
        :type relationship_type: str
        :param server: the server to modify the relationship on, if no server is given, the own API is used
        :type server: Server
        :return: returns true if the modification was successful
        :rtype: bool
        """

        url: str = self.__get_url(f"/tags/modifyTagRelationship/attribute/{attribute_tag_id}", server)
        body = {"Tag": {"relationship_type": relationship_type}}

        request: Request = Request("POST", url, json=body)
        prepared_request: PreparedRequest = (await self.__get_session(server)).prepare_request(request)

        response: dict = await self.__send_request(prepared_request, server)
        print(f"bananenbieger: modify_attribute_tag_relationship: response={response}")
        return response["saved"] is True and response["success"] is True
