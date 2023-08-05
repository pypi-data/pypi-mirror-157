class AssetManagementData:

    # CONSTRUCTOR
    def __init__(self, assetManagementData):
        self.__lifecycleToken = assetManagementData['LifecycleToken']
        self.__idSolution = assetManagementData['SolutionID']
        self.__idAsset = assetManagementData['AssetID']
        self.__assetName = assetManagementData['AssetName']
        self.__assetNamespace = assetManagementData['AssetNamespace']
        self.__assetType = assetManagementData['AssetType']
        self.__assetLevel = assetManagementData['AssetLevel']
        self.__assetCompiledStatus = assetManagementData['IsCompiled']
        self.__assetTranspiledStatus = assetManagementData['IsTranspiled']


    # GETTERS
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