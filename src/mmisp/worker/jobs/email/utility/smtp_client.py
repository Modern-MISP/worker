import smtplib

from mmisp.worker.misp_dataclasses.misp_user import MispUser

"""
    SMTPClient implements the singleton patter. It is used to send emails with a smtp server, therefore it is 
    important that only one smtp server exists.
"""


class SMTPClient:

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
        self.__smtp = smtplib.SMTP()
