class AssetManagementResult:

    # CONSTRUCTOR
    def __init__(self, assetManagementResult):
        self.__exitCode = assetManagementResult['ExitCode']
        self.__exitMessage = assetManagementResult['ExitMessage']

        self.__lifecycleToken = assetManagementResult['AssetData']['LifecycleToken']
        self.__idSolution = assetManagementResult['AssetData']['SolutionID']
        self.__idAsset = assetManagementResult['AssetData']['AssetID']
        self.__assetName = assetManagementResult['AssetData']['AssetName']
        self.__assetNamespace = assetManagementResult['AssetData']['AssetNamespace']
        self.__assetType = assetManagementResult['AssetData']['AssetType']
        self.__assetLevel = assetManagementResult['AssetData']['AssetLevel']
        self.__assetCompiledStatus = assetManagementResult['AssetData']['IsCompiled']
        self.__assetTranspiledStatus = assetManagementResult['AssetData']['IsTranspiled']


    # GETTERS
    def getExitCode(self):
        return self.__exitCode

    def getExitMessage(self):
        return self.__exitMessage

    def getLifecycleToken(self):
        return self.__lifecycleToken
    
    def getIdSolution(self):
        return self.__idSolution
    
    def getIdAsset(self):
        return self.__idAsset
    
    def getAssetName(self):
        return self.__assetName
    
    def getAssetNamespace(self):
        return self.__assetNamespace
    
    def getAssetType(self):
        return self.__assetType
    
    def getAssetLevel(self):
        return self.__assetLevel
    
    def getAssetCompiledStatus(self):
        return self.__assetCompiledStatus
    
    def getAssetTranspiledStatus(self):
        return self.__assetTranspiledStatus