
#TODO add Event as parameter
#returns depending on the EventTags which subject the email has
def getEmailSubjekt() -> str:
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

#TODO wie genau ich das mache, wtf, bzw was zum fick validiere ich da?
def sendEmail():
    pass
