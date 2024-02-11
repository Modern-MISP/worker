import smtplib
from smtplib import SMTP


class SmtpClient:
    """
    Provides methods to build an SMTP connection to send emails.
    """

    def __init__(self, host: str, port: int):
        """
        Initializes a new SMTP object.
        :param port: is the port of the SMTP server
        :type port: int
        :param host: is the host of the SMTP server
        :type host: str
        """
        self.__smtp: SMTP = smtplib.SMTP(host, port)

    def open_smtp_connection(self, misp_email: str, password: str):
        """
        Connects to the SMTP server and logs in with the misp email.
        :param misp_email: is the email of misp
        :type misp_email: str
        :param password: is the password of the email
        :type password: str
        """
        self.__smtp.ehlo()
        self.__smtp.starttls()
        self.__smtp.ehlo()
        self.__smtp.login(user=misp_email, password=password)

    def send_email(self, from_addr: str, to_addr: str, email: str):
        """
        Sends an email.
        :param from_addr: is the address of the sender (misp email9
        :type from_addr: str
        :param to_addr: is the address of the receiver (user)
        :type to_addr: str
        :param email: is the content of the email
        :type email: str
        """
        self.__smtp.sendmail(from_addr, to_addr, email)

    def close_smtp_connection(self):
        """
        Closes the SMTP Connection.
        """
        self.__smtp.close()
