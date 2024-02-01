from mmisp.worker.misp_database.misp_api_utils import MispAPIUtils
from mmisp.worker.misp_dataclasses.misp_event_attribute import MispEventAttribute
from mmisp.worker.misp_dataclasses.misp_event import MispEvent
from mmisp.worker.misp_dataclasses.misp_event_view import MispEventView
from mmisp.worker.misp_dataclasses.misp_galaxy import MispGalaxy
from mmisp.worker.misp_dataclasses.misp_galaxy_cluster import MispGalaxyCluster
from mmisp.worker.misp_dataclasses.misp_galaxy_element import MispGalaxyElement
from mmisp.worker.misp_dataclasses.misp_organisation import MispOrganisation
from mmisp.worker.misp_dataclasses.misp_role import MispRole
from mmisp.worker.misp_dataclasses.misp_server import MispServer
from mmisp.worker.misp_dataclasses.misp_sharing_group import MispSharingGroup
from mmisp.worker.misp_dataclasses.misp_sharing_group_org import MispSharingGroupOrg
from mmisp.worker.misp_dataclasses.misp_sharing_group_server import MispSharingGroupServer
from mmisp.worker.misp_dataclasses.misp_sighting import MispSighting
from mmisp.worker.misp_dataclasses.misp_tag import MispTag
from mmisp.worker.misp_dataclasses.misp_user import MispUser


