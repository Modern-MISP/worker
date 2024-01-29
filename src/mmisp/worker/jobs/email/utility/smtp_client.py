import smtplib
from smtplib import SMTP


class SmtpClient:

    def __init__(self, host: str, port: int):
        self.__smtp: SMTP = smtplib.SMTP(host, port)

    def openSmtpConnection(self, misp_email: str, password: str):
        self.__smtp.ehlo()
        self.__smtp.starttls()
        self.__smtp.ehlo()
        self.__smtp.login(user=misp_email, password=password)

    def sendEmail(self, from_addr: str, to_addr: str, email: str):
        self.__smtp.sendmail(from_addr, to_addr, email)

    def closeSmtpConnection(self):
        self.__smtp.close()
