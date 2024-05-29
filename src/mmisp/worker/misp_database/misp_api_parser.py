from mmisp.api_schemas.objects.get_object_response import ObjectWithAttributesResponse
from mmisp.api_schemas.tags.get_tag_response import TagViewResponse
from mmisp.api_schemas.users.user import User
from mmisp.api_schemas.users.users_view_me_response import UsersViewMeResponse
from mmisp.db.models.role import Role
from mmisp.worker.misp_database.misp_api_utils import MispAPIUtils
from mmisp.worker.misp_dataclasses.misp_event import MispEvent
from mmisp.worker.misp_dataclasses.misp_event_attribute import MispEventAttribute
from mmisp.worker.misp_dataclasses.misp_galaxy import MispGalaxy
from mmisp.worker.misp_dataclasses.misp_galaxy_cluster import MispGalaxyCluster
from mmisp.worker.misp_dataclasses.misp_galaxy_element import MispGalaxyElement
from mmisp.worker.misp_dataclasses.misp_object_attribute import MispObjectAttribute
from mmisp.worker.misp_dataclasses.misp_organisation import MispOrganisation
from mmisp.worker.misp_dataclasses.misp_proposal import MispProposal
from mmisp.worker.misp_dataclasses.misp_role import MispRole
from mmisp.worker.misp_dataclasses.misp_server import MispServer
from mmisp.worker.misp_dataclasses.misp_sharing_group import ViewUpdateSharingGroupLegacyResponse
from mmisp.worker.misp_dataclasses.misp_sharing_group_org import MispSharingGroupOrg
from mmisp.worker.misp_dataclasses.misp_sharing_group_server import MispSharingGroupServer
from mmisp.worker.misp_dataclasses.misp_sighting import MispSighting
from mmisp.worker.misp_dataclasses.event_tag_relationship import EventTagRelationship
from mmisp.worker.misp_dataclasses.misp_user import MispUser


