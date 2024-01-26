from email.message import EmailMessage

from mmisp.worker.misp_dataclasses.misp_event import MispEvent
from mmisp.worker.misp_dataclasses.misp_user import MispUser

"""
Provides functionality built emails.
"""


class UtilityEmail:

    """
    Returns a subject of an email based on the eventTags of the mispEvent object.
    """
    @staticmethod
    def get_email_subject_mark_for_event(event: MispEvent, email_subject_tlp_string: str) -> str:
        return "subjekt"
