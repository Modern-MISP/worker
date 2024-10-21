# from unittest.mock import patch

import requests

from mmisp.worker.api.requests_schemas import UserData
from mmisp.worker.jobs.email.alert_email_job import alert_email_job
from mmisp.worker.jobs.email.job_data import AlertEmailData

# from mmisp.worker.jobs.email.utility.email_config_data import EmailConfigData


def test_alert_email_job(email_worker_mock, utility_mock):
    data: AlertEmailData = AlertEmailData(event_id=1, receiver_ids=[1], old_publish=1722088063)
    alert_email_job(UserData(user_id=66), data)

    response = requests.get("http://localhost:9000/api/messages")

    print(response.json())
    assert response.status_code == 200


def test_alert_email_job_sharing_group_id_none(email_worker_mock, utility_mock):
    data: AlertEmailData = AlertEmailData(event_id=3, receiver_ids=[1], old_publish=1722088063)
    alert_email_job(UserData(user_id=66), data)
