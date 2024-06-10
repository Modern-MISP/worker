from email.message import EmailMessage

from mmisp.worker.jobs.email.email_worker import email_worker
from mmisp.worker.jobs.email.utility.smtp_client import SmtpClient
from mmisp.worker.misp_database.misp_api import MispAPI
from mmisp.api_schemas.events import AddEditGetEventDetails
from mmisp.worker.misp_dataclasses.misp_user import MispUser


class UtilityEmail:
    """
    Provides functionality to built emails.
    """

    @staticmethod
    def get_email_subject_mark_for_event(event: AddEditGetEventDetails, email_subject_string: str) -> str:
        """
        Returns the tlp tag of the given event as a subject for emails.

        :param event: the event to get the subject for
        :type event: AddEditGetEventDetails
        :param email_subject_string: is the tlp string to search
        :type email_subject_string: str
        :return: the tlp tag of the event
        :rtype: str
        """
        if event.tags is not None:
            for tag in event.tags:
                if email_subject_string in tag[0].name:
                    return tag[0].name

        return email_subject_string

    @staticmethod
    def send_emails(misp_email_address: str, email_password: str, smtp_port: int, smtp_host: str,
                    receiver_ids: list[int], email_msg: EmailMessage) -> None:
        """
        Sends emails to the given users by opening an SMTP connection

        :param misp_email_address: is the email of misp
        :type misp_email_address: str
        :param email_password: is the password of misp
        :type email_password: str
        :param smtp_port: is the port of the SMTP server
        :type smtp_port: int
        :param smtp_host: is the host of the SMTP server
        :type smtp_host: str
        :param receiver_ids: are the ids of the users who get the email
        :type receiver_ids: list[int]
        :param email_msg: is the email which will be sent
        :type email_msg: EmailMessage
        """
        smtp_client: SmtpClient = SmtpClient(smtp_host, smtp_port)

        smtp_client.open_smtp_connection(misp_email_address, email_password)

        misp_api: MispAPI = email_worker.misp_api

        for receiver_id in receiver_ids:
            user: MispUser = misp_api.get_user(receiver_id)
            email_msg['To'] = user.email
            smtp_client.send_email(misp_email_address, user.email, email_msg.as_string())
            del email_msg['To']

        smtp_client.close_smtp_connection()
