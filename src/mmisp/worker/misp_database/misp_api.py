import json
import logging
from datetime import datetime, timedelta
from typing import List, Self
from uuid import UUID

import requests
from fastapi.encoders import jsonable_encoder
from requests import PreparedRequest, Request, Response, Session, TooManyRedirects, codes

from mmisp.api_schemas.attributes import (
    AddAttributeBody,
    GetAttributeAttributes,
    GetAttributeResponse,
    SearchAttributesAttributesDetails,
    SearchAttributesResponse, SearchAttributesBody,
)
from mmisp.api_schemas.events import AddEditGetEventDetails, IndexEventsBody
from mmisp.api_schemas.galaxies import GetGalaxyClusterResponse
from mmisp.api_schemas.objects import ObjectWithAttributesResponse
from mmisp.api_schemas.server import Server, ServerVersion
from mmisp.api_schemas.shadow_attribute import ShadowAttribute
from mmisp.api_schemas.sharing_groups import (
    GetAllSharingGroupsResponse,
    GetAllSharingGroupsResponseResponseItem,
    ViewUpdateSharingGroupLegacyResponse,
)
from mmisp.api_schemas.sightings import SightingAttributesResponse
from mmisp.api_schemas.tags import TagCreateBody
from mmisp.api_schemas.users import UsersViewMeResponse
from mmisp.worker.exceptions.misp_api_exceptions import APIException, InvalidAPIResponse
from mmisp.worker.misp_database import misp_api_utils
from mmisp.worker.misp_database.misp_api_config import MispAPIConfigData, misp_api_config_data
from mmisp.worker.misp_database.misp_sql import get_api_authkey
from mmisp.worker.misp_dataclasses.misp_minimal_event import MispMinimalEvent
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

    def __init__(self: Self) -> None:
        self.__config: MispAPIConfigData = misp_api_config_data

    def __setup_api_session(self: Self) -> Session:
        """
        This method is used to set up the session for the API.

        :return:  returns the session that was set up
        :rtype: Session
        """

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

        key: str | None = await get_api_authkey(server_id)
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

        response: Response

        if "timeout" not in kwargs:
            kwargs["timeout"] = (self.__config.connect_timeout, self.__config.read_timeout)

        try:
            response = (await self.__get_session(server)).send(request, **kwargs)
        except (ConnectionError, TimeoutError, TooManyRedirects) as api_exception:
            _log.warning(f"API not available. The request could not be made. ==> {api_exception}")
            raise APIException(f"API not available. The request could not be made. ==> {api_exception}")

        if response.status_code != codes.ok:
            raise requests.HTTPError(response, response.json())

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
        user_view_me_responds: UsersViewMeResponse = UsersViewMeResponse.parse_obj(response)
        user_dict: dict = user_view_me_responds.dict()
        user_dict["Role"] = user_view_me_responds.Role

        try:
            return MispUser.parse_obj(user_dict)
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
            return ObjectWithAttributesResponse(id=0, uuid="", name="", distribution=0, sharing_group_id=0)

        url: str = self.__get_url(f"objects/view/{object_id}", server)

        request: Request = Request("GET", url)
        prepared_request: PreparedRequest = (await self.__get_session(server)).prepare_request(request)
        response: dict = await self.__send_request(prepared_request, server)

        try:
            return ObjectWithAttributesResponse.parse_obj(response)
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

    async def get_server(self: Self, server_id: int) -> Server:
        """
        Returns the server with the given server_id.

        :param server_id: id of the server to get from the API
        :type server_id: int
        :return: returns the server that got requested
        :rtype: Server
        """

        url: str = self.__get_url(f"/servers/index/{server_id}")

        request: Request = Request("GET", url)
        prepared_request: PreparedRequest = (await self.__get_session()).prepare_request(request)
        response: dict = await self.__send_request(prepared_request, None)
        print("bonobo", response)
        try:
            return Server.parse_obj(response[0]["Server"])
        except ValueError as value_error:
            raise InvalidAPIResponse(f"Invalid API response. MISP server could not be parsed: {value_error}")

    async def get_server_version(self: Self, server: Server | None = None) -> ServerVersion:
        """
        Returns the version of the given server

        :param server: the server to get the event from, if no server is given, the own API is used
        :type server:  Server
        :return: returns the version of the given server
        :rtype: ServerVersion
        """
        url: str = self.__get_url("/servers/getVersion", server)
        request: Request = Request("GET", url)
        prepared_request: PreparedRequest = (await self.__get_session(server)).prepare_request(request)
        response: dict = await self.__send_request(prepared_request, server)

        try:
            return ServerVersion.parse_obj(response)
        except ValueError as value_error:
            raise InvalidAPIResponse(f"Invalid API response. Server Version could not be parsed: {value_error}")

    async def get_custom_clusters(
        self: Self, conditions: dict, server: Server | None = None
    ) -> list[GetGalaxyClusterResponse]:
        """
        Returns all custom clusters that match the given conditions from the given server.
        the limit is set as a constant in the class, if the amount of clusters is higher,
        the method will return only the first n clusters.

        :param conditions: the conditions to filter the clusters
        :type conditions:  JsonType
        :param server: the server to get the event from, if no server is given, the own API is used
        :type server: Server
        :return: returns all custom clusters that match the given conditions from the given server
        :rtype: list[GetGalaxyClusterResponse]
        """

        output: list[GetGalaxyClusterResponse] = []
        finished: bool = False
        i: int = 1
        while not finished:
            endpoint_url = "/galaxy_clusters/restSearch" + f"/limit:{self.__LIMIT}/page:{i}"
            url: str = self.__get_url(endpoint_url, server)
            i += 1

            request: Request = Request("POST", url, json=conditions)
            prepared_request: PreparedRequest = (await self.__get_session(server)).prepare_request(request)
            response: dict = await self.__send_request(prepared_request, server)

            for cluster in response["response"]:
                try:
                    output.append(GetGalaxyClusterResponse.parse_obj(cluster))
                except ValueError as value_error:
                    _log.warning(f"Invalid API response. Galaxy Cluster could not be parsed: {value_error}")

            if len(response) < self.__LIMIT:
                finished = True

        return output

    async def get_galaxy_cluster(self: Self, cluster_id: int, server: Server | None = None) -> GetGalaxyClusterResponse:
        """
        Returns the galaxy cluster with the given cluster_id from the given server.

        :param cluster_id: the id of the cluster to get
        :type cluster_id: int
        :param server: the server to get the event from, if no server is given, the own API is used
        :type server: Server
        :return: returns the requested galaxy cluster with the given id from the given server
        :rtype: GetGalaxyClusterResponse
        """

        url: str = self.__get_url(f"/galaxy_clusters/view/{cluster_id}", server)

        request: Request = Request("GET", url)
        prepared_request: PreparedRequest = (await self.__get_session(server)).prepare_request(request)

        response: dict = await self.__send_request(prepared_request, server)

        try:
            return GetGalaxyClusterResponse.parse_obj(response)
        except ValueError as value_error:
            raise InvalidAPIResponse(f"Invalid API response. MISP Event could not be parsed: {value_error}")

    async def get_minimal_events(
        self: Self, ignore_filter_rules: bool, server: Server | None = None
    ) -> list[MispMinimalEvent]:
        """
        Returns all minimal events from the given server.
        if ignore_filter_rules is set to false, it uses the filter rules from the given server to filter the events.
        the limit is set as a constant in the class, if the amount of events is higher,
        the method will return only the first n events.

        :param ignore_filter_rules: boolean to ignore the filter rules
        :type ignore_filter_rules: bool
        :param server: the server to get the event from, if no server is given, the own API is used
        :type server: Server
        :return:    return all minimal events from the given server, capped by the limit
        :rtype: list[MispMinimalEvent]
        """
        if server is None:
            raise ValueError("invalid Server")

        output: list[MispMinimalEvent] = []
        finished: bool = False

        fr: IndexEventsBody
        if not ignore_filter_rules:
            fr = IndexEventsBody.parse_obj(self.__filter_rule_to_parameter(server.pull_rules))

        fr = IndexEventsBody(minimal=1, published=1)

        i: int = 1
        while not finished:
            url: str = self.__get_url("/events/index" + f"/limit:{self.__LIMIT}/page:{i}", server)
            i += 1

            request: Request = Request("POST", url, json=fr.json())
            prepared_request: PreparedRequest = (await self.__get_session(server)).prepare_request(request)
            response: dict = await self.__send_request(prepared_request, server)

            for event_view in response:
                try:
                    output.append(MispMinimalEvent.parse_obj(event_view))
                except ValueError as value_error:
                    _log.warning(f"Invalid API response. Minimal Event could not be parsed: {value_error}")

            if len(response) < self.__LIMIT:
                finished = True

        return output

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
            raise InvalidAPIResponse(f"Invalid API response. AddEditGetEventDetails could not be parsed: {value_error}")

    async def get_sightings_from_event(
        self: Self, event_id: int, server: Server | None = None
    ) -> list[SightingAttributesResponse]:
        """
        Returns all sightings from the given event from the given server.

        :param event_id: id of the event to get the sightings from
        :type event_id: id
        :param server: the server to get the event from, if no server is given, the own API is used
        :type server: Server
        :return: returns all sightings from the given event from the given server
        :rtype: list[SightingAttributesResponse]
        """
        url: str = self.__get_url(f"/sightings/index/{event_id}", server)

        request: Request = Request("GET", url)
        prepared_request: PreparedRequest = (await self.__get_session(server)).prepare_request(request)
        response: dict = await self.__send_request(prepared_request, server)

        out: list[SightingAttributesResponse] = []
        for sighting in response:
            try:
                out.append(SightingAttributesResponse.parse_obj(sighting))
            except ValueError as value_error:
                _log.warning(f"Invalid API response. Sighting could not be parsed: {value_error}")
        return out

    async def get_proposals(self: Self, server: Server | None = None) -> list[ShadowAttribute]:
        """
        Returns all shadow_attributes (proposals) from the given server from the last 90 days.

        :param server: the server to get the proposals from, if no server is given, the own API is used
        :type server: Server
        :return: returns all proposals from the given server from the last 90 days
        :rtype: list[ShadowAttribute]
        """
        if server is None:
            raise ValueError("invalid server")

        d: datetime = datetime.today() - timedelta(days=90)
        timestamp: str = str(datetime.timestamp(d))

        finished: bool = False
        i: int = 1
        out: list[ShadowAttribute] = []

        while not finished:
            param: str = f"/all:1/timestamp:{timestamp}/limit:{self.__LIMIT}/page:{i}/deleted[]:0/deleted[]:1.json"

            #  API Endpoint: https://www.misp-project.org/2019/08/19/MISP.2.4.113.released.html/
            url: str = self.__join_path(server.url, "/shadow_attributes/index" + param)

            request: Request = Request("GET", url)
            prepared_request: PreparedRequest = (await self.__get_session(server)).prepare_request(request)
            response: dict = await self.__send_request(prepared_request, server)

            for proposal in response:
                try:
                    out.append(ShadowAttribute.parse_obj(proposal["ShadowAttribute"]))
                except ValueError as value_error:
                    _log.warning(f"Invalid API response. MISP Proposal could not be parsed: {value_error}")
            if len(response) < self.__LIMIT:
                finished = True

        return out

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
        body: SearchAttributesBody = SearchAttributesBody(eventid=event_id, withAttachments="true",
                                                          includeEventUuid="true")
        request: Request = Request("POST", url, json=body.json())
        prepared_request: PreparedRequest = (await self.__get_session(server)).prepare_request(request)
        response: dict = await self.__send_request(prepared_request, server)

        try:
            return SearchAttributesResponse.parse_obj(response).response.Attribute
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

        url: str = self.__get_url(f"/attributes/add/{attribute.event_id}", server)

        request: Request = Request("POST", url, data=attribute.json())
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
        request: Request = Request("POST", url, data=tag.json())
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
        body: dict = {"Tag": {"relationship_type": relationship_type}}

        request: Request = Request("POST", url, json=body)
        prepared_request: PreparedRequest = (await self.__get_session(server)).prepare_request(request)

        response: dict = await self.__send_request(prepared_request, server)
        return response["saved"] == "true" and response["success"] == "true"

    async def save_cluster(self: Self, cluster: GetGalaxyClusterResponse, server: Server | None = None) -> bool:
        """
        Saves the given cluster on the given server.

        :param cluster: the cluster to save
        :type cluster: GetGalaxyClusterResponse
        :param server: the server to save the cluster on, if no server is given, the own API is used
        :type server: Server
        :return: returns true if the saving was successful
        :rtype: bool
        """

        url: str = self.__get_url(f"/galaxy_clusters/add/{cluster.galaxy_id}", server)
        request: Request = Request("POST", url, json=jsonable_encoder(cluster))
        prepared_request: PreparedRequest = (await self.__get_session(server)).prepare_request(request)

        try:
            await self.__send_request(prepared_request, server)
            return True
        except ValueError as value_error:
            _log.warning(f"Invalid API response. Galaxy Cluster with {cluster.id} could not be saved: {value_error}")
            return False

    async def save_event(self: Self, event: AddEditGetEventDetails, server: Server | None = None) -> bool:
        """
        Saves the given event on the given server.

        :param event: the event to save
        :type event: AddEditGetEventDetails
        :param server: the server to save the event on, if no server is given, the own API is used
        :type server: Server
        :return: returns true if the saving was successful
        :rtype: bool
        """

        url: str = self.__get_url("/events/add", server)
        request: Request = Request("POST", url, json=event.json())
        prepared_request: PreparedRequest = (await self.__get_session(server)).prepare_request(request)

        try:
            await self.__send_request(prepared_request, server)
            return True
        except (APIException, requests.HTTPError):
            return False

    async def update_event(self: Self, event: AddEditGetEventDetails, server: Server | None = None) -> bool:
        """
        Saves the given event on the given server.

        :param event: the event to save
        :type event: AddEditGetEventDetails
        :param server: the server to save the event on, if no server is given, the own API is used
        :type server: Server
        :return: returns true if the saving was successful
        :rtype: bool
        """

        url: str = self.__get_url(f"/events/edit/{event.uuid}", server)
        request: Request = Request("POST", url, json=event.json())
        prepared_request: PreparedRequest = (await self.__get_session(server)).prepare_request(request)

        try:
            await self.__send_request(prepared_request, server)
            return True
        except (APIException, requests.HTTPError):
            return False

    async def save_proposal(self: Self, event: AddEditGetEventDetails, server: Server | None = None) -> bool:
        """
        Saves the given proposal on the given server.

        :param event: the event to save the proposal for
        :type event: AddEditGetEventDetails
        :param server: the server to save the proposal on, if no server is given, the own API is used
        :type server: Server
        :return: returns true if the saving was successful
        :rtype: bool
        """

        url: str = self.__get_url(f"/events/pushProposals/{event.id}", server)
        request: Request = Request("POST", url, json=[sa.dict() for sa in event.ShadowAttribute])
        prepared_request: PreparedRequest = (await self.__get_session(server)).prepare_request(request)

        try:
            await self.__send_request(prepared_request, server)
            return True
        except ValueError:
            return False

    async def save_sighting(self: Self, sighting: SightingAttributesResponse, server: Server | None = None) -> bool:
        """
        Saves the given sighting on the given server.

        :param sighting: the sighting to save
        :type sighting: SightingAttributesResponse
        :param server: the server to save the sighting on, if no server is given, the own API is used
        :type server: Server
        :return: returns true if the saving was successful
        :rtype: bool
        """

        url: str = self.__get_url(f"/sightings/add/{sighting.attribute_id}", server)
        request: Request = Request("POST", url)
        prepared_request: PreparedRequest = (await self.__get_session(server)).prepare_request(request)
        prepared_request.body = sighting.json()

        try:
            await self.__send_request(prepared_request, server)
            return True
        except ValueError as value_error:
            _log.warning(f"Invalid API response. Sighting with id {sighting.id} could not be saved: {value_error}")
            return False

    def __filter_rule_to_parameter(self: Self, filter_rules: str) -> dict[str, list[str]]:
        """
        This method is used to convert the given filter rules string to a dictionary for the API.
        :param filter_rules: the filter rules to convert
        :type filter_rules: dict
        :return: returns the filter rules as a parameter for the API
        :rtype: dict
        """
        out: dict = dict()
        if not filter_rules:
            return out
        url_params = {}

        filter_rules_dict: dict = json.loads(filter_rules)
        for field, rules in filter_rules_dict.items():
            temp: List[str] = []
            if field == "url_params":
                url_params = {} if not rules else json.loads(rules)
            else:
                self.__get_rules(field, out, rules, temp)

        if url_params:
            out.update(url_params)

        return out

    def __get_rules(self: Self, field: str, out: dict, rules: dict, temp: List[str]) -> None:
        for operator, elements in rules.items():
            self.__get_rule(elements, operator, temp)
        if temp:
            out[field[:-1]] = temp

    def __get_rule(self: Self, elements: str, operator: str, temp: List[str]) -> None:
        for k, element in enumerate(elements):
            if operator == "NOT":
                element = "!" + element
            if element:
                temp.append(element)
