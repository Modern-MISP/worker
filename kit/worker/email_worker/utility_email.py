from kit.misp_dataclasses.mips_event import Event


#TODO add Event as parameter
#returns depending on the EventTags which subject the email has
def getEmailSubjektMarkForEvent(event: Event) -> str:
    return "subjekt"

#TODO fragen was genau ich da machen soll, muss wahrschinlich in andere UtilityKlasse
def getAnnounceBaseurl() -> str:

    """$baseurl = '';
        if (!empty(Configure::read('MISP.external_baseurl'))) {
            $baseurl = Configure::read('MISP.external_baseurl');
        } else if (!empty(Configure::read('MISP.baseurl'))) {
            $baseurl = Configure::read('MISP.baseurl');
        }
        return $baseurl;
    """

    return "url"

def sendEmail(subject: str, body: str, recivers: list[str]):

    #gegebenenfalls user validieren ka warum, problem für später

    #passawort und misp email wahrschienlich in config, muss fragen
    pass
