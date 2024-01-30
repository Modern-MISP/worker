from typing import Mapping
from typing import TypeAlias
from uuid import UUID

from requests import Session, Response, codes, PreparedRequest, Request
from requests.adapters import HTTPAdapter

from mmisp.worker.exceptions.misp_api_exceptions import InvalidAPIResponse, APIException
from mmisp.worker.misp_database.misp_api_config import misp_api_config_data, MispAPIConfigData
from mmisp.worker.misp_database.misp_api_parser import MispAPIParser
from mmisp.worker.misp_database.misp_api_utils import MispAPIUtils
from mmisp.worker.misp_dataclasses.misp_attribute import MispEventAttribute
from mmisp.worker.misp_dataclasses.misp_event import MispEvent
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

    def __init__(self):
        self.__config: MispAPIConfigData = misp_api_config_data
        self.__session: Session = self.__setup_api_session()

    def __setup_api_session(self) -> Session:

        session = Session()

        connect_timeout: int = self.__config.connect_timeout
        read_timeout: int = self.__config.read_timeout
        session.mount('http://', TimeoutHTTPAdapter(connect_timeout, read_timeout))
        session.mount('https://', TimeoutHTTPAdapter(connect_timeout, read_timeout))

        session.headers.update(self.__HEADERS)
        session.headers.update({'Authorization': f"{self.__config.key}"})

        return session

    def __get_url(self, path: str) -> str:
        url: str = self.__config.url
        return self.__join_path(url, path)

    def __join_path(self, url: str, path: str) -> str:
        if path.startswith('/'):
            return url + path
        else:
            return f"{url}/{path}"


    def __send_request(self, request: PreparedRequest, **kwargs) -> dict:
        response: Response
        # TODO: Error handling
        try:
            response = self.__session.send(request, **kwargs)
        except ConnectionError as connection_error:
            # TODO: Log API Connection failure.
            raise APIException("API not availabe. The request could not be made.")
        # except TimeoutError as timeout_error:
        #     pass
        # except TooManyRedirects as too_many_redirects_error:
        #     pass

        if response.status_code != codes.ok:
            response.raise_for_status()

        return MispAPIUtils.decode_json_response(response)

    def get_server(self, server_id: int) -> MispServer:
        url: str = self.__get_url(f"/servers/index/{server_id}")

        request: Request = Request('GET', url)
        prepared_request: PreparedRequest = self.__session.prepare_request(request)
        response: dict = self.__send_request(prepared_request)
        try:
            return MispAPIParser.parse_server(response)
        except ValueError as value_error:
            raise InvalidAPIResponse(f"Invalid API response. MISP server could not be parsed: {value_error}")

    def get_server_version(self, server: MispServer) -> MispServerVersion:
        pass

    def get_custom_cluster_from_server(self, conditions: JsonType, server: MispServer) \
            -> list[MispGalaxyCluster]:
        pass

    def get_galaxy_cluster(self, cluster_id: int, server: MispServer) -> MispGalaxyCluster:
        pass

    def get_event_views_from_server(self, ignore_filter_rules: bool, server: MispServer) -> list[MispEvent]:
        pass

    def get_event_from_server(self, event_uuid: UUID, server: MispServer) -> MispEvent:
        pass

    def get_event(self, event_id: int | str) -> MispEvent:
        """
        TODO: Doesn't work yet due to wrong types in MispEvent class.
        TODO: Test
        """
        url: str = self.__get_url(f"/events/view/{event_id}")

        request: Request = Request('GET', url)
        prepared_request: PreparedRequest = self.__session.prepare_request(request)
        response: dict = self.__send_request(prepared_request)

        event: MispEvent
        try:
            event = MispEvent.model_validate(response['Event'])
        except ValueError as value_error:
            raise InvalidAPIResponse(f"Invalid API response. MISP Event could not be parsed: {value_error}")

        return event

    def get_sightings(self, user_id: int, server: MispServer) -> list[MispSighting]:
        pass

    def get_sightings_from_event(self, event_uuid: UUID, server: MispServer) -> list[MispSighting]:
        pass

    def get_proposals(self, user_id: int, server: MispServer) -> list[MispProposal]:
        pass

    def get_sharing_groups_ids(self, server: MispServer) -> list[int]:
        pass

    def filter_event_ids_for_push(self, events: list[UUID], server: MispServer) -> list[UUID]:
        pass

    def set_last_pulled_id(self, server: MispServer) -> bool:
        pass

    def set_last_pushed_id(self, server: MispServer) -> bool:
        pass

    def save_cluster(self, cluster: MispGalaxyCluster, server: MispServer) -> bool:
        pass

    def save_event(self, event: MispEvent, server: MispServer) -> bool:
        pass

    def save_proposal(self, event: MispEvent, server: MispServer) -> bool:
        pass

    def save_sightings(self, sightings: list[MispSighting], server: MispServer) -> int:
        pass

    def get_event_attribute(self, attribute_id: int) -> MispEventAttribute:
        url: str = self.__get_url(f"/attributes/view/{attribute_id}")

        request: Request = Request('GET', url)
        prepared_request: PreparedRequest = self.__session.prepare_request(request)
        response: dict = self.__send_request(prepared_request)

        attribute: MispEventAttribute
        try:
            attribute = MispAPIParser.parse_event_attribute(response['Attribute'])
        except ValueError as value_error:
            raise InvalidAPIResponse(f"Invalid API response. MISP Attribute could not be parsed: {value_error}")
        return attribute

    def get_event_attributes(self, event_id: int) -> list[MispEventAttribute]:
        pass

    def create_attribute(self, attribute: MispEventAttribute) -> bool:
        pass

    def create_tag(self, attribute: MispTag) -> id:
        pass

    def attach_attribute_tag(self, relationship: AttributeTagRelationship) -> bool:
        pass

    def attach_event_tag(self, relationship: EventTagRelationship) -> bool:
        pass

    def get_user(self, user_id: int) -> MispUser:

        url: str = self.__get_url(f"/admin/users/view/{user_id}")

        request: Request = Request('GET', url)
        prepared_request: PreparedRequest = self.__session.prepare_request(request)
        response: dict = self.__send_request(prepared_request)

        try:
            return MispAPIParser.parse_user(response)
        except ValueError as value_error:
            raise InvalidAPIResponse(f"Invalid API response. MISP user could not be parsed: {value_error}")

    def get_object(self, object_id: int) -> MispObject:
        pass

    def get_sharing_group(self, sharing_group_id: int) -> MispSharingGroup:
        """
        url: str = self.__get_url(f"/sharing_groups/view/{sharing_group_id}")

        request: Request = Request('GET', url)
        prepared_request: PreparedRequest = self.__session.prepare_request(request)
        response: dict = self.__send_request(prepared_request)

        try:
            re = MispAPIParser.get_sharing_group(response)
            print(re)
            return re
        except ValueError as value_error:
            raise InvalidAPIResponse(f"Invalid API response. MISP MispSharingGroup could not be parsed: {value_error}")

        """

    def __modify_event_tag_relationship(self, relationship: EventTagRelationship) -> bool:
        pass

    def __modify_attribute_tag_relationship(self, relationship: AttributeTagRelationship) -> bool:
        pass
