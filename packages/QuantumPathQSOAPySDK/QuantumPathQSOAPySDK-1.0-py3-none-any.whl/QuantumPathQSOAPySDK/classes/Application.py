class Application:

    # CONSTRUCTOR
    def __init__(self, applicationName, idSolution, idFlow, idDevice, executionToken):
        self.__applicationName = applicationName
        self.__idSolution = idSolution
        self.__idFlow = idFlow
        self.__idDevice = idDevice
        self.__executionToken = executionToken


    # GETTERS
    def getApplicationName(self):
        return self.__applicationName

    def getIdSolution(self):
        return self.__idSolution

    def getIdFlow(self):
        return self.__idFlow

    def getIdDevice(self):
        return self.__idDevice

    def getExecutionToken(self):
        return self.__executionToken