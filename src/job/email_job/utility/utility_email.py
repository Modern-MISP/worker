from src.misp_dataclasses.misp_event import MispEvent

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
