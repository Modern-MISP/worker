from src.misp_dataclasses.misp_event import MispEvent
from src.misp_dataclasses.misp_user import MispUser

"""
Provides functionality built emails.
"""


class UtilityEmail:

    """
    Returns a subject of an email based on the eventTags of the mispEvent object.
    """
    @staticmethod
    def get_email_subject_mark_for_event(event: MispEvent) -> str:
        return "subjekt"

    """
    Returns the baseurl of Misp, if it is set. A exception wil be thrown if not baseurl is set.
    """
    @staticmethod
    def get_announce_baseurl() -> str:  # TODO exeption

        """$baseurl = '';
            if (!empty(Configure::read('MISP.external_baseurl'))) {
                $baseurl = Configure::read('MISP.external_baseurl');
            } else if (!empty(Configure::read('MISP.baseurl'))) {
             $baseurl = Configure::read('MISP.baseurl');
            }
            return $baseurl;
     """

        return "url"

    """
    Returns users with active contactalert
    """
    @staticmethod
    def get_users_with_active_contactalert(users: list[MispUser]) -> list[MispUser]:
        pass