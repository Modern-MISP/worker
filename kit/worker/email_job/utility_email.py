from kit.misp_dataclasses.misp_event import MispEvent

class utility_email():

    #returns depending on the EventTags which subject the email has
    def getEmailSubjektMarkForEvent(event: MispEvent) -> str:
        return "subjekt"


    def getAnnounceBaseurl() -> str: #TODO exeption

        """$baseurl = '';
            if (!empty(Configure::read('MISP.external_baseurl'))) {
                $baseurl = Configure::read('MISP.external_baseurl');
            } else if (!empty(Configure::read('MISP.baseurl'))) {
             $baseurl = Configure::read('MISP.baseurl');
            }
            return $baseurl;
     """

        return "url"
