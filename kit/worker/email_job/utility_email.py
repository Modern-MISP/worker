from kit.misp_dataclasses.misp_event import MispEvent


class UtilityEmail:

    # returns depending on the EventTags which subject the email has
    @staticmethod
    def get_email_subjekt_mark_for_event(event: MispEvent) -> str:
        return "subjekt"

    @staticmethod
    def get_announce_baseurl() -> str:  # TODO exeption

        """$baseurl = '';
            if (!empty(Configure::read('MISP.external_baseurl'))) {
                $baseurl = Configure::read('MISP.external_baseurl');
            } else if (!empty(Configure::read('MISP.baseurl'))) {
             $baseurl = Configure::read('MISP.baseurl');
            }
            return $baseurl;
     """

        return "url"
