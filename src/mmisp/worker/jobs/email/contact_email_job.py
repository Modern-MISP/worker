from mmisp.worker.api.job_router.input_data import UserData
from mmisp.worker.controller.celery.celery import celery_app
from mmisp.worker.jobs.email.email_worker import email_worker
from mmisp.worker.jobs.email.job_data import ContactEmailData
from mmisp.worker.jobs.email.utility.smtp_client import SMTPClient


"""
Provides functionality for ContactEmailJob.
"""

smtp_client = SMTPClient.get_instance(email_worker.config.misp_email_address,
                                      email_worker.config.email_password,
                                      email_worker.config.smtp_port,
                                      email_worker.config.smtp_host)


@celery_app.task
def contact_email_job(requester: UserData, data: ContactEmailData):
    """
    Prepares the contact email and sends it.
    """

    # getEvent8id)

    # requester = getUser(user_id)

    # for receiver_ids: recivers = getUSer(id)

    # getEmailSubjektMarkForEvent()

    # getAnnounceBaseurl()

    # smtp.getInstance

    # smtp.sendEmail
    pass

    """edited"""
