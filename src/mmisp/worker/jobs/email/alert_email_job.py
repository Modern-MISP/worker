from jinja2 import Template

from mmisp.worker.controller.celery.celery import celery_app
from mmisp.worker.jobs.email.email_worker import email_worker
from mmisp.worker.jobs.email.job_data import AlertEmailData
from mmisp.worker.jobs.email.utility.utility_email import UtilityEmail
from mmisp.worker.misp_database.misp_api import MispAPI
from mmisp.worker.misp_dataclasses.misp_event import MispEvent
from mmisp.worker.misp_dataclasses.misp_user import MispUser

"""
Provides functionality for AlertEmailJob.

Prepares the alert email and sends it.
"""


@celery_app.task
def alert_email_job(data: AlertEmailData):

    event: MispEvent = MispAPI.get_event(data.event_id)
    # getEvent(event_id)

    url: str  # TODO
    # get_announce_baseurl()

    tempo: str  # todo
    UtilityEmail.get_email_subject_mark_for_event(event, tempo)
    # getEmailSUbjektMark

    receivers: list[MispUser] = []
    for user_id in data.receiver_ids:
        receivers.append(MispAPI.get_user(user_id))
    # for receivers do: getUsers

    template: Template = email_worker.environment.get_template("alert_email_template.j2")


    email_worker.environment.fi
    # TODO
    template_str: str = template.render(data="abc")

    # email_worker.smtp_client.send_mail(template_str, receivers)
    # smt.getInstance

    # smtpSendEmail

    pass
