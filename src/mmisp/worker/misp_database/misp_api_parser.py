from mmisp.worker.misp_database.misp_api_utils import MispAPIUtils
from mmisp.worker.misp_dataclasses.misp_attribute import MispEventAttribute
from mmisp.worker.misp_dataclasses.misp_role import MispRole
from mmisp.worker.misp_dataclasses.misp_server import MispServer
from mmisp.worker.misp_dataclasses.misp_tag import MispTag, AttributeTagRelationship
from mmisp.worker.misp_dataclasses.misp_user import MispUser


class MispAPIParser:

    @classmethod
    def parse_event_attribute(cls, event_attribute: dict) -> MispEventAttribute:
        partly_parsed_attribute: dict = {key: event_attribute[key] for key in event_attribute.keys() - {'Tag'}}
        attribute_id: int = partly_parsed_attribute['id']

        tags: list[tuple[MispTag, AttributeTagRelationship]] = []
        partly_parsed_attribute['Tag'] = tags
        for tag in event_attribute['Tag']:
            parsed_tag: MispTag = cls.parse_tag(tag)
            tag_relationship: dict = {
                'attribute_id': attribute_id,
                'tag_id': parsed_tag.id,
                'local': tag['local'],
            }

            if 'tag_relationship' in tag.keys():
                tag_relationship['tag_relationship'] = tag['tag_relationship']

            parsed_tag_relationship: AttributeTagRelationship =\
                (AttributeTagRelationship.model_validate(tag_relationship))

            tags.append((parsed_tag, parsed_tag_relationship))

        attribute: MispEventAttribute = MispEventAttribute.model_validate(partly_parsed_attribute)
        return attribute

    @staticmethod
    def parse_tag(tag: dict) -> MispTag:
        return MispTag.model_validate(tag)

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
        server_response: dict = response['User']
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

"""
    def get_sharing_group(response: dict) -> MispSharingGroup:
        sharing_group_response_translator: dict[str, str] = {
            'SharingGroupServer': '',
            'SharingGroupOrg': 'sharing_group_orgs'
        }

        modified_sharing_group_response: dict = response['SharingGroup']

        print(modified_sharing_group_response)



        modified_sharing_group_response['sharing_group_servers'] = response['SharingGroupServer']

        print(modified_sharing_group_response)




        modified_sharing_group_response['sharing_group_orgs'] = response['SharingGroupOrg']

        #print(modified_sharing_group_response)

        modified_sharing_group_response['org_count'] = len(modified_sharing_group_response['sharing_group_orgs'])

        return MispSharingGroup.model_validate(modified_sharing_group_response)

    def get_sharing_group_servers(response: dict) -> MispSharingGroupServer:
        pass
        
"""