from email.message import EmailMessage

from mmisp.worker.jobs.email.email_worker import email_worker
from mmisp.worker.jobs.email.utility.smtp_client import SmtpClient
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

        for event_tag_name in event.eventTags.name:
            if email_subject_tlp_string in event_tag_name:
                return event_tag_name

        return email_subject_tlp_string if email_subject_tlp_string is not None else "tlp:amber"

    @staticmethod
    def sendEmails(misp_email_address: str, email_password: str, smtp_port: int, smtp_host: str,
                   receiver_ids: list[int], email_msg: EmailMessage) -> None:

        smtp_client: SmtpClient = SmtpClient(smtp_host, smtp_port)

        smtp_client.openSmtpConnection(misp_email_address, email_password)

        for receiver_id in receiver_ids:
            user: MispUser = email_worker.misp_api.get_user(receiver_id)
            email_msg['To'] = user.email
            smtp_client.sendEmail(misp_email_address, user.email, email_msg.as_string())

        smtp_client.closeSmtpConnection()
