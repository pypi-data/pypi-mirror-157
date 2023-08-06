from Login.Config.ConfigDetector import ConfigDetector
from Login.ProtocolLogin.EASLogin import EASLogin
from Login.ProtocolLogin.IMapLogin import IMapLogin
from Login.ProtocolLogin.PopLogin import PopLogin


class LoginHandler:
    @classmethod
    def findConfigAndLogin(cls, email, pwd):
        config = ConfigDetector.detect(email)
        if config is None:
            protocols = []
        else:
            protocols = config["protocols"]

        results = []
        for protocol in protocols:
            if protocol["protocol"] == 'imap':
                imapResult = IMapLogin.login(email, pwd, protocol)
                results.append(imapResult)
            elif protocol["protocol"] == 'pop3':
                popResult = PopLogin.login(email, pwd, protocol)
                results.append(popResult)

        easResult = EASLogin.login(email, pwd)
        results.append(easResult)

        return results
