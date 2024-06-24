import json
import logging
from datetime import datetime, timedelta
from uuid import UUID

import requests
from fastapi.encoders import jsonable_encoder
from requests import Session, Response, codes, PreparedRequest, Request, TooManyRedirects

from mmisp.api_schemas.attributes import (
    GetAttributeAttributes,
    GetAttributeResponse,
    SearchAttributesAttributesDetails,
    SearchAttributesResponse,
)
from mmisp.api_schemas.sightings import SightingAttributesResponse
from mmisp.api_schemas.tags import TagViewResponse
from mmisp.api_schemas.galaxies import GetGalaxyClusterResponse
from mmisp.api_schemas.objects import ObjectWithAttributesResponse
from mmisp.api_schemas.sharing_groups import (
    ViewUpdateSharingGroupLegacyResponse,
    GetAllSharingGroupsResponseResponseItem,
    GetAllSharingGroupsResponse,
)
from mmisp.api_schemas.users import UsersViewMeResponse
from mmisp.worker.exceptions.misp_api_exceptions import InvalidAPIResponse, APIException
from mmisp.worker.misp_database.misp_api_config import misp_api_config_data, MispAPIConfigData
from mmisp.worker.misp_database.misp_api_utils import MispAPIUtils
from mmisp.worker.misp_database.misp_sql import MispSQL
from mmisp.worker.misp_dataclasses.attribute_tag_relationship import AttributeTagRelationship
from mmisp.worker.misp_dataclasses.event_tag_relationship import EventTagRelationship
from mmisp.api_schemas.events import AddEditGetEventDetails
from mmisp.worker.misp_dataclasses.misp_event_attribute import MispFullAttribute
from mmisp.worker.misp_dataclasses.misp_event_view import MispMinimalEvent
from mmisp.worker.misp_dataclasses.misp_minimal_event import MispMinimalEvent
from mmisp.api_schemas.shadow_attribute import ShadowAttribute
from mmisp.api_schemas.server import Server
from mmisp.api_schemas.server import ServerVersion
from mmisp.worker.misp_dataclasses.misp_user import MispUser

_log = logging.getLogger(__name__)