class MispAPIParser:

    @classmethod
    def parse_event(cls, event: dict) -> MispEvent:
        prepared_event: dict = event.copy()
        event_response_translator: dict = {
            'Org': 'org',
            'Orgc': 'orgc',
            'Attribute': 'attributes',
            'ShadowAttribute': 'shadow_attributes',
            'RelatedEvent': 'related_events',
            # 'Galaxy': 'clusters', TODO!
            'Object': 'objects',
            'EventReport': 'reports',
            'Tag': 'tags',
            'CryptographicKey': 'cryptographic_key'
        }

        # TODO: Parse Galaxy
        # TODO: Parse Object

        for i, attribute in enumerate(prepared_event['attributes']):
            prepared_event['attributes'][i] = cls.parse_event_attribute(attribute)

        prepared_event = MispAPIUtils.translate_dictionary(prepared_event, event_response_translator)
        return MispEvent.model_validate(prepared_event)

    @classmethod
    def parse_event_attribute(cls, event_attribute: dict) -> MispEventAttribute:
        prepared_event_attribute: dict = {key: event_attribute[key] for key in event_attribute.keys() - {'Tag'}}

        attribute_id: int = prepared_event_attribute['id']
        tags: list[tuple] = []
        for tag in event_attribute['Tag']:
            tag_relationship: dict = {
                'attribute_id': attribute_id,
                'tag_id': tag['id'],
                'local': tag['local'],
            }

            if 'tag_relationship' in tag.keys():
                tag_relationship['tag_relationship'] = tag['tag_relationship']

            tags.append((tag, tag_relationship))

        prepared_event_attribute['tags'] = tags

        return MispEventAttribute.model_validate(prepared_event_attribute)

    @staticmethod
    def parse_user(response: dict) -> MispUser:
        user_response: dict = response['User']
        role_response: dict = response['Role']

        del user_response['role_id']

        user_response_translator: dict[str, str] = {
            'autoalert': 'auto_alert',
            'gpgkey': 'gpg_key',
            'termsaccepted': 'terms_accepted',
            'contactalert': 'contact_alert',
            'orgAdmins': 'org_admins'
        }
        modified_user_response = MispAPIUtils.translate_dictionary(user_response, user_response_translator)

        role: MispRole = MispRole.model_validate(role_response)

        modified_user_response['role'] = role
        return MispUser.model_validate(modified_user_response)

    @staticmethod
    def parse_server(response: dict) -> MispServer:
        server_response: dict = response['Server']
        organisation_response: dict = response['Organisation']
        remote_org_response: dict = response['RemoteOrg']

        del server_response['organisation_id']
        del server_response['remote_org_id']

        server_response_translator: dict[str, str] = {
            'lastpulledid': 'last_pulled_id',
            'lastpushedid': 'last_pushed_id'
        }

        modified_server_response = MispAPIUtils.translate_dictionary(server_response, server_response_translator)
        organisation: MispOrganisation = MispOrganisation.model_validate(organisation_response)
        remote_org: MispOrganisation = MispOrganisation.model_validate(remote_org_response)
        modified_server_response['organisation'] = organisation
        modified_server_response['remote_org'] = remote_org
        return MispServer.model_validate(modified_server_response)

    @staticmethod
    def parse_sharing_group(response: dict) -> MispSharingGroup:

        modified_sharing_group_response: dict = response['SharingGroup'].copy()

        msgs: list[MispSharingGroupServer] = []
        for server in response['SharingGroupServer']:
            msgs.append(MispAPIParser.parse_sharing_group_server(server))

        modified_sharing_group_response['sharing_group_servers'] = msgs

        msgo: list[MispSharingGroupOrg] = []
        for org in response['SharingGroupOrg']:
            msgo.append(MispAPIParser.parse_sharing_group_org(org))

        modified_sharing_group_response['sharing_group_orgs'] = msgo

        modified_sharing_group_response['org_count'] = len(modified_sharing_group_response['sharing_group_orgs'])

        misp_sharing_group: MispSharingGroup = MispSharingGroup.model_validate(modified_sharing_group_response)
        return misp_sharing_group

    @staticmethod
    def parse_sharing_group_server(response: dict) -> MispSharingGroupServer:

        modified_sharing_group_server_response: dict = response.copy()

        del modified_sharing_group_server_response['Server']
        del modified_sharing_group_server_response['id']

        modified_sharing_group_server_response['server_name'] = response['Server']['name']

        return MispSharingGroupServer.model_validate(modified_sharing_group_server_response)

    @staticmethod
    def parse_sharing_group_org(response: dict) -> MispSharingGroupOrg:

        modified_sharing_group_orgs_response: dict = response.copy()
        del modified_sharing_group_orgs_response['Organisation']

        org: MispOrganisation = MispAPIParser.parse_organisation(response['Organisation'])

        modified_sharing_group_orgs_response['org_uuid'] = org.uuid
        modified_sharing_group_orgs_response['org_name'] = org.name

        return MispSharingGroupOrg.model_validate(modified_sharing_group_orgs_response)

    @staticmethod
    def parse_organisation(response: dict) -> MispOrganisation:
        return MispOrganisation.model_validate(response)

    @staticmethod
    def parse_galaxy_cluster(response: dict) -> MispGalaxyCluster:
        galaxy_cluster_response: dict = response['GalaxyCluster']
        galaxy_response: dict = galaxy_cluster_response['Galaxy'].copy()
        galaxy_elements_response: list[dict] = galaxy_cluster_response['GalaxyElement'].copy()
        galaxy_cluster_relations_response: list[dict] = galaxy_cluster_response['GalaxyClusterRelation'].copy()
        org_response: dict = response['Org'].copy()
        org_c_response: dict = response['Orgc'].copy()

        del galaxy_cluster_response['Galaxy']
        del galaxy_cluster_response['GalaxyElement']
        del galaxy_cluster_response['GalaxyClusterRelation']
        del galaxy_cluster_response['Org']
        del galaxy_cluster_response['Orgc']

        del galaxy_cluster_response['org_id']
        del galaxy_cluster_response['orgc_id']
        del galaxy_cluster_response['galaxy_id']

        galaxy: MispGalaxy = MispGalaxy.model_validate(galaxy_response)
        galaxy_elements: list[MispTag] = []
        for galaxy_element in galaxy_elements_response:
            galaxy_elements.append(MispGalaxyElement.model_validate(galaxy_element))
        galaxy_cluster_relations: list[MispTag] = []
        for galaxy_cluster_relation in galaxy_cluster_relations_response:
            galaxy_cluster_relations.append(MispTag.model_validate(galaxy_cluster_relation))
        organisation: MispOrganisation = MispOrganisation.model_validate(org_response)
        organisation_c: MispOrganisation = MispOrganisation.model_validate(org_c_response)

        galaxy_cluster_response['galaxy'] = galaxy
        galaxy_cluster_response['galaxy_elements'] = galaxy_elements
        galaxy_cluster_response['galaxy_cluster_relations'] = galaxy_cluster_relations
        galaxy_cluster_response['organisation'] = organisation
        galaxy_cluster_response['organisation_c'] = organisation_c
        return MispGalaxyCluster.model_validate(galaxy_cluster_response)

    @staticmethod
    def parse_event_view(response: dict) -> MispEventView:
        event_view_response: dict = response.copy()
        event_tags_response: list[dict] = event_view_response['EventTag'].copy()
        org_response: dict = response['Org'].copy()
        org_c_response: dict = response['Orgc'].copy()

        del event_view_response['Org']
        del event_view_response['Orgc']
        del event_view_response['EventTag']

        del event_view_response['org_id']
        del event_view_response['orgc_id']

        event_tags: list[MispTag] = []
        for event_tag_relation in event_tags_response:
            event_tags.append(MispTag.model_validate(event_tag_relation))
        organisation: MispOrganisation = MispOrganisation.model_validate(org_response)
        organisation_c: MispOrganisation = MispOrganisation.model_validate(org_c_response)

        event_view_response['event_tags'] = event_tags
        event_view_response['organisation'] = organisation
        event_view_response['organisation_c'] = organisation_c
        return MispEventView.model_validate(event_view_response)

    @staticmethod
    def parse_sighting(response: dict) -> MispSighting:
        organisation_response: dict = response['Organisation']
        del response['Organisation']

        organisation: MispOrganisation = MispOrganisation.model_validate(organisation_response)
        response['organisation'] = organisation
        return MispSighting.model_validate(response)
