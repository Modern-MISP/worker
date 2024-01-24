from mmisp.worker.api.job_router.input_data import UserData
from mmisp.worker.controller.celery.celery import celery_app
from mmisp.worker.jobs.email.job_data import ContactEmailData


"""
Provides functionality for ContactEmailJob.
"""


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
