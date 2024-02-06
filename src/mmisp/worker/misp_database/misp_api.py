import json
from datetime import datetime, timedelta
from typing import Mapping
from typing import TypeAlias
from uuid import UUID

import requests
from requests import Session, Response, codes, PreparedRequest, Request
from requests.adapters import HTTPAdapter

from mmisp.worker.exceptions.misp_api_exceptions import InvalidAPIResponse, APIException
from mmisp.worker.misp_database.misp_api_config import misp_api_config_data, MispAPIConfigData
from mmisp.worker.misp_database.misp_api_parser import MispAPIParser
from mmisp.worker.misp_database.misp_api_utils import MispAPIUtils
from mmisp.worker.misp_database.misp_sql import MispSQL
from mmisp.worker.misp_dataclasses.misp_event import MispEvent
from mmisp.worker.misp_dataclasses.misp_event_attribute import MispEventAttribute
from mmisp.worker.misp_dataclasses.misp_event_view import MispMinimalEvent
from mmisp.worker.misp_dataclasses.misp_galaxy_cluster import MispGalaxyCluster
from mmisp.worker.misp_dataclasses.misp_object import MispObject
from mmisp.worker.misp_dataclasses.misp_proposal import MispProposal
from mmisp.worker.misp_dataclasses.misp_server import MispServer
from mmisp.worker.misp_dataclasses.misp_server_version import MispServerVersion
from mmisp.worker.misp_dataclasses.misp_sharing_group import MispSharingGroup
from mmisp.worker.misp_dataclasses.misp_sighting import MispSighting
from mmisp.worker.misp_dataclasses.misp_tag import EventTagRelationship, AttributeTagRelationship
from mmisp.worker.misp_dataclasses.misp_tag import MispTag
from mmisp.worker.misp_dataclasses.misp_user import MispUser

JsonType: TypeAlias = list['JsonValue'] | Mapping[str, 'JsonValue']
JsonValue: TypeAlias = str | int | float | None | JsonType


class MispObjectEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            # if the obj is uuid, we simply return the value of uuid
            return str(obj)
        return json.JSONEncoder.default(self, obj)


class TimeoutHTTPAdapter(HTTPAdapter):
    """
    TODO: Maybe remove this class and set default timeout in 'MispAPI.__send_request()' method.
    """

    def __init__(self, connect_timeout: int, read_timeout: int, *args, **kwargs):
        if connect_timeout and connect_timeout > 0:
            if read_timeout and read_timeout > 0:
                self.__timeout = (connect_timeout, read_timeout)
            else:
                raise ValueError(f"read_timeout is {connect_timeout}, but must be a positive integer.")
        else:
            raise ValueError(f"connect_timeout is {connect_timeout}, but must be a positive integer.")

        super().__init__(*args, **kwargs)

    def send(self, request, *args, **kwargs):
        if 'timeout' not in kwargs or kwargs['timeout'] is None and hasattr(self, '__timeout'):
            kwargs['timeout'] = self.__timeout
        return super().send(request, *args, **kwargs)


