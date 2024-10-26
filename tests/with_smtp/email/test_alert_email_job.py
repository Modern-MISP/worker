import requests

from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.jobs.email.alert_email_job import alert_email_job
from mmisp.worker.jobs.email.job_data import AlertEmailData


def test_alert_email_job(init_api_config, event, user, site_admin_user):
    data: AlertEmailData = AlertEmailData(event_id=event.id, receiver_ids=[user.id],
                                          old_publish=1722088063)
    alert_email_job(UserData(user_id=site_admin_user.id), data)

    response = requests.get("http://localhost:9000/api/messages")

    print("emailbonobo", response.json())
    assert response.status_code == 200

