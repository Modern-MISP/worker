import smtplib
from email.message import EmailMessage


class SMTPClient:

    __instance: "SMTPClient" = None

    __smtp: smtplib = None


    @classmethod
    def get_instance(cls) -> "SMTPClient":
        if cls.__instance is None:
            SMTPClient.__instance = SMTPClient()
        return cls.__instance

    def send_mail(self, message: EmailMessage, receivers: list[str]) -> bool:
        #message.as_string()
        # TODO gegebenenfalls user validieren ka warum, problem für später
        # TODO passawort und misp email wahrschienlich in config, muss fragen
        self.__smtp.sendmail()

    def __init__(self):
        smtp = smtplib.SMTP()
