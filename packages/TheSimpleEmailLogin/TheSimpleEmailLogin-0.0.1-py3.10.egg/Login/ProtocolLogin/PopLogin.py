import poplib


class PopLogin:
    @classmethod
    def login(cls, email, pwd, protocol):
        host = protocol['hostname']
        port = protocol['port']
        try:
            if 'encryption' in protocol and protocol['encryption'] == 'ssl':
                M = poplib.POP3_SSL(host, port=port, timeout=30)
            else:
                M = poplib.POP3(host, port=port, timeout=30)
            M.user(email)
            M.pass_(pwd)
            results = M.list()
        except Exception as e:
            print("pop exception " + str(e) + " email " + email)
            return 'OK' in str(e), email, pwd, protocol, str(e)
        else:
            result = ('OK' in str(results[0]), email, pwd, protocol)
            st = ' '.join(map(str, result))
            print("login succeed " + st)
            return result
