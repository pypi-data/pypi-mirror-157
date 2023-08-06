import imaplib


class IMapLogin:
    @classmethod
    def login(cls, email, pwd, protocol):
        host = protocol['hostname']
        port = protocol['port']

        try:
            if 'encryption' in protocol and protocol['encryption'] == 'ssl':
                M = imaplib.IMAP4_SSL(host=host, port=port, timeout=30)
            else:
                M = imaplib.IMAP4(host=host, port=port, timeout=30)
            result = M.login(email, pwd)
        except Exception as e:
            print("imap exception " + str(e) + " email " + email)
            return 'OK' in str(e), email, pwd, protocol, e
        else:
            M.logout()
            result = ('OK' in result, email, pwd, protocol)
            st = ' '.join(map(str, result))
            print("login succeed " + st)
            return result


