import unittest

from mmisp.worker.jobs.email.alert_email_job import alert_email_job
from mmisp.worker.jobs.email.email_worker import EmailWorker
from mmisp.worker.jobs.email.job_data import AlertEmailData
from mmisp.worker.misp_dataclasses.misp_event import MispEvent
from mmisp.worker.misp_dataclasses.misp_user import MispUser


class TestBasicAlertEmailJob(unittest.TestCase):

    def test_alert_email_job(self):
        """
        user1: MispUser = MispUser(id=1, org_id=1, server_id=0, email="lerngruppeMisp@outlook.de",
                                   autoalert=False,
                                   password="password",
                                   authkey="WLubSZRh4xfovca2NhdvBnQ5BG9TJpDmKqjAKXTf",
                                   invited_by=0,
                                   gpgkey=None,
                                   certif_public="",
                                   nids_sid=4000000,
                                   termsaccepted=False,
                                   newsread=0,
                                   role_id=1,
                                   change_pw=False,
                                   contactalert=False,
                                   disabled=False,
                                   expiration=None,
                                   current_login=1706730471,
                                   last_login=1706728690,
                                   last_api_access=1706742153,
                                   force_logout=False,
                                   date_created=None,
                                   date_modified=1706728169,
                                   last_pw_change=1699633563)

        user2: MispUser = MispUser(id=2, org_id=1, server_id=8, email="lerngruppeMisp@outlook.de",
                                   auto_alert=False,
                                   password="password",
                                   authkey="WLubSZRh4xfovcalldkmldvBnQ5BG9TJpDmKqjAKXTf",
                                   invited_by=0,
                                   gpgkey=None,
                                   certif_public="",
                                   nids_sid=4000000,
                                   termsaccepted=True,
                                   newsread=0,
                                   role_id=1,
                                   change_pw=False,
                                   contactalert=True,
                                   disabled=False,
                                   expiration=None,
                                   current_login=1706730471,
                                   last_login=1706728690,
                                   last_api_access=1706742153,
                                   force_logout=True,
                                   date_created=None,
                                   date_modified=1706728169,
                                   last_pw_change=1699633563)

        event: MispEvent = MispEvent(id=2,
                                     org_id=1,
                                     date=2023 - 11 - 16,
                                     info="sdfas",
                                     uuid="fb2fa4a2-66e5-48a3-9bdd-5c5ce78e11e8",
                                     published=False,
                                     analysis=0,
                                     attribute_count=6,
                                     orgc_id=1,
                                     timestamp=1706736785,
                                     distribution=1,
                                     sharing_group_id=0,
                                     proposal_email_lock=False,
                                     locked=False,
                                     threat_level_id=4,
                                     publish_timestamp=1700496633,
                                     sighting_timestamp=0,
                                     disable_correlation=False,
                                     extends_uuid="",
                                     protected=None, )

        old_publish: str = "test"

        data: AlertEmailData = AlertEmailData(old_publish=old_publish, event_id=event.id, receiver_ids=[user1.id,
                                                                                                        user2.id])
        email_worker: EmailWorker = EmailWorker()

        alert_email_job(data)

        self.assertEqual(True, True)
        """

if __name__ == '__main__':
    unittest.main()
