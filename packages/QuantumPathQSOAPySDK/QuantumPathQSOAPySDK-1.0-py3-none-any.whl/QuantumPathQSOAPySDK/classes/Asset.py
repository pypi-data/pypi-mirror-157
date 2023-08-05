import base64

class Asset:

    # CONSTRUCTOR
    def __init__(self, asset):
        self.__id = asset['AssetID']
        self.__name = asset['AssetName']
        self.__namespace = asset['AssetNamespace']
        self.__description = asset['AssetDescription']
        self.__body = base64.b64decode(asset['AssetBody']).decode('ascii')
        self.__type = asset['AssetType']
        self.__level = asset['AssetLevel']
        self.__lastUpdate = asset['AssetLastUpdate']


    # GETTERS
    def getId(self):
        return self.__id
    
    def getName(self):
        return self.__name
    
    def getNamespace(self):
        return self.__namespace
    
    def getDescription(self):
        return self.__description
    
    def getBody(self):
        return self.__body
    
    def getType(self):
        return self.__type
    
    def getLevel(self):
        return self.__level
    
    def getLastUpdate(self):
        return self.__lastUpdate
    

    # SETTERS
    def setName(self, name):
        self.__name = name
    
    def setNamespace(self, namespace):
        self.__namespace = namespace
    
    def setDescription(self, description):
        self.__description = description
    
    def setBody(self, body):
        self.__body = body
    
    def setType(self, type):
        self.__type = type
    
    def setLevel(self, level):
        self.__level = level