class TestMispAPI:
    """
    This class is used to communicate with the MISP API.

    it encapsulates the communication with the MISP API and provides methods to retrieve and send data.
    the data is parsed and validated by the MispAPIParser and MispAPIUtils classes,
    and returns the data as MMISP dataclasses.
    """

    __HEADERS: dict = {"Accept": "application/json", "Content-Type": "application/json", "Authorization": ""}
    __LIMIT: int = 1000

    def __init__(self):
        self.__config: MispAPIConfigData = misp_api_config_data
        self.__session: dict[int, Session] = {0: self.__setup_api_session()}
        self.__misp_sql: MispSQL = None

    def __setup_api_session(self) -> Session:
        """
        This method is used to set up the session for the API.

        :return:  returns the session that was set up
        :rtype: Session
        """

        session = Session()
        session.headers.update(self.__HEADERS)
        session.headers.update({"Authorization": f"{self.__config.key}"})
        return session

    def __setup_remote_api_session(self, server_id: int) -> Session:
        """
        This method is used to set up the session for the remote API.

        :param server_id: server id of the remote server to set up the session for
        :type server_id: int
        :return: returns the session to the specified server that was set up
        :rtype: Session
        """

        key: str = "rB2hwhWSISCAuUZpxlQRbmBQebTWGCeE9dB60ljA"

        session = Session()
        session.headers.update(self.__HEADERS)
        session.headers.update({"Authorization": f"{key}"})
        return session

    def __get_session(self, server: Server = None) -> Session:
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
        if server_id in self.__session:
            return self.__session[server_id]
        else:
            session: Session = self.__setup_remote_api_session(server_id)
            self.__session[server_id] = session
            return session

    def __get_url(self, path: str, server: Server = None) -> str:
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

    def __send_request(self, request: PreparedRequest, server: Server = None, **kwargs) -> dict:
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
        timeout: tuple[float, float] | dict
        if "timeout" in kwargs:
            timeout = kwargs["timeout"]
            del kwargs["timeout"]
        else:
            timeout = (self.__config.connect_timeout, self.__config.read_timeout)

        try:
            response = self.__get_session(server).send(request, timeout=timeout, **kwargs)
        except (ConnectionError, TimeoutError, TooManyRedirects) as api_exception:
            _log.warning(f"API not availabe. The request could not be made. ==> {api_exception}")
            raise APIException(f"API not availabe. The request could not be made. ==> {api_exception}")

        if response.status_code != codes.ok:
            raise requests.HTTPError(response, response.json())

        return MispAPIUtils.decode_json_response(response)

    def get_user(self, user_id: int, server: Server = None) -> MispUser:
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
        prepared_request: PreparedRequest = self.__get_session(server).prepare_request(request)
        response: dict = self.__send_request(prepared_request, server)
        user_view_me_responds: UsersViewMeResponse = UsersViewMeResponse.parse_obj(response)

        try:
            return MispUser.parse_obj(user_view_me_responds.User, role=user_view_me_responds.Role)
        except ValueError as value_error:
            raise InvalidAPIResponse(f"Invalid API response. MISP user could not be parsed: {value_error}")

    def get_object(self, object_id: int, server: Server = None) -> ObjectWithAttributesResponse:
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
            return ObjectWithAttributesResponse(id=0, name="", distribution=0, sharing_group_id=0)

        url: str = self.__get_url(f"objects/view/{object_id}", server)

        request: Request = Request("GET", url)
        prepared_request: PreparedRequest = self.__get_session(server).prepare_request(request)
        response: dict = self.__send_request(prepared_request, server)
        try:
            return ObjectWithAttributesResponse.model_validate(response["Object"])
        except ValueError as value_error:
            raise InvalidAPIResponse(
                f"Invalid API response. MISP ObjectWithAttributesResponse could not be parsed: {value_error}"
            )

    def get_sharing_group(self, sharing_group_id: int, server: Server = None) -> ViewUpdateSharingGroupLegacyResponse:
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
        prepared_request: PreparedRequest = self.__get_session(server).prepare_request(request)
        response: dict = self.__send_request(prepared_request, server)
        try:
            return ViewUpdateSharingGroupLegacyResponse.parse_obj(response)
        except ValueError as value_error:
            raise InvalidAPIResponse(
                f"Invalid API response. MISP ViewUpdateSharingGroupLegacyResponse could not be parsed: {value_error}"
            )

    def get_server(self, server_id: int) -> Server:
        """
        Returns the server with the given server_id.

        :param server_id: id of the server to get from the API
        :type server_id: int
        :return: returns the server that got requested
        :rtype: Server
        """

        url: str = self.__get_url(f"/servers/index/{server_id}")

        request: Request = Request("GET", url)
        prepared_request: PreparedRequest = self.__get_session().prepare_request(request)
        response: dict = self.__send_request(prepared_request, None)
        try:
            return Server.parse_obj(response[0]["Server"])
        except ValueError as value_error:
            raise InvalidAPIResponse(f"Invalid API response. MISP server could not be parsed: {value_error}")

    def get_server_version(self, server: Server = None) -> ServerVersion:
        """
        Returns the version of the given server

        :param server: the server to get the event from, if no server is given, the own API is used
        :type server:  Server
        :return: returns the version of the given server
        :rtype: ServerVersion
        """
        url: str = self.__get_url("/servers/getVersion", server)
        request: Request = Request("GET", url)
        prepared_request: PreparedRequest = self.__get_session(server).prepare_request(request)
        response: dict = self.__send_request(prepared_request, server)

        try:
            return ServerVersion.model_validate(response)
        except ValueError as value_error:
            raise InvalidAPIResponse(f"Invalid API response. Server Version could not be parsed: {value_error}")

    def get_custom_clusters(self, conditions: dict, server: Server = None) -> list[GetGalaxyClusterResponse]:
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

            request: Request = Request("POST", url)
            request.body = conditions
            prepared_request: PreparedRequest = self.__get_session(server).prepare_request(request)
            response: dict = self.__send_request(prepared_request, server)

            for cluster in response["response"]:
                try:
                    output.append(GetGalaxyClusterResponse.parse_obj(cluster))
                except ValueError as value_error:
                    _log.warning(f"Invalid API response. Galaxy Cluster could not be parsed: {value_error}")

            if len(response) < self.__LIMIT:
                finished = True

        return output

    def get_galaxy_cluster(self, cluster_id: int, server: Server = None) -> GetGalaxyClusterResponse:
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
        prepared_request: PreparedRequest = self.__get_session(server).prepare_request(request)

        response: dict = self.__send_request(prepared_request, server)

        try:
            return GetGalaxyClusterResponse.parse_obj(response)
        except ValueError as value_error:
            raise InvalidAPIResponse(f"Invalid API response. MISP Event could not be parsed: {value_error}")

    def get_minimal_events(self, ignore_filter_rules: bool, server: Server = None) -> list[MispMinimalEvent]:
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
        output: list[MispMinimalEvent] = []
        finished: bool = False

        filter_rules: dict = {}
        if not ignore_filter_rules:
            filter_rules = self.__filter_rule_to_parameter(server.pull_rules)

        filter_rules["minimal"] = 1
        filter_rules["published"] = 1

        i: int = 1
        while not finished:
            url: str = self.__get_url("/events/index" + f"/limit:{self.__LIMIT}/page:{i}", server)
            i += 1

            request: Request = Request("POST", url, json=filter_rules)
            prepared_request: PreparedRequest = self.__get_session(server).prepare_request(request)
            response: dict = self.__send_request(prepared_request, server)

            for event_view in response:
                try:
                    output.append(MispMinimalEvent.model_validate(event_view))
                except ValueError as value_error:
                    _log.warning(f"Invalid API response. Minimal Event could not be parsed: {value_error}")

            if len(response) < self.__LIMIT:
                finished = True

        return output

    def get_event(self, event_id: int | UUID, server: Server = None) -> AddEditGetEventDetails:
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
        prepared_request: PreparedRequest = self.__get_session(server).prepare_request(request)
        response: dict = self.__send_request(prepared_request, server)
        try:
            return AddEditGetEventDetails.parse_obj(response["Event"])
        except ValueError as value_error:
            raise InvalidAPIResponse(f"Invalid API response. MISP Event could not be parsed: {value_error}")

    def get_event_no_parse(self, event_id: int, server: Server = None) -> dict:
        """
        Returns the event with the given event_id from the given server,
         the own API is used if no server is given.

        :param event_id: the id of the event to get
        :type event_id: int
        :param server: the server to get the event from, if no server is given, the own API is used
        :type server: Server
        :return: returns the event with the given event_id from the given server
        :rtype: dict
        """
        url: str = self.__get_url(f"/events/view/{event_id}", server)
        request: Request = Request("GET", url)
        prepared_request: PreparedRequest = self.__get_session(server).prepare_request(request)
        response: dict = self.__send_request(prepared_request, server)
        try:
            return response["Event"]
        except ValueError as value_error:
            raise InvalidAPIResponse(f"Invalid API response. MISP Event could not be parsed: {value_error}")

    def get_sightings_from_event(self, event_id: int, server: Server = None) -> list[SightingAttributesResponse]:
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
        prepared_request: PreparedRequest = self.__get_session(server).prepare_request(request)
        response: dict = self.__send_request(prepared_request, server)

        out: list[SightingAttributesResponse] = []
        for sighting in response:
            try:
                out.append(MispAPIParser.parse_sighting(sighting))
            except ValueError as value_error:
                _log.warning(f"Invalid API response. Sighting could not be parsed: {value_error}")
        return out

    def get_proposals(self, server: Server = None) -> list[ShadowAttribute]:
        """
        Returns all proposals from the given server from the last 90 days.

        :param server: the server to get the proposals from, if no server is given, the own API is used
        :type server: Server
        :return: returns all proposals from the given server from the last 90 days
        :rtype: list[ShadowAttribute]
        """
        d: datetime = datetime.today() - timedelta(days=90)
        timestamp: str = str(datetime.timestamp(d))

        finished: bool = False
        i: int = 1
        out: list[ShadowAttribute] = []

        while not finished:
            param: str = f"/all:1/timestamp:{timestamp}/limit:{self.__LIMIT}/page:{i}/deleted[]:0/deleted[]:1.json"
            url: str = self.__join_path(server.url, "/shadow_attributes/index" + param)

            request: Request = Request("GET", url)
            prepared_request: PreparedRequest = self.__get_session(server).prepare_request(request)
            response: dict = self.__send_request(prepared_request, server)

            for proposal in response:
                try:
                    out.append(ShadowAttribute.parse_obj(proposal["ShadowAttribute"]))
                except ValueError as value_error:
                    _log.warning(f"Invalid API response. MISP Proposal could not be parsed: {value_error}")
            if len(response) < self.__LIMIT:
                finished = True

        return out

    def get_sharing_groups(self, server: Server = None) -> list[GetAllSharingGroupsResponseResponseItem]:
        """
        Returns all sharing groups from the given server, if no server is given, the own API is used.

        :param server: the server to get the sharing groups from, if no server is given, the own API is used
        :type server: Server
        :return: returns all sharing groups from the given server
        :rtype: list[GetAllSharingGroupsResponseResponseItem]
        """
        url: str = self.__get_url("/sharing_groups", server)

        request: Request = Request("GET", url)
        prepared_request: PreparedRequest = self.__get_session(server).prepare_request(request)
        response: dict = self.__send_request(prepared_request, server)

        try:
            return GetAllSharingGroupsResponse.parse_obj(response).response
        except ValueError as value_error:
            _log.warning(f"Invalid API response. MISP Sharing " f"Group could not be parsed: {value_error}")

    def get_attribute(self, attribute_id: int, server: Server = None) -> GetAttributeAttributes:
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
        prepared_request: PreparedRequest = self.__get_session(server).prepare_request(request)
        response: dict = self.__send_request(prepared_request, server)

        try:
            return GetAttributeResponse.parse_obj(response).Attribute
        except ValueError as value_error:
            raise InvalidAPIResponse(f"Invalid API response. MISP Attribute could not be parsed: {value_error}")

    def get_event_attributes(self, event_id: int, server: Server = None) -> list[SearchAttributesAttributesDetails]:
        """
        Returns all attribute object of the given event, represented by given event_id.

        :param event_id: of the event
        :type event_id: int
        :param server: the server to get the attribute from, if no server is given, the own API is used
        :type server: Server
        :return: a list of all attributes
        :rtype: list[MispFullAttribute]
        """

        url: str = self.__get_url("/attributes/restSearch", server)

        body: dict = {"eventid": event_id, "withAttachments": "true", "includeEventUuid": "true"}
        request: Request = Request("POST", url, json=body)
        prepared_request: PreparedRequest = self.__get_session(server).prepare_request(request)
        response: dict = self.__send_request(prepared_request, server)

        try:
            return SearchAttributesResponse.parse_obj(response).response.Attribute
        except ValueError as value_error:
            raise InvalidAPIResponse(f"Invalid API response. Event Attributes could not be parsed: {value_error}")

    def filter_events_for_push(self, events: list[AddEditGetEventDetails], server: Server = None) -> list[int]:
        """
        Filters the given events for a push on the given server.

        :param events: the events to filter
        :type events: list[AddEditGetEventDetails]
        :param server: the server to filter the events for, if no server is given, the own API is used
        :type server: Server
        :return: returns the ids of the events that should be pushed
        :rtype: list[int]
        """
        url: str = self.__join_path(server.url, "/events/filterEventIdsForPush")
        body: list[dict] = [{"Event": jsonable_encoder(event)} for event in events]
        request: Request = Request("POST", url, json=body)
        session: Session = self.__get_session(server)
        prepared_request: PreparedRequest = session.prepare_request(request)
        response: dict = self.__send_request(prepared_request, server)

        out_uuids: list[UUID] = []
        for uuid in response:
            try:
                out_uuids.append(UUID(uuid))
            except ValueError as value_error:
                _log.warning(f"Invalid API response. Event-UUID could not be " f"parsed: {value_error}")
        return [event.id for event in events if event.uuid in out_uuids]

    def create_attribute(self, attribute: MispFullAttribute, server: Server = None) -> int:
        """
        creates the given attribute on the server

        :param attribute: contains the required attributes to creat an attribute
        :type attribute: MispFullAttribute
        :param server: the server to create the attribute on, if no server is given, the own API is used
        :type server: Server
        :return: The attribute id if the creation was successful. -1 otherwise.
        :rtype: int
        """
        url: str = self.__get_url(f"/attributes/add/{attribute.event_id}", server)
        json_data_str = attribute.model_dump_json()
        json_data = json.loads(json_data_str)
        if "uuid" in json_data:
            del json_data["uuid"]
        if "id" in json_data:
            del json_data["id"]

        json_data_str = json.dumps(json_data)
        request: Request = Request("POST", url, data=json_data_str)
        prepared_request: PreparedRequest = self.__get_session(server).prepare_request(request)
        response: dict = self.__send_request(prepared_request, server)
        if "Attribute" in response:
            return int(response["Attribute"]["id"])

        return -1

    def create_tag(self, tag: TagViewResponse, server: Server = None) -> int:
        """
        Creates the given tag on the server
        :param tag: The tag to create.
        :type tag: TagViewResponse
        :param server: The server to create the tag on. If no server is given, the own MMISP-API Server is used.
        :type server: Server
        :return: the id of the created tag
        :rtype: int
        """

        url: str = self.__get_url("/tags/add", server)
        json_data = tag.model_dump_json()
        request: Request = Request("POST", url, data=json_data)
        prepared_request: PreparedRequest = self.__get_session(server).prepare_request(request)

        response: dict = self.__send_request(prepared_request, server)
        return int(response["Tag"]["id"])

    def attach_attribute_tag(self, relationship: AttributeTagRelationship, server: Server = None) -> bool:
        """
        Attaches a tag to an attribute

        :param relationship: contains the attribute id, tag id and the
        :type relationship: AttributeTagRelationship
        :param server: the server to attach the tag to the attribute on, if no server is given, the own API is used
        :type server: Server
        :return: true if the attachment was successful
        :rtype: bool
        """
        url: str = self.__get_url(
            f"/attributes/addTag/{relationship.attribute_id}/{relationship.tag_id}/local:" f"{relationship.local}",
            server,
        )
        request: Request = Request("POST", url)
        prepared_request: PreparedRequest = self.__get_session(server).prepare_request(request)
        self.__send_request(prepared_request, server)

        return True

    def attach_event_tag(self, relationship: EventTagRelationship, server: Server = None) -> bool:
        """
        Attaches a tag to an event

        :param relationship:
        :type relationship: EventTagRelationship
        :param server: the server to attach the tag to the event on, if no server is given, the own API is used
        :type server: Server
        :return:
        :rtype: bool
        """
        url: str = self.__get_url(
            f"/events/addTag/{relationship.event_id}/{relationship.tag_id}/local:" f"{relationship.local}", server
        )
        request: Request = Request("POST", url)
        prepared_request: PreparedRequest = self.__get_session(server).prepare_request(request)

        self.__send_request(prepared_request, server)
        return True

    def modify_event_tag_relationship(self, relationship: EventTagRelationship, server: Server = None) -> bool:
        """
        Modifies the relationship of the given tag to the given event
        Endpoint documented at: https://www.misp-project.org/2022/10/10/MISP.2.4.164.released.html/

        :param relationship: contains the event id, tag id and the relationship type
        :type relationship: EventTagRelationship
        :param server: the server to modify the relationship on, if no server is given, the own API is used
        :type server: Server
        :return: returns true if the modification was successful
        :rtype: bool
        """

        url: str = self.__get_url(f"/tags/modifyTagRelationship/event/{relationship.id}", server)

        request: Request = Request("POST", url)
        prepared_request: PreparedRequest = self.__get_session(server).prepare_request(request)
        prepared_request.body = {"Tag": {"relationship_type": relationship.relationship_type}}

        response: dict = self.__send_request(prepared_request, server)
        return response["saved"] == "true" and response["success"] == "true"

    def modify_attribute_tag_relationship(self, relationship: AttributeTagRelationship, server: Server = None) -> bool:
        """
        Modifies the relationship of the given tag to the given attribute
        Endpoint documented at: https://www.misp-project.org/2022/10/10/MISP.2.4.164.released.html/

        :param relationship: contains the event id, tag id and the relationship type
        :type relationship: EventTagRelationship
        :param server: the server to modify the relationship on, if no server is given, the own API is used
        :type server: Server
        :return: returns true if the modification was successful
        :rtype: bool
        """

        url: str = self.__get_url(f"/tags/modifyTagRelationship/attribute/{relationship.id}", server)

        request: Request = Request("POST", url)
        prepared_request: PreparedRequest = self.__get_session(server).prepare_request(request)
        prepared_request.body = {"Tag": {"relationship_type": relationship.relationship_type}}

        response: dict = self.__send_request(prepared_request, server)
        return response["saved"] == "true" and response["success"] == "true"

    def save_cluster(self, cluster: GetGalaxyClusterResponse, server: Server = None) -> bool:
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
        prepared_request: PreparedRequest = self.__get_session(server).prepare_request(request)

        try:
            self.__send_request(prepared_request, server)
            return True
        except ValueError as value_error:
            _log.warning(f"Invalid API response. Galaxy Cluster with {cluster.id} could not be saved: {value_error}")
            return False

    def save_event_dic(self, event: dict, server: Server = None) -> bool:
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
        request: Request = Request("POST", url, json=event)
        prepared_request: PreparedRequest = self.__get_session(server).prepare_request(request)

        try:
            self.__send_request(prepared_request, server)
            return True
        except Exception:
            return False

    def update_event_dic(self, event: dict, server: Server = None) -> bool:
        """
        Saves the given event on the given server.

        :param event: the event to save
        :type event: AddEditGetEventDetails
        :param server: the server to save the event on, if no server is given, the own API is used
        :type server: Server
        :return: returns true if the saving was successful
        :rtype: bool
        """
        url: str = self.__get_url(f"/events/edit/{event['uuid']}", server)
        request: Request = Request("POST", url, json=event)
        prepared_request: PreparedRequest = self.__get_session(server).prepare_request(request)

        try:
            self.__send_request(prepared_request, server)
            return True
        except Exception:
            return False

    def save_proposal(self, event: AddEditGetEventDetails, server: Server = None) -> bool:
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
        request: Request = Request("POST", url)
        request.body = event.shadow_attributes
        prepared_request: PreparedRequest = self.__get_session(server).prepare_request(request)

        try:
            self.__send_request(prepared_request, server)
            return True
        except ValueError:
            return False

    def save_sighting(self, sighting: SightingAttributesResponse, server: Server = None) -> bool:
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
        request.body = sighting
        prepared_request: PreparedRequest = self.__get_session(server).prepare_request(request)

        try:
            self.__send_request(prepared_request, server)
            return True
        except ValueError as value_error:
            _log.warning(f"Invalid API response. Sighting with id {sighting.id} could not be saved: {value_error}")
            return False

    def __filter_rule_to_parameter(self, filter_rules: str) -> dict[str, list[str]]:
        """
        This method is used to convert the given filter rules string to a dictionary for the API.
        :param filter_rules: the filter rules to convert
        :type filter_rules: dict
        :return: returns the filter rules as a parameter for the API
        :rtype: dict
        """
        out = dict()
        if not filter_rules:
            return out
        url_params = {}

        filter_rules_dict: dict = json.loads(filter_rules)
        for field, rules in filter_rules_dict.items():
            temp = []
            if field == "url_params":
                url_params = {} if not rules else json.loads(rules)
            else:
                for operator, elements in rules.items():
                    for k, element in enumerate(elements):
                        if operator == "NOT":
                            element = "!" + element
                        if element:
                            temp.append(element)
                if temp:
                    out[field[:-1]] = temp

        if url_params:
            out.update(url_params)

        return out