class MispAPIParser:

    @classmethod
    def parse_event(cls, event: dict) -> MispEvent:
        """
        Parse the event response dictionary from the MISP API to a MispEvent object

        :param event: dictionary containing the event response from the MISP API
        :type event: dict
        :return: returns a MispEvent object with the values from the event dictionary
        :rtype: MispEvent
        """
        prepared_event: dict = event.copy()
        event_response_translator: dict = {
            'Org': 'org',
            'Orgc': 'orgc',
            'Attribute': 'attributes',
            'ShadowAttribute': 'shadow_attributes',
            'RelatedEvent': 'related_events',
            'Galaxy': 'clusters',
            'Object': 'objects',
            'EventReport': 'reports',
            'Tag': 'tags',
            'CryptographicKey': 'cryptographic_key'
        }
        if "Galaxy" in prepared_event:
            for i, galaxy in enumerate(prepared_event['Galaxy']):
                prepared_event['Galaxy'][i] = cls.parse_galaxy(galaxy)

        if "Object" in prepared_event:
            for i, object in enumerate(prepared_event['Object']):
                prepared_event['Object'][i] = cls.parse_object(object)

        if "Attribute" in prepared_event:
            for i, attribute in enumerate(prepared_event['Attribute']):
                prepared_event['Attribute'][i] = cls.parse_event_attribute(attribute)

        if "RelatedEvent" in prepared_event:
            for i, related_event in enumerate(prepared_event['RelatedEvent']):
                prepared_event['RelatedEvent'][i] = cls.parse_event(related_event["Event"])

        if "Tag" in prepared_event:
            for i, tag in enumerate(prepared_event['Tag']):
                saved_tag = cls.parse_tag(tag)
                tag_relationship: EventTagRelationship = EventTagRelationship(
                    event_id=prepared_event['id'],
                    tag_id=saved_tag.id
                )
                prepared_event['Tag'][i] = tuple((saved_tag, tag_relationship))
        prepared_event = MispAPIUtils.translate_dictionary(prepared_event, event_response_translator)
        return MispEvent.model_validate(prepared_event)

    @classmethod
    def parse_tag(cls, tag: dict) -> TagViewResponse:
        """
        Parse the tag response dictionary from the MISP API to a MispTag object

        :param tag: dictionary containing the tag response from the MISP API
        :type tag: dict
        :return: returns a MispTag object with the values from the tag dictionary
        :rtype: TagViewResponse
        """

        return TagViewResponse.model_validate(tag)

    @staticmethod
    def parse_object(object_response: ObjectWithAttributesResponse) -> ObjectWithAttributesResponse:
        """
        :param object_response: object response from the MISP API
        :type object_response: ObjectWithAttributesResponse
        :return: returns a ObjectWithAttributeResponse object with the values from the object response
        :rtype: ObjectWithAttributesResponse
        """

        attributes: list[MispObjectAttribute] = []
        for attribute in object_response.Attribute:
            attributes.append(MispObjectAttribute(
                id=attribute.id,
                type=object_response.type,
                category=object_response.category,
                to_ids=object_response.to_ids,
                uuid=object_response.uuid,
                event_id=object_response.event_id,
                distribution=object_response.distribution,
                timestamp=object_response.timestamp,
                comment=object_response.comment,
                sharing_group_id=object_response.sharing_group_id,
                deleted=object_response.deleted,
                disable_correlation=object_response.disable_correlation,
                object_id=object_response.object_id,
                object_relation=object_response.object_relation,
                first_seen=object_response.first_seen,
                last_seen=object_response.last_seen,
                value=object_response.value
            ))

        return ObjectWithAttributesResponse(
            id=object_response.id,
            name=object_response.name,
            meta_category=object_response.meta_category,
            description=object_response.description,
            template_uuid=object_response.template_uuid,
            template_version=object_response.template_version,
            event_id=object_response.event_id,
            uuid=object_response.uuid,
            timestamp=object_response.timestamp,
            distribution=object_response.distribution,
            sharing_group_id=object_response.sharing_group_id,
            comment=object_response.comment,
            deleted=object_response.deleted,
            first_seen=object_response.first_seen,
            last_seen=object_response.last_seen,
            attributes=attributes
        )

    @classmethod
    def parse_event_attribute(cls, event_attribute: dict) -> MispEventAttribute:
        """
        Parse the event attribute response dictionary from the MISP API to a MispEventAttribute object

        :param event_attribute: dictionary containing the event attribute response from the MISP API
        :type event_attribute: dict
        :return: returns a MispEventAttribute object with the values from the event attribute dictionary
        :rtype: MispEventAttribute
        """
        prepared_event_attribute: dict = {key: event_attribute[key] for key in event_attribute.keys() - {'Tag'}}
        attribute_id: int = prepared_event_attribute['id']
        if 'Tag' in event_attribute.keys():
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
    def parse_user(response_user_view_me: UsersViewMeResponse) -> MispUser:
        response_user: User = response_user_view_me.User
        response_role: Role = response_user_view_me.Role
        return MispUser(id=response_user.id,
                        password=response_user.password,
                        org_id=response_user.org_id,
                        email=response_user.email,
                        auto_alert=response_user.autoalert,
                        invited_by=int(response_user.invited_by),
                        gpg_key=response_user.gpgkey,
                        certif_public=response_user.certif_public,
                        nids_sid=None,
                        terms_accepted=response_user.termsaccepted,
                        news_read=0,
                        role=MispRole(id=response_role.id,
                                      name=response_role.name,
                                      created=response_role.created,
                                      modified=response_role.modified,
                                      perm_add=response_role.perm_add,
                                      perm_modify=response_role.perm_modify,
                                      perm_modify_org=response_role.perm_modify_org,
                                      perm_publish=response_role.perm_publish,
                                      perm_delegate=response_role.perm_delegate,
                                      perm_sync=response_role.perm_sync,
                                      perm_admin=response_role.perm_admin,
                                      perm_audit=response_role.perm_audit,
                                      perm_auth=response_role.perm_auth,
                                      perm_site_admin=response_role.perm_site_admin,
                                      perm_regexp_access=response_role.perm_regexp_access,
                                      perm_tagger=response_role.perm_tagger,
                                      perm_template=response_role.perm_template,
                                      perm_sharing_group=response_role.perm_sharing_group,
                                      perm_tag_editor=response_role.perm_tag_editor,
                                      perm_sighting=response_role.perm_sighting,
                                      perm_object_template=response_role.perm_object_template,
                                      default_role=response_role.default_role,
                                      memory_limit=response_role.memory_limit,
                                      max_execution_time=response_role.max_execution_time,
                                      restricted_to_site_admin=response_role.restricted_to_site_admin,
                                      perm_publish_zmq=response_role.perm_publish_zmq,
                                      perm_publish_kafka=response_role.perm_publish_kafka,
                                      perm_decaying=response_role.perm_decaying,
                                      enforce_rate_limit=response_role.enforce_rate_limit,
                                      rate_limit_count=response_role.rate_limit_count,
                                      perm_galaxy_editor=response_role.perm_galaxy_editor,
                                      perm_warning_list=response_role.perm_warninglist,
                                      perm_view_feed_correlations=response_role.perm_view_feed_correlations,
                                      permission=response_role.permission,
                                      permission_description=response_role.permission_description),
                        change_pw=response_user.change_pw,
                        contact_alert=response_user.contactalert,
                        disabled=response_user.disabled,
                        expiration=response_user.expiration,
                        current_login=response_user.current_login,
                        last_login=response_user.last_login,
                        force_logout=response_user.force_logout,
                        date_created=response_user.date_created,
                        date_modified=response_user.date_modified,
                        sub=None,
                        external_auth_required=response_user.external_auth_required,
                        external_auth_key=response_user.external_auth_key,
                        last_api_access=response_user.last_api_access,
                        notification_daily=response_user.notification_daily,
                        notification_weekly=response_user.notification_weekly,
                        notification_monthly=response_user.notification_monthly,
                        totp=response_user.totp,
                        hotp_counter=response_user.hotp_counter,
                        last_pw_change=response_user.last_pw_change)

    @staticmethod
    def parse_server(response: dict) -> MispServer:
        """
        Parse the server response dictionary from the MISP API to a MispServer object

        :param response:  dictionary containing the server response from the MISP API
        :type response:  dict
        :return:  returns a MispServer object with the values from the server dictionary
        :rtype:  MispServer
        """
        server_response: dict = response["Server"]
        organisation_response: dict = response['Organisation']
        remote_org_response: dict = response['RemoteOrg']

        del server_response['org_id']
        del server_response['remote_org_id']

        server_response_translator: dict[str, str] = {
            'lastpulledid': 'last_pulled_id',
            'lastpushedid': 'last_pushed_id'
        }

        modified_server_response = MispAPIUtils.translate_dictionary(server_response, server_response_translator)
        organisation: MispOrganisation = MispOrganisation.model_validate(organisation_response)
        remote_org: MispOrganisation = MispOrganisation.model_validate(remote_org_response)
        modified_server_response['organization'] = organisation
        modified_server_response['remote_organization'] = remote_org
        return MispServer.model_validate(modified_server_response)

    @staticmethod
    def parse_sharing_group(response: dict) -> ViewUpdateSharingGroupLegacyResponse:
        """
        Parse the sharing group response dictionary from the MISP API to a MispSharingGroup object

        :param response:  dictionary containing the sharing group response from the MISP API
        :type response:  dict
        :return:  returns a MispSharingGroup object with the values from the sharing group dictionary
        :rtype:  ViewUpdateSharingGroupLegacyResponse
        """

        modified_sharing_group_response: dict = response['SharingGroup'].copy()

        msgs: list[MispSharingGroupServer] = []
        for server in response['SharingGroupServer']:
            msgs.append(MispAPIParser.parse_sharing_group_server(server))

        modified_sharing_group_response['sharing_group_servers'] = msgs

        msgo: list[MispSharingGroupOrg] = []
        for org in response['SharingGroupOrg']:
            msgo.append(MispAPIParser.parse_sharing_group_org(org))

        modified_sharing_group_response['sharing_group_orgs'] = msgo
        org_response: dict = response['Organisation']
        modified_sharing_group_response["organisation"] = MispOrganisation.model_validate(org_response)
        modified_sharing_group_response['org_count'] = len(modified_sharing_group_response['sharing_group_orgs'])

        misp_sharing_group: ViewUpdateSharingGroupLegacyResponse = ViewUpdateSharingGroupLegacyResponse.model_validate(modified_sharing_group_response)
        return misp_sharing_group

    @staticmethod
    def parse_sharing_group_server(response: dict) -> MispSharingGroupServer:
        """
        Parse the sharing group server response dictionary from the MISP API to a MispSharingGroupServer object

        :param response:  dictionary containing the sharing group server response from the MISP API
        :type response:     dict
        :return:    returns a MispSharingGroupServer object with the values from the sharing group server dictionary
        :rtype:   MispSharingGroupServer
        """

        modified_sharing_group_server_response: dict = response.copy()
        del modified_sharing_group_server_response['Server']

        if len(response["Server"]) > 0 and "server_id" in response["Server"].keys():
            modified_sharing_group_server_response['server_id'] = response['Server']['id']

        return MispSharingGroupServer.model_validate(modified_sharing_group_server_response)

    @staticmethod
    def parse_sharing_group_org(response: dict) -> MispSharingGroupOrg:
        """
        Parse the sharing group org response dictionary from the MISP API to a MispSharingGroupOrg object

        :param response: dictionary containing the sharing group org response from the MISP API
        :type response:  dict
        :return:  returns a MispSharingGroupOrg object with the values from the sharing group org dictionary
        :rtype:  MispSharingGroupOrg
        """

        modified_sharing_group_orgs_response: dict = response.copy()
        del modified_sharing_group_orgs_response['Organisation']

        org: MispOrganisation = MispAPIParser.parse_organisation(response['Organisation'])

        modified_sharing_group_orgs_response['org_uuid'] = org.uuid
        modified_sharing_group_orgs_response['org_name'] = org.name

        return MispSharingGroupOrg.model_validate(modified_sharing_group_orgs_response)

    @staticmethod
    def parse_organisation(response: dict) -> MispOrganisation:
        """
        Parse the organisation response dictionary from the MISP API to a MispOrganisation object

        :param response: dictionary containing the organisation response from the MISP API
        :type response:  dict
        :return:  returns a MispOrganisation object with the values from the organisation dictionary
        :rtype:  MispOrganisation
        """
        return MispOrganisation.model_validate(response)

    @staticmethod
    def parse_galaxy_cluster(response: dict) -> MispGalaxyCluster:
        """
        Parse the galaxy cluster response dictionary from the MISP API to a MispGalaxyCluster object

        :param response:  dictionary containing the galaxy cluster response from the MISP API
        :type response:  dict
        :return:  returns a MispGalaxyCluster object with the values from the galaxy cluster dictionary
        :rtype:  MispGalaxyCluster
        """
        galaxy_cluster_response: dict = response
        galaxy_elements_response: list[dict] = galaxy_cluster_response['GalaxyElement'].copy()
        galaxy_cluster_relations_response: list[dict] = galaxy_cluster_response['GalaxyClusterRelation'].copy()
        org_response: dict = galaxy_cluster_response['Org'].copy()
        org_c_response: dict = galaxy_cluster_response['Orgc'].copy()
        galaxy_id: int = galaxy_cluster_response['Galaxy']['id']

        del galaxy_cluster_response['Galaxy']
        del galaxy_cluster_response['GalaxyElement']
        del galaxy_cluster_response['GalaxyClusterRelation']
        del galaxy_cluster_response['Org']
        del galaxy_cluster_response['Orgc']

        del galaxy_cluster_response['org_id']
        del galaxy_cluster_response['orgc_id']

        if galaxy_cluster_response['authors'] is None:
            galaxy_cluster_response['authors'] = []

        galaxy_elements: list[MispGalaxyElement] = []
        for galaxy_element in galaxy_elements_response:
            galaxy_elements.append(MispGalaxyElement.model_validate(galaxy_element))
        galaxy_cluster_relations: list[TagViewResponse] = []
        for galaxy_cluster_relation in galaxy_cluster_relations_response:
            galaxy_cluster_relations.append(TagViewResponse.model_validate(galaxy_cluster_relation))
        organisation: MispOrganisation = MispOrganisation.model_validate(org_response)
        organisation_c: MispOrganisation = MispOrganisation.model_validate(org_c_response)

        galaxy_cluster_response['galaxy_elements'] = galaxy_elements
        galaxy_cluster_response['galaxy_cluster_relations'] = galaxy_cluster_relations
        galaxy_cluster_response['organisation'] = organisation
        galaxy_cluster_response['organisation_c'] = organisation_c
        galaxy_cluster_response['galaxy_id'] = galaxy_id

        return MispGalaxyCluster.model_validate(galaxy_cluster_response)

    @staticmethod
    def parse_sighting(response: dict) -> MispSighting:
        """
        Parse the sighting response dictionary from the MISP API to a MispSighting object

        :param response:  dictionary containing the sighting response from the MISP API
        :type response:  dict
        :return:  returns a MispSighting object with the values from the sighting dictionary
        :rtype:  MispSighting
        """
        organisation_response: dict = response['Organisation']
        del response['Organisation']

        organisation: MispOrganisation = MispOrganisation.model_validate(organisation_response)
        response['organisation'] = organisation
        return MispSighting.model_validate(response)

    @classmethod
    def parse_proposal(cls, param: dict) -> MispProposal:
        """
        Parse the proposal response dictionary from the MISP API to a MispProposal object

        :param param:   dictionary containing the proposal response from the MISP API
        :type param:  dict
        :return:  returns a MispProposal object with the values from the proposal dictionary
        :rtype:  MispProposal
        """
        parse_proposal_response: dict = param.copy()

        del parse_proposal_response['Org']

        organisation: MispOrganisation = MispOrganisation.model_validate(param['Org'])
        parse_proposal_response['organisation'] = organisation
        return MispProposal.model_validate(parse_proposal_response)

    @classmethod
    def parse_galaxy(cls, param: dict) -> MispGalaxy:
        """
        Parse the galaxy response dictionary from the MISP API to a MispGalaxy object

        :param param:  dictionary containing the galaxy response from the MISP API
        :type param: dict
        :return: returns a MispGalaxy object with the values from the galaxy dictionary
        :rtype: MispGalaxy
        """
        galaxy_response: dict = param.copy()
        del galaxy_response['GalaxyCluster']
        return MispGalaxy.model_validate(galaxy_response)
