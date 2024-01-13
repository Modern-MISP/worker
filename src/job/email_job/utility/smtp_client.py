import smtplib
from typing import Self

from src.misp_dataclasses.misp_user import MispUser

"""
    SMTPClient implements the singleton patter. It is used to send emails with a smtp server, therefore it is 
    important that only one smtp server exists.
"""


class SMTPClient:

    __instance: Self = None

    __smtp: smtplib = None

    """
    Returns the SMTPClient instance itself. If the SMTPClient object is already created it will be returned, if not, 
    it will be created
    """
    @classmethod
    def get_instance(cls, misp_email: str, misp_email_password: str, smtp_port: int, smtp_host: str) -> Self:
        if cls.__instance is None:
            SMTPClient.__instance = SMTPClient()
        return cls.__instance

    """
    Sends emails with a smtp.
    Returns True if all emails were successfully sent, false if not
    """
    def send_mail(self, message: str, receivers: list[MispUser]):
        # message.as_string()
        # TODO gegebenenfalls user validieren ka warum, problem für später
        # TODO passawort und misp email wahrschienlich in config, muss fragen
        self.__smtp.sendmail()

    def __init__(self, misp_email: str, misp_email_password: str, smtp_port: int, smtp_host: str):
        __smtp = smtplib.SMTP()
