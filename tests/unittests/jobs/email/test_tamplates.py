import unittest

from jinja2 import Environment, PackageLoader, select_autoescape, Template

from tests.mocks.misp_database_mock import misp_api_mock
from tests.mocks.misp_database_mock.misp_api_mock import MispAPIMock


class TestTemplates(unittest.TestCase):
    __mmisp_url: str = "https://misp.local"

    def test_alert_email_template_multiple_tags_and_attributes(self):
        env: Environment = Environment(loader=PackageLoader('mmisp',
                                                            'worker/jobs/email/templates'),
                                       autoescape=select_autoescape())

        event = {
            "id": 1,
            "date": "2021-08-01",
            "distribution": 4,
            "orgc": {"name": "orgc_name"},
            "org": {"name": "org_name"},
            "tags": [({"name": "name"}, "relationship"), ({"name": "name2"}, "relationship2")],
            "analysis": "analysis",
            "info": "info",
            "related_events": [{"id": 1, "date": "test_date"}, {"id": 2, "date": "test_date2"}],
            "attributes": [{"to_ids": True, "value": "value", "type": "type", "timestamp": 55,
                            "category": "category", "tags": [({"name": "name1"}, "relationship"),
                                                             ({"name": "name1.2"}, "relationship2")]},
                           {"to_ids": False, "value": "value2", "type": "type2", "timestamp": 9,
                            "category": "category2", "tags": [({"name": "name2"}, "relationship2"),
                                                              ({"name": "name2.2"}, "relationship2.2"),
                                                              ({"name": "name2.3"}, "relationship2.2"),
                                                              ({"name": "name2.4"}, "relationship2.2")]},
                           {"to_ids": False, "value": "value3", "type": "type3", "timestamp": 7,
                            "category": "category3", "tags": [({"name": "name3"}, "relationship3"),
                                                              ({"name": "name3.2"}, "relationship2.3")]},
                           {"to_ids": True, "value": "value4", "type": "type4", "timestamp": 8,
                            "category": "category4", "tags": [({"name": "name4"}, "relationship4"),
                                                              ({"name": "name4.2"}, "relationship2.4")]}
                           ],
            "objects": [{"name": "object_name", "attributes": [{"to_ids": True, "value": "value", "type": "type",
                                                                "timestamp": 4, "category": "category",
                                                                "tags": [({"name": "name1"}, "relationship"),
                                                                         ({"name": "name1.2"}, "relationship2")]},
                                                               {"to_ids": False, "value": "value2", "type": "type2",
                                                                "timestamp": 8, "category": "category2",
                                                                "tags": [({"name": "name2"}, "relationship"),
                                                                         ({"name": "name2.2"}, "relationship2")]},
                                                               {"to_ids": True, "value": "value3", "type": "type3",
                                                                "timestamp": 7, "category": "category3",
                                                                "tags": [({"name": "name3"}, "relationship3"),
                                                                         ({"name": "name3.2"}, "relationship3"),
                                                                         ({"name": "name2.3"}, "relationship2.2"),
                                                                         ({"name": "name2.4"}, "relationship2.2")]},
                                                               {"to_ids": False, "value": "value4", "type": "type4",
                                                                "timestamp": 5, "category": "category4",
                                                                "tags": [({"name": "name4"}, "relationship"),
                                                                         ({"name": "name4.2"}, "relationship2")]}
                                                               ],
                         "meta_category": "meta_category", "timestamp": 2},
                        {"name": "object_name2", "attributes": [{"to_ids": True, "value": "value", "type": "type",
                                                                 "timestamp": 2, "category": "category",
                                                                 "tags": [({"name": "name1"}, "relationship"),
                                                                          ({"name": "name1.2"}, "relationship2")]}],
                         "meta_category": "meta_category2", "timestamp": 2}
                        ],
            "threat_level_id": 1,
        }

        event_sharing_group = {
            "name": "event_sharing_group_name",
        }

        old_publish = 1

        thread_level = "high"

        template: Template = env.get_template('alert_email.j2')

        template_str: str = template.render(mmisp_url=self.__mmisp_url, event=event,
                                            event_sharing_group=event_sharing_group, event_thread_level=thread_level,
                                            old_publish_timestamp=old_publish)

        expected_output = """
Hallo,
you receive this e-mail because this e-mail address is set to receive alerts on the MISP instance at https://misp.local

Event details
==============================================

URL: https://misp.local/events/view/1
Event ID: 1
Date: 2021-08-01
Reported by: orgc_name
Local owner of the event: org_name
Distribution: 4
Sharing Group: event_sharing_group_name
Tags: name, name2
Threat Level: high
Analysis: analysis
Description: info

==============================================

Related to:

https://misp.local/events/view/1 (test_date)

https://misp.local/events/view/2 (test_date2)

==============================================

Attributes (* indicates a new or modified attribute since last update):

*   category/type              : value(IDS) *
  - Tags: name1, name1.2
*   category2/type2             : value2 *
  - Tags: name2, name2.2, name2.3, name2.4
*   category3/type3             : value3 *
  - Tags: name3, name3.2
*   category4/type4             : value4(IDS) *
  - Tags: name4, name4.2

Objects (* indicates a new or modified attribute since last update):

* object_name/meta_category
*   category/type              : value(IDS) *
  - Tags: name1, name1.2
*   category2/type2             : value2 *
  - Tags: name2, name2.2
*   category3/type3             : value3(IDS) *
  - Tags: name3, name3.2, name2.3, name2.4
*   category4/type4             : value4 *
  - Tags: name4, name4.2

* object_name2/meta_category2
*   category/type              : value(IDS) *
  - Tags: name1, name1.2

=============================================="""

        self.assertEqual(expected_output, template_str)

    def test_alert_email_template_distribution_not_4(self):
        env: Environment = Environment(loader=PackageLoader('mmisp',
                                                            'worker/jobs/email/templates'),
                                       autoescape=select_autoescape())

        event = {
            "id": 1,
            "date": "2021-08-01",
            "distribution": 1,
            "orgc": {"name": "orgc_name"},
            "org": {"name": "org_name"},
            "tags": [({"name": "name"}, "relationship"), ({"name": "name2"}, "relationship2")],
            "analysis": "analysis",
            "info": "info",
            "related_events": [{"id": 1, "date": "test_date"}, {"id": 2, "date": "test_date2"}],
            "attributes": [],
            "objects": [],
            "threat_level_id": 1,
        }

        event_sharing_group = {
            "name": "event_sharing_group_name2",
        }

        old_publish = 20

        thread_level = "low"

        template: Template = env.get_template('alert_email.j2')

        template_str: str = template.render(mmisp_url=self.__mmisp_url, event=event,
                                            event_sharing_group=event_sharing_group,
                                            event_thread_level=thread_level,
                                            old_publish_timestamp=old_publish)

        expected_output = """
Hallo,
you receive this e-mail because this e-mail address is set to receive alerts on the MISP instance at https://misp.local

Event details
==============================================

URL: https://misp.local/events/view/1
Event ID: 1
Date: 2021-08-01
Reported by: orgc_name
Local owner of the event: org_name
Distribution: 1
Tags: name, name2
Threat Level: low
Analysis: analysis
Description: info

==============================================

Related to:

https://misp.local/events/view/1 (test_date)

https://misp.local/events/view/2 (test_date2)

==============================================
"""

        self.assertEqual(expected_output, template_str)

    def test_alert_email_template_no_tags_attributes_objects_related_events(self):
        env: Environment = Environment(loader=PackageLoader('mmisp',
                                                            'worker/jobs/email/templates'),
                                       autoescape=select_autoescape())

        event = {
            "id": 1,
            "date": "2021-08-01",
            "distribution": 4,
            "orgc": {"name": "orgc_name"},
            "org": {"name": "org_name"},
            "tags": [],
            "analysis": "analysis",
            "info": "info",
            "related_events": [],
            "attributes": [],
            "objects": [],
            "threat_level_id": 1,
        }

        event_sharing_group = {
            "name": "event_sharing_group_name3",
        }

        old_publish = 0

        thread_level = "low"

        template: Template = env.get_template('alert_email.j2')

        template_str: str = template.render(mmisp_url=self.__mmisp_url, event=event,
                                            event_sharing_group=event_sharing_group,
                                            event_thread_level=thread_level,
                                            old_publish_timestamp=old_publish)

        expected_output = """
Hallo,
you receive this e-mail because this e-mail address is set to receive alerts on the MISP instance at https://misp.local

Event details
==============================================

URL: https://misp.local/events/view/1
Event ID: 1
Date: 2021-08-01
Reported by: orgc_name
Local owner of the event: org_name
Distribution: 4
Sharing Group: event_sharing_group_name3
Tags:
Threat Level: low
Analysis: analysis
Description: info
"""

        self.assertEqual(expected_output, template_str)

    def test_alert_email_template_old_publish(self):
        env: Environment = Environment(loader=PackageLoader('mmisp',
                                                            'worker/jobs/email/templates'),
                                       autoescape=select_autoescape())

        event = {
            "id": 1,
            "date": "2021-08-01",
            "distribution": 4,
            "orgc": {"name": "orgc_name"},
            "org": {"name": "org_name"},
            "tags": [({"name": "name"}, "relationship"), ({"name": "name2"}, "relationship2")],
            "analysis": "analysis",
            "info": "info",
            "related_events": [{"id": 1, "date": "test_date"}, {"id": 2, "date": "test_date2"}],
            "attributes": [{"to_ids": True, "value": "value", "type": "type", "timestamp": 5,
                            "category": "category", "tags": [({"name": "name1"}, "relationship"),
                                                             ({"name": "name1.2"}, "relationship2")]},
                           {"to_ids": False, "value": "value2", "type": "type2", "timestamp": 15,
                            "category": "category2", "tags": [({"name": "name2"}, "relationship2"),
                                                              ({"name": "name2.2"}, "relationship2.2"),
                                                              ({"name": "name2.3"}, "relationship2.2"),
                                                              ({"name": "name2.4"}, "relationship2.2")]}],
            "objects": [{"name": "object_name", "attributes": [{"to_ids": True, "value": "value", "type": "type",
                                                                "timestamp": 5, "category": "category",
                                                                "tags": [({"name": "name1"}, "relationship"),
                                                                         ({"name": "name1.2"}, "relationship2")]},
                                                               {"to_ids": False, "value": "value2", "type": "type2",
                                                                "timestamp": 15, "category": "category2",
                                                                "tags": [({"name": "name2"}, "relationship"),
                                                                         ({"name": "name2.2"}, "relationship2")]}
                                                               ]}
                        ],
            "threat_level_id": 1,
        }

        event_sharing_group = {
            "name": "event_sharing_group_name",
        }

        old_publish = 10

        thread_level = "high"

        template: Template = env.get_template('alert_email.j2')

        template_str: str = template.render(mmisp_url=self.__mmisp_url, event=event,
                                            event_sharing_group=event_sharing_group,
                                            event_thread_level=thread_level,
                                            old_publish_timestamp=old_publish)

        expected_output = """
Hallo,
you receive this e-mail because this e-mail address is set to receive alerts on the MISP instance at https://misp.local

Event details
==============================================

URL: https://misp.local/events/view/1
Event ID: 1
Date: 2021-08-01
Reported by: orgc_name
Local owner of the event: org_name
Distribution: 4
Sharing Group: event_sharing_group_name
Tags: name, name2
Threat Level: high
Analysis: analysis
Description: info

==============================================

Related to:

https://misp.local/events/view/1 (test_date)

https://misp.local/events/view/2 (test_date2)

==============================================

Attributes (* indicates a new or modified attribute since last update):

  category/type              : value(IDS)
  - Tags: name1, name1.2
*   category2/type2             : value2 *
  - Tags: name2, name2.2, name2.3, name2.4

Objects (* indicates a new or modified attribute since last update):

  object_name/
  category/type              : value(IDS)
  - Tags: name1, name1.2
*   category2/type2             : value2 *
  - Tags: name2, name2.2

=============================================="""

        self.assertEqual(expected_output, template_str)

    def test_posts_email_template(self):
        env: Environment = Environment(loader=PackageLoader('mmisp',
                                                            'worker/jobs/email/templates'),
                                       autoescape=select_autoescape())

        template: Template = env.get_template('posts_email.j2')

        template_str: str = template.render(title="test_title", mmisp_url=self.__mmisp_url, thread_id=1,
                                            post_id=2, message="test_message")

        expected_output = """Hello,

Someone just posted to a MISP discussion you participated in with title:
test_title

The full discussion can be found at:
https://misp.local/threads/view/1post_id:2

The following message was added:

test_message"""

        self.assertEqual(expected_output, template_str)

    def test_contact_email_template(self):
        env: Environment = Environment(loader=PackageLoader('mmisp',
                                                            'worker/jobs/email/templates'),
                                       autoescape=select_autoescape())

        template: Template = env.get_template('contact_email.j2')

        template_str: str = template.render(mmisp_url=self.__mmisp_url, event_id=1, message="test_message",
                                            requestor_email="testEmail@bonobo.com")

        expected_output = """Hello,

Someone wants to get in touch with you concerning a MISP event.
You can reach them at testEmail@bonobo.com

They wrote the following message:

test_message

The event is the following:
https://misp.local/events/view/1"""

        self.assertEqual(expected_output, template_str)

    def test(self):
        api = MispAPIMock()
        event = api.get_event(1)
        print("was für wert " + str(event.sharing_group_id))
        if event.sharing_group_id is not None:
            print(event.sharing_group_id)
        else:
            print("else")