class MispAPI:
    __HEADERS: dict = {'Accept': 'application/json',
                       'Content-Type': 'application/json',
                       'Authorization': ''}
    __LIMIT: int = 1000

    def __init__(self):
        self.__config: MispAPIConfigData = misp_api_config_data
        self.__session: dict[int, Session] = {0: self.__setup_api_session()}
        self.__misp_sql: MispSQL = None

    def __setup_api_session(self) -> Session:

        session = Session()
        connect_timeout: int = self.__config.connect_timeout
        read_timeout: int = self.__config.read_timeout
        session.mount('http://', TimeoutHTTPAdapter(connect_timeout, read_timeout))
        session.mount('https://', TimeoutHTTPAdapter(connect_timeout, read_timeout))
        session.headers.update(self.__HEADERS)
        session.headers.update({'Authorization': f"{self.__config.key}"})
        return session

    def __setup_remote_api_session(self, server_id: int) -> Session:
        if self.__misp_sql is None:
            self.__misp_sql = MispSQL()
        key: str = self.__misp_sql.get_api_authkey(server_id)
        if key is None:
            raise APIException(f"API key for server {server_id} is not available.")

        session = Session()
        connect_timeout: int = self.__config.connect_timeout
        read_timeout: int = self.__config.read_timeout
        session.mount('http://', TimeoutHTTPAdapter(connect_timeout, read_timeout))
        session.mount('https://', TimeoutHTTPAdapter(connect_timeout, read_timeout))
        session.headers.update(self.__HEADERS)
        session.headers.update({'Authorization': f"{key}"})
        return session

    def __get_session(self, server_id: int = 0) -> Session:
        if server_id in self.__session:
            return self.__session[server_id]
        else:
            session: Session = self.__setup_remote_api_session(server_id)
            self.__session[server_id] = session
            return session

    def __get_url(self, path: str, server: MispServer = None) -> str:
        url: str
        if server:
            url = server.url
        else:
            url = self.__config.url

        return self.__join_path(url, path)

    @staticmethod
    def __join_path(url: str, path: str) -> str:
        if path.startswith('/'):
            return url + path
        else:
            return f"{url}/{path}"

    def __send_request(self, request: PreparedRequest, **kwargs) -> dict:
        response: Response
        # TODO: Error handling
        try:
            response = self.__get_session().send(request, **kwargs)
        except ConnectionError as connection_error:
            # TODO: Log API Connection failure.
            raise APIException("API not availabe. The request could not be made.")
        # except TimeoutError as timeout_error:
        #     pass
        # except TooManyRedirects as too_many_redirects_error:
        #     pass

        if response.status_code != codes.ok:
            # print(response.json())
            raise requests.HTTPError(response, response.json())
            # response.raise_for_status()

        return MispAPIUtils.decode_json_response(response)

    def get_user(self, user_id: int) -> MispUser:
        """

        :param user_id:
        :type user_id:
        :return:
        :rtype:
        """
        # At the moment, the API team has not defined this API call.
        url: str = self.__get_url(f"/admin/users/view/{user_id}")

        request: Request = Request('GET', url)
        prepared_request: PreparedRequest = self.__get_session().prepare_request(request)
        response: dict = self.__send_request(prepared_request)

        try:
            return MispAPIParser.parse_user(response)
        except ValueError as value_error:
            raise InvalidAPIResponse(f"Invalid API response. MISP user could not be parsed: {value_error}")

    def get_object(self, object_id: int) -> MispObject:
        # TODO url zu /objects/{object_id} ändern (von api gruppe)
        url: str = self.__get_url(f"objects/view/{object_id}")

        request: Request = Request('GET', url)
        prepared_request: PreparedRequest = self.__get_session().prepare_request(request)
        response: dict = self.__send_request(prepared_request)

        try:

            return MispObject.model_validate(response['Object'])
        except ValueError as value_error:
            raise InvalidAPIResponse(f"Invalid API response. MISP MispObject could not be parsed: {value_error}")

    def get_sharing_group(self, sharing_group_id: int) -> MispSharingGroup:
        url: str = self.__get_url(f"/sharing_groups/{sharing_group_id}/info")

        request: Request = Request('GET', url)
        prepared_request: PreparedRequest = self.__get_session().prepare_request(request)
        response: dict = self.__send_request(prepared_request)

        try:

            return MispAPIParser.parse_sharing_group(response)
        except ValueError as value_error:
            raise InvalidAPIResponse(f"Invalid API response. MISP MispSharingGroup could not be parsed: {value_error}")


    def get_server(self, server_id: int) -> MispServer:
        url: str = self.__get_url(f"/servers/index/{server_id}")

        request: Request = Request('GET', url)
        prepared_request: PreparedRequest = self.__get_session().prepare_request(request)
        response: dict = self.__send_request(prepared_request)
        try:
            return MispAPIParser.parse_server(response[0])
        except ValueError as value_error:
            raise InvalidAPIResponse(f"Invalid API response. MISP server could not be parsed: {value_error}")

    def get_server_version(self, server: MispServer) -> MispServerVersion:
        endpoint_url: str = "/servers/getVersion"
        url: str = ""
        if server is None:
            url: str = self.__get_url(endpoint_url)
        else:
            url: str = self.__join_path(server.url, endpoint_url)

        request: Request = Request('GET', url)
        prepared_request: PreparedRequest = self.__get_session(server.id).prepare_request(request)
        response: dict = self.__send_request(prepared_request)

        try:
            return MispServerVersion.model_validate(response)
        except ValueError as value_error:
            raise InvalidAPIResponse(f"Invalid API response. Server Version could not be parsed: {value_error}")

    def get_custom_clusters_from_server(self, conditions: JsonType, server: MispServer) \
            -> list[MispGalaxyCluster]:

        output: list[MispGalaxyCluster] = []
        finished: bool = False
        i: int = 1
        while not finished:
            endpoint_url = "/galaxy_clusters/restSearch" + f"/limit:{self.__LIMIT}/page:{i}"
            url: str = self.__get_url(endpoint_url, server)
            i += 1

            request: Request = Request('POST', url)
            request.body = conditions
            prepared_request: PreparedRequest = self.__get_session(server.id).prepare_request(request)
            response: dict = self.__send_request(prepared_request)

            try:
                for cluster in response:
                    output.append(MispAPIParser.parse_galaxy_cluster(cluster))
            except ValueError as value_error:
                raise InvalidAPIResponse(f"Invalid API response. Server Version could not be parsed: {value_error}")

            if len(response) < self.__LIMIT:
                finished = True

        return output

    def get_galaxy_cluster(self, cluster_id: int, server: MispServer) -> MispGalaxyCluster:
        endpoint_url: str = f"/galaxy_clusters/view/{cluster_id}"
        url: str = self.__get_url(endpoint_url, server)

        request: Request = Request('GET', url)
        prepared_request: PreparedRequest = self.__get_session(server.id).prepare_request(request)
        response: dict = self.__send_request(prepared_request)

        try:
            return MispAPIParser.parse_galaxy_cluster(response)
        except ValueError as value_error:
            raise InvalidAPIResponse(f"Invalid API response. Server Version could not be parsed: {value_error}")

    def get_minimal_events_from_server(self, ignore_filter_rules: bool, server: MispServer) -> list[MispMinimalEvent]:
        output: list[MispMinimalEvent] = []
        finished: bool = False
        i: int = 1
        while not finished:
            endpoint_url = "/events/index" + f"/limit:{self.__LIMIT}/page:{i}"
            url: str = self.__get_url(endpoint_url, server)
            i += 1

            filter_rules: dict = {}
            if not ignore_filter_rules:
                filter_rules = self.__filter_rule_to_parameter(server.pull_rules)

            filter_rules['minimal'] = True
            filter_rules['published'] = True

            request: Request = Request('POST', url)
            request.body = filter_rules
            prepared_request: PreparedRequest = self.__get_session(server.id).prepare_request(request)
            response: dict = self.__send_request(prepared_request)

            try:
                for event_view in response:
                    output.append(MispMinimalEvent.model_validate(event_view))
            except ValueError as value_error:
                raise InvalidAPIResponse(f"Invalid API response. Server Version could not be parsed: {value_error}")

            if len(response) < self.__LIMIT:
                finished = True

        return output

    def get_event(self, event_id: int, server: MispServer = None) -> MispEvent:
        endpoint_path: str = f"/events/view/{event_id}"

        url: str
        id: int = 0
        if server is not None:
            url = self.__get_url(endpoint_path, server.url)
            id = server.id
        else:
            url = self.__get_url(endpoint_path)

        request: Request = Request('GET', url)
        prepared_request: PreparedRequest = self.__get_session(id).prepare_request(request)
        response: dict = self.__send_request(prepared_request)

        parsed_event: MispEvent
        try:
            return MispAPIParser.parse_event(response['Event'])
        except ValueError as value_error:
            raise InvalidAPIResponse(f"Invalid API response. MISP Event could not be parsed: {value_error}")

    def get_sightings_from_event(self, event_id: int, server: MispServer) -> list[MispSighting]:
        url: str = self.__join_path(server.url, f"/sightings/index/{event_id}")

        request: Request = Request('GET', url)
        prepared_request: PreparedRequest = self.__get_session(server.id).prepare_request(request)
        response: dict = self.__send_request(prepared_request)

        try:
            out: list[MispSighting] = []
            for sighting in response:
                out.append(MispAPIParser.parse_sighting(sighting))
            return out

        except ValueError as value_error:
            raise InvalidAPIResponse(f"Invalid API response. MISP Event could not be parsed: {value_error}")

    def get_proposals(self, server: MispServer) -> list[MispProposal]:
        d: datetime = datetime.today() - timedelta(days=90)
        timestamp: str = str(datetime.timestamp(d))

        finished: bool = False
        i: int = 1
        out: list[MispProposal] = []

        while not finished:
            param: str = f"/all:1/timestamp:{timestamp}/limit:{self.__LIMIT}/page:{i}/deleted[]:0/deleted[]:1.json"
            url: str = self.__join_path(server.url, '/shadow_attributes/index' + param)

            request: Request = Request('GET', url)
            prepared_request: PreparedRequest = self.__get_session(server.id).prepare_request(request)
            response: dict = self.__send_request(prepared_request)

            try:
                for proposal in response:
                    out.append(MispAPIParser.parse_proposal(proposal["ShadowAttribute"]))

            except ValueError as value_error:
                raise InvalidAPIResponse(f"Invalid API response. MISP Event could not be parsed: {value_error}")
            if len(response) < self.__LIMIT:
                finished = True

        return out

    def get_sharing_groups(self, server: MispServer = None) -> list[MispSharingGroup]:
        url: str = self.__join_path(server.url, f"/sharing_groups")

        request: Request = Request('GET', url)
        prepared_request: PreparedRequest = self.__get_session(server.id).prepare_request(request)
        response: dict = self.__send_request(prepared_request)

        try:
            out: list[MispSharingGroup] = []
            for sharing_group in response["response"]:
                out.append(MispAPIParser.parse_sharing_group(sharing_group))
            return out

        except ValueError as value_error:
            raise InvalidAPIResponse(f"Invalid API response. MISP Event could not be parsed: {value_error}")

    def get_event_attribute(self, attribute_id: int) -> MispEventAttribute:
        url: str = self.__get_url(f"/attributes/{attribute_id}")

        request: Request = Request('GET', url)
        prepared_request: PreparedRequest = self.__get_session().prepare_request(request)
        response: dict = self.__send_request(prepared_request)

        attribute: MispEventAttribute
        try:
            attribute = MispAPIParser.parse_event_attribute(response['Attribute'])
        except ValueError as value_error:
            raise InvalidAPIResponse(f"Invalid API response. MISP Attribute could not be parsed: {value_error}")
        return attribute

    def get_event_attributes(self, event_id: int) -> list[MispEventAttribute]:
        """
        Returns all attribute object of the given event, represented by given event_id.
        :param event_id: of the event
        :type event_id: int
        :return: a list of all attributes
        :rtype: list[MispEventAttribute]
        """
        url: str = self.__get_url("/attributes/restSearch")

        request: Request = Request('POST', url)
        prepared_request: PreparedRequest = self.__get_session().prepare_request(request)
        prepared_request.body = {'eventid': event_id}
        response: dict = self.__send_request(prepared_request)

        attributes: list[MispEventAttribute] = []
        for attribute in response:
            parsed_attribute: MispEventAttribute
            try:
                parsed_attribute = MispAPIParser.parse_event_attribute(attribute)
            except ValueError as value_error:
                raise InvalidAPIResponse(f"Invalid API response. MISP Attributes could not be parsed: {value_error}")

            attributes.append(parsed_attribute)

        return attributes

    def filter_events_for_push(self, events: list[MispEvent], server: MispServer) -> list[int]:
        url: str = self.__join_path(server.url, "/events/filterEventIdsForPush")
        request: Request = Request('POST', url)
        body: list[dict[str, MispEvent]] = [{"Event": event} for event in events]
        request.body = body
        prepared_request: PreparedRequest = self.__get_session(server.id).prepare_request(request)
        response: dict = self.__send_request(prepared_request)

        try:
            out_uuids: list[UUID] = []
            for uuid in response:
                out_uuids.append(UUID(uuid))
            return [event.id for event in events if event.uuid in out_uuids]
        except ValueError as value_error:
            raise InvalidAPIResponse(f"Invalid API response. Server Version could not be parsed: {value_error}")

    def create_attribute(self, attribute: MispEventAttribute) -> bool:
        """
        Creates an attribute.
        :param attribute: contains the required attributes to creat an attribute
        :type attribute: MispEventAttribute
        :return: if the creation was successful return true, else false
        :rtype: bool
        """
        url: str = self.__get_url(f"/attributes/add/{attribute.event_id}")
        #json_data = json.dumps(attribute.__dict__, cls=MispObjectEncoder)
        json_data = attribute.model_dump_json()
        request: Request = Request('POST', url, data=json_data)
        prepared_request: PreparedRequest = self.__get_session().prepare_request(request)
        try:
            response: dict = self.__send_request(prepared_request)
            return True
        except requests.HTTPError as exception:
            msg: dict = exception.strerror
            print(
                f"{exception}\r\n {exception.args}\r\n {msg['errors']['value']}\r\n {exception.errno.status_code}\r\n")
        return False

    def create_tag(self, attribute: MispTag) -> int:
        """
        Creates a tag.
        :param attribute: contains the required attributes to creat a tag
        :type attribute: MispTag
        :return: the id of the created tag
        :rtype: int
        """
        url: str = self.__get_url(f"/tags/add")
        json_data = json.dumps(attribute.__dict__, cls=MispObjectEncoder)
        request: Request = Request('POST', url, data=json_data)
        prepared_request: PreparedRequest = self.__get_session().prepare_request(request)

        response: dict = self.__send_request(prepared_request)
        return response['id']

    def attach_attribute_tag(self, relationship: AttributeTagRelationship) -> bool:
        """
        Attaches a tag to an attribute
        :param relationship: contains the attribute id, tag id and the
        :type relationship: AttributeTagRelationship
        :return: true if the attachment was successful
        :rtype: bool
        """
        url: str = self.__get_url(f"/attributes/addTag/{relationship.attribute_id}/{relationship.tag_id}/local:"
                                  f"{relationship.local}")
        request: Request = Request('POST', url)
        prepared_request: PreparedRequest = self.__get_session().prepare_request(request)
        self.__send_request(prepared_request)

        return True

    def attach_event_tag(self, relationship: EventTagRelationship) -> bool:
        """
        Attaches a tag to an event
        :param relationship:
        :type relationship: EventTagRelationship
        :return:
        :rtype: bool
        """
        url: str = self.__get_url(f"/events/addTag/{relationship.event_id}/{relationship.tag_id}/local:"
                                  f"{relationship.local}")
        request: Request = Request('POST', url)
        prepared_request: PreparedRequest = self.__get_session().prepare_request(request)

        self.__send_request(prepared_request)
        return True


    def modify_event_tag_relationship(self, relationship: EventTagRelationship) -> bool:
        # https://www.misp-project.org/2022/10/10/MISP.2.4.164.released.html/
        url: str = self.__get_url(f"/tags/modifyTagRelationship/event/{relationship.id}")

        request: Request = Request('POST', url)
        prepared_request: PreparedRequest = self.__get_session().prepare_request(request)
        prepared_request.body = {
            "Tag": {
                "relationship_type": relationship.relationship_type
            }
        }

        response: dict = self.__send_request(prepared_request)
        return response['saved'] == 'true' and response['success'] == 'true'

    def modify_attribute_tag_relationship(self, relationship: AttributeTagRelationship) -> bool:
        # https://www.misp-project.org/2022/10/10/MISP.2.4.164.released.html/
        url: str = self.__get_url(f"/tags/modifyTagRelationship/attribute/{relationship.id}")

        request: Request = Request('POST', url)
        prepared_request: PreparedRequest = self.__get_session().prepare_request(request)
        prepared_request.body = {
            "Tag": {
                "relationship_type": relationship.relationship_type
            }
        }

        response: dict = self.__send_request(prepared_request)
        return response['saved'] == 'true' and response['success'] == 'true'

    def __filter_rule_to_parameter(self, filter_rules: dict):
        out = {}
        if not filter_rules:
            return out
        url_params = {}

        for field, rules in filter_rules.items():
            temp = []
            if field == 'url_params':
                url_params = {} if not rules else json.loads(rules)
            else:
                for operator, elements in rules.items():
                    for k, element in enumerate(elements):
                        if operator == 'NOT':
                            element = '!' + element
                        if element:
                            temp.append(element)
                if temp:
                    out[field[:-1]] = temp

        if url_params:
            out.update(url_params)

        return out

    def save_cluster(self, cluster: MispGalaxyCluster, server: MispServer) -> bool:
        url: str = self.__join_path(server.url, f"/galaxy_clusters/add/{cluster.id}")
        request: Request = Request('POST', url)
        request.body = cluster
        prepared_request: PreparedRequest = self.__get_session(server.id).prepare_request(request)

        try:
            self.__send_request(prepared_request)
            return True
        except ValueError as value_error:
            return False

    def save_event(self, event: MispEvent, server: MispServer) -> bool:
        url: str = self.__join_path(server.url, "/events/add")
        request: Request = Request('POST', url)
        request.body = event
        prepared_request: PreparedRequest = self.__get_session(server.id).prepare_request(request)

        try:
            self.__send_request(prepared_request)
            return True
        except ValueError as value_error:
            return False

    def save_proposal(self, event: MispEvent, server: MispServer) -> bool:
        url: str = self.__join_path(server.url, f"/events/pushProposals/{event.id}")
        request: Request = Request('POST', url)
        request.body = event.shadow_attributes
        prepared_request: PreparedRequest = self.__get_session(server.id).prepare_request(request)

        try:
            self.__send_request(prepared_request)
            return True
        except ValueError as value_error:
            return False

    def save_sighting(self, sighting: MispSighting, server: MispServer) -> bool:
        url: str = self.__join_path(server.url, f"/sightings/add/{sighting.attribute_id}")
        request: Request = Request('POST', url)
        request.body = sighting
        prepared_request: PreparedRequest = self.__get_session(server.id).prepare_request(request)

        try:
            self.__send_request(prepared_request)
            return True
        except ValueError as value_error:
            return False