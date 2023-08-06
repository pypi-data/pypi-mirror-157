class LoginInfoLoader:
    @classmethod
    def loadLoginInfoArray(cls, path):
        f = open(path, "r")
        userLines = f.readlines()
        print(''.join(userLines))
        loginInfoArray = []
        for line in userLines:
            info = line.split(' ')
            email = info[0].replace('\n', '')
            pwd = info[-1].replace('\n', '')
            loginInfo = [email, pwd]
            loginInfoArray.append(loginInfo)
        f.close()
        return loginInfoArray
