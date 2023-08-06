import exchangelib
from exchangelib import Credentials, Account


class EASLogin:
    @classmethod
    def login(cls, email, pwd):
        try:
            credentials = Credentials(email, pwd)
            account = Account(email, credentials=credentials, autodiscover=True)
        except Exception as e:
            print("eas exception " + str(e) + " email " + email)
            return False, email, pwd, "eas", e
        else:
            result = (True, email, pwd, "eas")
            st = ' '.join(map(str, result))
            print("login succeed " + st)
            return result
