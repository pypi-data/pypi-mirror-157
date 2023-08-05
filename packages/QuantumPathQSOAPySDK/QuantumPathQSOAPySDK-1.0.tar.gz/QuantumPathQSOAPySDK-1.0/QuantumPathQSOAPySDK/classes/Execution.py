import json

class Execution:

    # CONSTRUCTOR
    def __init__(self, execution):
        self.__exitCode = execution['ExitCode']
        self.__exitMessage = execution['ExitMessage']

        self.__solutionName = execution['ExecutionData']['Solution'] if execution['ExecutionData'] else None
        self.__flowName = execution['ExecutionData']['Flow'] if execution['ExecutionData'] else None
        self.__deviceName = execution['ExecutionData']['Device'] if execution['ExecutionData'] else None
        self.__histogram = json.loads(execution['ExecutionData']['Histogram']) if execution['ExecutionData'] else None
        self.__duration = execution['ExecutionData']['Duration'] if execution['ExecutionData'] else None


    # GETTERS
    def getExitCode(self):
        return self.__exitCode
    
    def getExitMessage(self):
        return self.__exitMessage
    
    def getSolutionName(self):
        return self.__solutionName
    
    def getFlowName(self):
        return self.__flowName
    
    def getDeviceName(self):
        return self.__deviceName
    
    def getHistogram(self):
        return self.__histogram
    
    def getDuration(self):
        return self.__duration