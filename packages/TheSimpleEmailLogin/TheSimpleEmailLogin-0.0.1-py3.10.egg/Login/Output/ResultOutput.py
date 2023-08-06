class ResultOutput:
    succeedResultFile = None
    failedResultFile = None

    @classmethod
    def openSucceedFile(cls, originName):
        cls.succeedResultFile = open(originName, 'w+')

    @classmethod
    def openFailedFile(cls, originName):
        cls.failedResultFile = open(originName, 'w+')

    @classmethod
    def closeSucceedFile(cls):
        cls.succeedResultFile.close()

    @classmethod
    def closeFailedFile(cls):
        cls.failedResultFile.close()

    @classmethod
    def outputSucceedResult(cls, result):
        cls.failedResultFile.write(result)

    @classmethod
    def outputFailedResult(cls, result):
        cls.failedResultFile.write(result)

