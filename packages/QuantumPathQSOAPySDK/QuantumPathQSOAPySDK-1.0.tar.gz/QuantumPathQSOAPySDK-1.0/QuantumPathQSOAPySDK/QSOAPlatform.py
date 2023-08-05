from .classes import apiConnection

class QSOAPlatform:
    from .classes import Application
    from .classes import Asset
    from .classes import AssetManagementData
    from .classes import AssetManagementResult
    from .classes import CircuitGates
    from .classes import Context
    from .classes import NewFlow
    from .classes import Device
    from .classes import Execution
    from .classes import Flow
    from .classes import Solution

    from pathlib import Path
    from configparser import ConfigParser
    import os

    from matplotlib import pyplot as plt
    from prettytable import PrettyTable
    import collections
    import base64

    # CONSTRUCTOR
    def __init__(self, username=None, password=None, configFile=False):
        """
        QSOAPlatform object constructor.

        Prerequisites
        ----------
        - User created in QPath.

        Parameters
        ----------
        username : str
            QPath account username to authenticate.
        password : str
            QPath account password to authenticate. (SHA-256)
        
        Prerequisites
        ----------
        - User created in QPath.
        - .qpath file created in home path.

        Parameters
        ----------
        authenticate : str
            True to authenticate using .qpath config file.

        Output
        ----------
        QSOAPlatform obj
        """

        # VARIABLES
        self.environments = {
            'default-environments': {
                'pro': 'https://qsoa.quantumpath.app:8443/api/',
                'lab': 'https://qsoa.quantumsoftt.com:10443/api/'
            },
            'custom-environments': {}
        }

        qpathFile = self.ConfigParser(allow_no_value=True)
        qpathFileExists = qpathFile.read(str(self.Path.home()) + '\.qpath')
        if qpathFileExists:
            self.activeEnvironment = eval(qpathFile.options('active-environment')[0])
        else:
            self.activeEnvironment = ('default-environments', 'pro')

        self.context = None

        # API ENDPOINTS
        self.securityEndpoints = {
            'echoping': 'login/echoping/',
            'echouser': 'login/echouser/',
            'echostatus': 'login/echostatus',
            'authenticate': 'login/authenticate/',
            'authenticateEx': 'login/authenticateEx/'
        }

        self.connectionPoints = {
            'getVersion': 'connectionPoint/getVersion/',
            'getQuantumSolutions': 'connectionPoint/getQuantumSolutions/',
            'getQuantumDevices': 'connectionPoint/getQuantumDevices/',
            'getQuantumFlows': 'connectionPoint/getQuantumFlows/',
            'runQuantumApplication': 'connectionPoint/runQuantumApplication/',
            'getQuantumExecutionResponse': 'connectionPoint/getQuantumExecutionResponse/'
        }

        self.dynamicExtensions = {
            'getAssetCatalog': 'connectionPoint/getAssetCatalog/',
            'getAsset': 'connectionPoint/getAsset/',
            'createAsset': 'connectionPoint/createAsset?aSolutionID=',
            'updateAsset': 'connectionPoint/updateAsset/',
            'getAssetManagementResult': 'connectionPoint/getAssetManagementResult/',
            'deleteAsset': 'connectionPoint/deleteAsset/'
        }

        if configFile:
            self.authenticateEx()
        
        elif username:
            self.authenticateEx(username, password)


    # INTERN FUNCTIONS
    def __updateEnviroments(self):
        customEnvironments = []

        qpathFile = self.ConfigParser(allow_no_value=True)
        qpathFileExists = qpathFile.read(str(self.Path.home()) + '\.qpath')

        if qpathFileExists:
            for key in qpathFile['custom-environments']:
                customEnvironments.append((key, qpathFile['custom-environments'][key]))
                
        self.environments = {
            'default-environments': {
                'pro': 'https://qsoa.quantumpath.app:8443/api/',
                'lab': 'https://qsoa.quantumsoftt.com:10443/api/'
            },
            'custom-environments': dict(customEnvironments)
        }


    # USER METHODS
    def getEnvironments(self): # getEnvironments. Returns a Dictionary
        """
        Show QuantumPath available environments.

        Prerequisites
        ----------
        None.

        Output
        ----------
        dict
        """

        qpathFile = self.ConfigParser(allow_no_value=True)
        qpathFileExists = qpathFile.read(str(self.Path.home()) + '\.qpath')

        if qpathFileExists:
            self.__updateEnviroments()

        return self.environments


    def getActiveEnvironment(self): # getActiveEnvironment. Returns a Tuple
        """
        Show active QuantumPath environment.

        Prerequisites
        ----------
        None.

        Output
        ----------
        tuple
        """

        return self.activeEnvironment


    def setActiveEnvironment(self, environmentName): # setActiveEnvironment. Returns a Tuple
        """
        Set active QuantumPath environment.

        Prerequisites
        ----------
        Existing QuantumPath environment.

        Parameters
        ----------
        environmentName : str
            QuantumPath environment name to set as active.

        Output
        ----------
        tuple
        """

        newActiveEnvironment = None

        self.__updateEnviroments()

        if environmentName in self.environments['default-environments']:
            newActiveEnvironment = ('default-environments', environmentName)
        
        elif environmentName in self.environments['custom-environments']:
            newActiveEnvironment = ('custom-environments', environmentName)

        if newActiveEnvironment:
            self.activeEnvironment = newActiveEnvironment

        return self.activeEnvironment


    def echoping(self): # echoping. Returns a Boolean
        """
        Test to validate if the security service is enabled.

        Prerequisites
        ----------
        None.

        Output
        ----------
        bool
        """

        url = self.environments[self.activeEnvironment[0]][self.activeEnvironment[1]] + self.securityEndpoints['echoping']
        
        ping = apiConnection(url, 'boolean')
        
        return ping


    def authenticate(self, *args): # authenticate. Returns a Boolean
        """
        Performs the user authentication process.
        
        Prerequisites
        ----------
        - User created in QPath.

        Parameters
        ----------
        username : str
            QPath account username to authenticate.
        password : str
            QPath account password to authenticate. (Base64)
        
        Prerequisites
        ----------
        - User created in QPath.
        - .qpath file created in home path.

        Parameters
        ----------
        None if .qpath file in home path contains the credentials.

        Output
        ----------
        bool
        """

        authenticated = False

        url = self.environments[self.activeEnvironment[0]][self.activeEnvironment[1]] + self.securityEndpoints['authenticate']

        if not args:
            try:
                qpathcredentials = self.ConfigParser(allow_no_value=True)
                qpathcredentials.read(str(self.Path.home()) + '\.qpath')

                username = qpathcredentials[self.activeEnvironment[1] + '-credentials']['username']
                password = qpathcredentials[self.activeEnvironment[1] + '-credentials']['password']
            
            except:
                username = None
                password = None
            
        elif len(args) == 2:
            username = str(args[0])

            try:
                base64_bytes = str(args[1]).encode('ascii')
                password = str(self.base64.b64decode(base64_bytes).decode('ascii'))
            
            except:
                password = None

        self.context = self.Context(username, password, url)

        if self.context.getAuthToken():
            authenticated = True

        return authenticated


    def authenticateEx(self, *args): # authenticateEx. Returns a Boolean
        """
        Performs the user authentication process.
        
        Prerequisites
        ----------
        - User created in QPath.

        Parameters
        ----------
        username : str
            QPath account username to authenticate.
        password : str
            QPath account password to authenticate. (SHA-256)
        
        Prerequisites
        ----------
        - User created in QPath.
        - .qpath file created in home path.

        Parameters
        ----------
        None if .qpath file in home path contains the credentials.

        Output
        ----------
        bool
        """

        authenticated = False

        url = self.environments[self.activeEnvironment[0]][self.activeEnvironment[1]] + self.securityEndpoints['authenticateEx']

        if not args:
            try:
                qpathcredentials = self.ConfigParser(allow_no_value=True)
                qpathcredentials.read(str(self.Path.home()) + '\.qpath')

                username = qpathcredentials[self.activeEnvironment[1] + '-credentials']['username']
                password = qpathcredentials[self.activeEnvironment[1] + '-credentials']['password']
            
            except:
                username = None
                password = None
            
        elif len(args) == 2:
            username = str(args[0])
            password = str(args[1])

        self.context = self.Context(username, password, url)

        if self.context.getAuthToken():
            authenticated = True

        return authenticated


    def echostatus(self): # echostatus. Returns a Boolean
        """
        Check if user session is active.

        Prerequisites
        ----------
        None.

        Output
        ----------
        bool
        """
        
        status = False

        if self.context:
            url = self.environments[self.activeEnvironment[0]][self.activeEnvironment[1]] + self.securityEndpoints['echostatus']

            status = apiConnection(url, self.context.getHeader(), 'boolean')

            if not status:
                self.context = None

        return status


    def echouser(self): # echouser. Returns a String
        """
        Check user login status.

        Prerequisites
        ----------
        - User already authenticated.

        Output
        ----------
        str
        """

        login = None

        if self.echostatus():
            url = self.environments[self.activeEnvironment[0]][self.activeEnvironment[1]] + self.securityEndpoints['echouser']
            
            
            login = apiConnection(url, self.context.getHeader(), 'string')

        return login


    def getVersion(self): # getVersion. Returns a String
        """
        Check the ConnectionPoint service version.

        Prerequisites
        ----------
        - User already authenticated.

        Output
        ----------
        str
        """

        version = None

        if self.echostatus():
            url = self.environments[self.activeEnvironment[0]][self.activeEnvironment[1]] + self.connectionPoints['getVersion']

            version = apiConnection(url, self.context.getHeader(), 'string')

        return version


    def getQuantumSolutionList(self): # getQuantumSolutionList. Returns a JSON
        """
        Show the list of solutions available to the user along with their IDs.

        Prerequisites
        ----------
        - User already authenticated.
        - Solution created.

        Output
        ----------
        dict
        """

        solutionsJSON = None

        if self.echostatus():
            url = self.environments[self.activeEnvironment[0]][self.activeEnvironment[1]] + self.connectionPoints['getQuantumSolutions']

            solutionsJSON = apiConnection(url, self.context.getHeader(), 'json')

        return solutionsJSON


    def getQuantumSolutions(self): # getQuantumSolutions. Returns a Solution Array
        """
        Get the solutions available from the user as an object.

        Prerequisites
        ----------
        - User already authenticated.

        Output
        ----------
        Solution obj list
        """

        solutions = []

        if self.echostatus():
            url = self.environments[self.activeEnvironment[0]][self.activeEnvironment[1]] + self.connectionPoints['getQuantumSolutions']

            solutionsJSON = apiConnection(url, self.context.getHeader(), 'json')

            if solutionsJSON:
                for idSolution in solutionsJSON:
                    solutions.append(self.Solution(int(idSolution), solutionsJSON[idSolution]))
        
        return solutions


    def getQuantumSolutionName(self, idSolution): # getQuantumSolutionName. Returns a String
        """
        Get the name of a solution.

        Prerequisites
        ----------
        - User already authenticated.
        
        Parameters
        ----------
        idSolution : int
            Solution ID to show their name.

        Output
        ----------
        str
        """

        solutionName = None

        if self.echostatus():
            url = self.environments[self.activeEnvironment[0]][self.activeEnvironment[1]] + self.connectionPoints['getQuantumSolutions']

            solutionsJSON = apiConnection(url, self.context.getHeader(), 'json')
            
            if solutionsJSON:
                if str(idSolution) in solutionsJSON.keys():
                    solutionName = solutionsJSON[str(idSolution)]

        return solutionName


    def getQuantumDeviceList(self, idSolution): # getQuantumDeviceList. Returns a JSON
        """
        Show the list of devices available in a solution along with their IDs.

        Prerequisites
        ----------
        - User already authenticated.
        - Solution created.
        
        Parameters
        ----------
        idSolution : int
            Solution ID to show their devices.

        Output
        ----------
        dict
        """

        devicesJSON = None

        if self.echostatus():
            url = self.environments[self.activeEnvironment[0]][self.activeEnvironment[1]] + self.connectionPoints['getQuantumDevices'] + str(idSolution)

            devicesJSON = apiConnection(url, self.context.getHeader(), 'json')

        return devicesJSON


    def getQuantumDevices(self, idSolution): # getQuantumDevices. Returns a Device Array
        """
        Get the available devices in a solution as an object.

        Prerequisites
        ----------
        - User already authenticated.
        - Solution created.
        
        Parameters
        ----------
        idSolution : int
            Solution ID to show their devices.
        
        Output
        ----------
        Device obj list
        """

        devices = []

        if self.echostatus():
            url = self.environments[self.activeEnvironment[0]][self.activeEnvironment[1]] + self.connectionPoints['getQuantumDevices'] + str(idSolution)

            devicesJSON = apiConnection(url, self.context.getHeader(), 'json')

            if devicesJSON:
                for idDevice in devicesJSON:
                    devices.append(self.Device(int(idDevice), devicesJSON[idDevice]))
        
        return devices


    def getQuantumDeviceName(self, idSolution, idDevice): # getQuantumDeviceName. Returns a String
        """
        Get the name of a device.

        Prerequisites
        ----------
        - User already authenticated.
        - Solution created.
        
        Parameters
        ----------
        idSolution : int
            Solution ID to wich the device belongs.
        idDevice : int
            Device ID to show their name.
        
        Output
        ----------
        str
        """

        deviceName = None

        if self.echostatus():
            url = self.environments[self.activeEnvironment[0]][self.activeEnvironment[1]] + self.connectionPoints['getQuantumDevices'] + str(idSolution)

            devicesJSON = apiConnection(url, self.context.getHeader(), 'json')
            
            if devicesJSON:
                if str(idDevice) in devicesJSON.keys():
                    deviceName = devicesJSON[str(idDevice)]

        return deviceName


    def getQuantumFlowList(self, idSolution): # getQuantumFlowList. Returns a JSON
        """
        Show the list of flows available in a solution along with their IDs.

        Prerequisites
        ----------
        - User already authenticated.
        - Solution created.
        
        Parameters
        ----------
        idSolution : int
            Solution ID to show their flows.
        
        Output
        ----------
        dict
        """

        flowsJSON = None

        if self.echostatus():
            url = self.environments[self.activeEnvironment[0]][self.activeEnvironment[1]] + self.connectionPoints['getQuantumFlows'] + str(idSolution)

            flowsJSON = apiConnection(url, self.context.getHeader(), 'json')
            if flowsJSON == {}: flowsJSON = None
        
        return flowsJSON


    def getQuantumFlows(self, idSolution): # getQuantumFlows. Returns a Flow Array
        """
        Get the flows available in a solution as an object.
        
        Prerequisites
        ----------
        - User already authenticated.
        - Solution created.

        Parameters
        ----------
        idSolution : int
            Solution ID to show their flows.

        Output
        ----------
        Flow obj list
        """

        flows = []

        if self.echostatus():
            url = self.environments[self.activeEnvironment[0]][self.activeEnvironment[1]] + self.connectionPoints['getQuantumFlows'] + str(idSolution)

            flowsJSON = apiConnection(url, self.context.getHeader(), 'json')

            if flowsJSON:
                for idFlow in flowsJSON:
                    flows.append(self.Flow(int(idFlow), flowsJSON[idFlow]))
        
        return flows


    def getQuantumFlowName(self, idSolution, idFlow): # getQuantumFlowName. Returns a String
        """
        Get the name of a flow.

        Prerequisites
        ----------
        - User already authenticated.
        - Solution created.
        
        Parameters
        ----------
        idSolution : int
            Solution ID to wich the flow belongs.
        idFlow : int
            Flow ID to show their name.

        Output
        ----------
        str
        """

        flowName = None

        if self.echostatus():
            url = self.environments[self.activeEnvironment[0]][self.activeEnvironment[1]] + self.connectionPoints['getQuantumFlows'] + str(idSolution)

            flowsJSON = apiConnection(url, self.context.getHeader(), 'json')
            
            if flowsJSON:
                if str(idFlow) in flowsJSON.keys():
                    flowName = flowsJSON[str(idFlow)]

        return flowName


    def runQuantumApplication(self, applicationName, idSolution, idFlow, idDevice): # runQuantumApplication. Returns an Application object
        """
        Run a created quantum solution.

        Prerequisites
        ----------
        - User already authenticated.
        - Solution created.
        
        Parameters
        ----------
        applicationName : str
            Nametag to identify the execution.
        idSolution : int
            Solution ID to run.
        idFlow : int
            Specific Flow ID to run.
        idDevice : int
            Specific Device ID to run the solution.
        
        Output
        ----------
        Application obj
        """

        application = None

        if self.echostatus():
            url = self.environments[self.activeEnvironment[0]][self.activeEnvironment[1]] + self.connectionPoints['runQuantumApplication'] + str(applicationName) + '/' + str(idSolution) + '/' + str(idFlow) + '/' + str(idDevice)

            executionToken = apiConnection(url, self.context.getHeader(), 'string')

            if executionToken:
                application = self.Application(applicationName, int(idSolution), int(idFlow), int(idDevice), executionToken)

        return application


    def getQuantumExecutionResponse(self, *args): # getQuantumExecutionResponse. Returns an Execution object
        """
        Get the response of a quantum solution execution.

        Prerequisites
        ----------
        - User already authenticated.
        - Solution run.
        - Application object generated.
        
        Parameters
        ----------
        application : Application obj
            Application object generated in running a quantum solution.
        
        Prerequisites
        ----------
        - User already authenticated.
        - Solution run.

        Parameters
        ----------
        applicationName : str
            Executino nametag.
        idSolution : int
            Solution ID of the solution already run.
        idFlow : int
            Specific Flow ID of the solution already run.
        idDevice : int
            Specific Device ID of the solution already run.
        
        Output
        ----------
        Execution obj
        """

        execution = None

        if self.echostatus():

            executionToken = str(args[0].getExecutionToken()) if len(args) == 1 else str(args[0])
            idSolution = str(args[0].getIdSolution()) if len(args) == 1 else str(args[1])
            idFlow = str(args[0].getIdFlow()) if len(args) == 1 else str(args[2])

            url = self.environments[self.activeEnvironment[0]][self.activeEnvironment[1]] + self.connectionPoints['getQuantumExecutionResponse'] + executionToken + '/' + idSolution + '/' + idFlow

            executionJSON = apiConnection(url, self.context.getHeader(), 'json')
            
            if executionJSON:
                execution = self.Execution(executionJSON)
        
        return execution


    def representResults(self, execution): # representResults. Returns a plot
        """
        Results visual representation.

        Prerequisites
        ----------
        - User already authenticated.
        - Execution completed.
        
        Parameters
        ----------
        execution : Execution obj
            Execution object generated by execution response method.
        
        Output
        ----------
        png / string
        """

        representation = None

        if self.echostatus():

            if isinstance(execution, self.Execution):

                if execution.getExitCode() == 'OK':

                    histogramData = execution.getHistogram()
                    histogramTitle = list(histogramData.keys())[0]
                    histogramValues = list(histogramData.values())[0]

                    if 'number_of_samples' in histogramValues.keys(): # annealing
                        tableResults = self.PrettyTable(['Name', 'Value'])

                        for key, value in histogramValues['fullsample'].items():
                            tableResults.add_row([key, value])

                        del histogramValues['fullsample']

                        tableInfo = self.PrettyTable()
                        tableInfo.field_names = histogramValues.keys()
                        tableInfo.add_rows([histogramValues.values()])

                        representation = str(histogramTitle) + '\n' + str(tableInfo) + '\n' + str(tableResults)

                    else: # quantum gates
                        histogramValues = self.collections.OrderedDict(sorted(list(histogramData.values())[0].items()))

                        fig, ax = self.plt.subplots(1, 1)
                        ax.bar([ str(i) for i in histogramValues.keys()], histogramValues.values(), color='g')

                        ax.set_title(histogramTitle)

                        rects = ax.patches
                        labels = [list(histogramValues.values())[i] for i in range(len(rects))]

                        for rect, label in zip(rects, labels):
                            height = rect.get_height()
                            ax.text(rect.get_x() + rect.get_width() / 2, height+0.01, label,
                                ha='center', va='bottom')

                        representation = 'Results Ploted'
                        self.plt.show()
        
        return representation


    def getAssetCatalog(self, idSolution, assetType, assetLevel): # getAssetCatalog. Returns an Asset List
        """
        Get asset information from a solution.

        Prerequisites
        ----------
        - User already authenticated.
        - Solution created.
        
        Parameters
        ----------
        idSolution : int
            Solution ID to show their information.
        assetType : string
            Type of the asset required. It can be CIRCUIT or FLOW.
        assetLevel : string
            Level of the lenguage specificated. It can be VL (Visual Language) or IL (Intermediate Lenguage).
        
        Output
        ----------
        Asset obj list
        """

        assetTypeOptions = ['CIRCUIT', 'FLOW'] # assetType input possible options
        assetLevelOptions = ['VL', 'IL'] # assetLevel input possible options
        assetCatalog = []

        assetType = str(assetType).upper()
        assetLevel = str(assetLevel).upper()
        
        if assetType in assetTypeOptions and assetLevel in assetLevelOptions: # arguments are correct

            if self.echostatus():
                url = self.environments[self.activeEnvironment[0]][self.activeEnvironment[1]] + self.dynamicExtensions['getAssetCatalog'] + str(idSolution) + '/' + assetType + '/' + assetLevel

                assetCatalogList = apiConnection(url, self.context.getHeader(), 'json')

                if assetCatalogList:
                    for asset in assetCatalogList:
                        assetCatalog.append(self.Asset(asset))

        return assetCatalog


    def getAsset(self, idAsset, assetType, assetLevel): # getAsset. Returns an Asset object
        """
        Get specific asset information.

        Prerequisites
        ----------
        - User already authenticated.
        - Asset created.
        
        Parameters
        ----------
        idAsset : int
            Asset ID to show their information.
        assetType : string
            Type of the asset required. It can be CIRCUIT or FLOW.
        assetLevel : string
            Level of the lenguage specificated. It can be VL (Visual Language) or IL (Intermediate Lenguage).
        
        Output
        ----------
        Asset obj
        """

        assetTypeOptions = ['CIRCUIT', 'FLOW'] # assetType input possible options
        assetLevelOptions = ['VL', 'IL'] # assetLevel input possible options
        asset = None

        assetType = str(assetType).upper()
        assetLevel = str(assetLevel).upper()
        
        if assetType in assetTypeOptions and assetLevel in assetLevelOptions: # arguments are correct

            if self.echostatus():
                url = self.environments[self.activeEnvironment[0]][self.activeEnvironment[1]] + self.dynamicExtensions['getAsset'] + str(idAsset) + '/' + assetType + '/' + assetLevel

                assetResponse = apiConnection(url, self.context.getHeader(), 'json')

                if assetResponse:
                    asset = self.Asset(assetResponse)

        return asset


    def createAsset(self, idSolution, assetName, assetNamespace, assetDescription, assetBody, assetType, assetLevel): # createAsset. Returns an Asset Management Data object
        """
        Create asset.

        Prerequisites
        ----------
        - User already authenticated.
        - Solution created.
        
        Parameters
        ----------
        idSolution : int
            Solution to create the asset.
        assetName : string
            New asset name.
        assetNamespace : string
            New asset namespace.
        assetDescription : string
            New asset description.
        assetBody : string / CircuitGates obj / NewFlow obj
            New asset body as string or as a circtuit obj.
        assetType : string
            New asset type. It can be GATES, ANNEAL or FLOW.
        assetLevel : string
            New asset level. It can be VL (Visual Language) or IL (Intermediate Lenguage).
        
        Output
        ----------
        Asset Management Data obj
        """
        
        assetTypeOptions = ['GATES', 'ANNEAL', 'FLOW'] # assetType input possible options
        assetLevelOptions = ['VL', 'IL'] # assetLevel input possible options
        assetManagementData = None

        if assetType in assetTypeOptions and assetLevel in assetLevelOptions: # arguments are correct
        
            if self.echostatus():
                if isinstance(assetBody, self.CircuitGates) or isinstance(assetBody, self.NewFlow):
                    assetBody = assetBody.getParsedBody()

                newAsset = {
                    "AssetID": -1,
                    "AssetName": assetName,
                    "AssetNamespace": assetNamespace,
                    "AssetDescription": assetDescription,
                    "AssetBody": self.base64.b64encode(assetBody.encode('ascii')).decode('ascii'),
                    "AssetType": assetType,
                    "AssetLevel": assetLevel,
                    "AssetLastUpdate": ''
                }

                url = self.environments[self.activeEnvironment[0]][self.activeEnvironment[1]] + self.dynamicExtensions['createAsset'] + str(idSolution)

                assetManagementDataResult = apiConnection(url, self.context.getHeader(), str(newAsset), 'json', 'data')

                if assetManagementDataResult:
                    assetManagementData = self.AssetManagementData(assetManagementDataResult)

        return assetManagementData


    def updateAsset(self, asset, assetName = None, assetNamespace = None, assetDescription = None,
                    assetBody = None, assetType = None, assetLevel = None): # updateAsset. Returns an Asset Management Data object
        """
        Update asset values.

        Prerequisites
        ----------
        - User already authenticated.
        - Asset created.
        
        Parameters
        ----------
        asset : Asset obj
            Asset object to change information.
        assetName : string
            New asset name. Optional argument.
        assetNamespace : string
            New asset namespace. Optional argument.
        assetDescription : string
            New asset description. Optional argument.
        assetBody : string / CircuitGates obj / NewFlow obj
            New asset body as string or as a circtuit obj. Optional argument.
        assetType : string
            New asset type. It can be GATES, ANNEAL or FLOW. Optional argument.
        assetLevel : string
            New asset level. It can be VL (Visual Language) or IL (Intermediate Lenguage). Optional argument.
        
        Output
        ----------
        Asset Management Data obj
        """
        
        assetTypeOptions = ['GATES', 'ANNEAL', 'FLOW'] # assetType input possible options
        assetLevelOptions = ['VL', 'IL'] # assetLevel input possible options
        goodArguments = True
        assetManagementData = None

        if assetType and assetType not in assetTypeOptions: # argument are incorrect
            goodArguments = False
        
        if assetLevel and assetLevel not in assetLevelOptions: # argument are incorrect
            goodArguments = False
        
        if goodArguments and asset and self.echostatus():
            if assetName: asset.setName(str(assetName))
            if assetNamespace: asset.setNamespace(str(assetName))
            if assetDescription: asset.setDescription(str(assetDescription))
            if assetBody:
                if isinstance(assetBody, self.CircuitGates) or isinstance(assetBody, self.NewFlow):
                    assetBody = assetBody.getParsedBody()
                else:
                    assetBody = str(assetBody)
                asset.setBody(assetBody)
            if assetType: asset.setType(str(assetType))
            if assetLevel: asset.setLevel(str(assetLevel))

            newAsset = {
                "AssetID": asset.getId(),
                "AssetName": asset.getName(),
                "AssetNamespace": asset.getNamespace(),
                "AssetDescription": asset.getDescription(),
                "AssetBody": self.base64.b64encode(asset.getBody().encode('ascii')).decode('ascii'),
                "AssetType": asset.getType(),
                "AssetLevel": asset.getLevel(),
                "AssetLastUpdate": asset.getLastUpdate()
            }

            url = self.environments[self.activeEnvironment[0]][self.activeEnvironment[1]] + self.dynamicExtensions['updateAsset']

            assetManagementDataResult = apiConnection(url, self.context.getHeader(), str(newAsset), 'json', 'data')

            if assetManagementDataResult:
                assetManagementData = self.AssetManagementData(assetManagementDataResult)
        
        return assetManagementData


    def deleteAsset(self, *args): # deleteAsset. Returns a Boolean
        """
        Delete asset.

        Prerequisites
        ----------
        - User already authenticated.
        - Asset created.
        
        Parameters
        ----------
        asset : Asset obj
            Asset object to delete.
        
        Parameters
        ----------
        idAsset : int
            Asset id to delete.
        assetType : string
            Asset type to delete. It can be CIRCUIT or FLOW.
        
        Output
        ----------
        bool
        """

        assetDeleted = False

        if self.echostatus():
            idAsset = str(args[0].getId()) if len(args) == 1 else str(args[0])

            if len(args) == 1:
                assetType = args[0].getType() if args[0].getType() == 'FLOW' else 'CIRCUIT'

            else:
                assetType = str(args[1])
            
            url = self.environments[self.activeEnvironment[0]][self.activeEnvironment[1]] + self.dynamicExtensions['deleteAsset'] + idAsset + '/' + assetType

            assetDeleted = apiConnection(url, self.context.getHeader(), 'boolean')

        return assetDeleted


    def getAssetManagementResult(self, lifecycleToken): # getAssetManagementResult. Returns an Asset Management Data object
        """
        Get Asset Management Result from a lifecycle token.

        Prerequisites
        ----------
        - Existing asset lifecycle token.
        
        Parameters
        ----------
        lifecycleToken : string
            Asset lifecycle token.
        
        Output
        ----------
        Asset Management Result obj
        """

        if self.echostatus():
            url = self.environments[self.activeEnvironment[0]][self.activeEnvironment[1]] + self.dynamicExtensions['getAssetManagementResult'] + str(lifecycleToken)

            assetManagementResult = apiConnection(url, self.context.getHeader(), 'json')

            if assetManagementResult:
                assetManagementResult = self.AssetManagementResult(assetManagementResult)

        return assetManagementResult