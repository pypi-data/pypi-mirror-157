import unittest
import time

from QuantumPathQSOAPySDK import QSOAPlatform

idSolution_g = 10391 # gates pro
idFlow_g = 331 # gates pro
idDevice_g = 2 # gates pro

idSolution_a = 10396 # annealing pro
idFlow_a = 335 # annealing pro
idDevice_a = 19 # annealing pro

idAsset = 20380

##################_____GET ENVIRONMENTS_____##################

class Test_GetEnvironments(unittest.TestCase):

    # GET ENVIRONMENTS
    def test_getEnvironments(self):
        qsoa = QSOAPlatform()

        environments = qsoa.getEnvironments()

        self.assertEqual(environments['default-environments'], {
            'pro': 'https://qsoa.quantumpath.app:8443/api/',
            'lab': 'https://qsoa.quantumsoftt.com:10443/api/'
        }) # check default environments


##################_____GET ACTIVE ENVIRONMENT_____##################

class Test_GetActiveEnvironment(unittest.TestCase):

    # GET ACTIVE ENVIRONMENT
    def test_getActiveEnvironment(self):
        qsoa = QSOAPlatform()

        qsoa.setActiveEnvironment('pro')
        activeEnvironment = qsoa.getActiveEnvironment()

        self.assertEqual(activeEnvironment, ('default-environments', 'pro')) # check active environment


##################_____SET ACTIVE ENVIRONMENT_____##################

class Test_SetActiveEnvironment(unittest.TestCase):

    # SET ACTIVE ENVIRONMENT
    def test_setActiveEnvironment(self):
        qsoa = QSOAPlatform()

        setActiveEnvironment = qsoa.setActiveEnvironment('lab')

        self.assertEqual(setActiveEnvironment, ('default-environments', 'lab')) # check active environment
    
    # SET ACTIVE ENVIRONMENT BAD ENVIRONMENT
    def test_setActiveEnvironment_badEnvironment(self):
        qsoa = QSOAPlatform()

        qsoa.setActiveEnvironment('pro')

        setActiveEnvironment = qsoa.setActiveEnvironment('badEnvironment')

        self.assertEqual(setActiveEnvironment, ('default-environments', 'pro')) # check active environment


##################_____ECHOPING_____##################

class Test_Echoping(unittest.TestCase):

    # CHECK SECURITY
    def test_echoping(self):
        qsoa = QSOAPlatform()

        ping = qsoa.echoping() # check security

        self.assertIsInstance(ping, bool) # check is a boolean


##################_____QSOAPLATFORM_____##################

class Test_QSOAPlatform(unittest.TestCase):

    # NOT AUTHENTICATE
    def test_QSOAPlatform_notAuthenticate(self):
        qsoa = QSOAPlatform()

        authenticated = qsoa.echostatus() # check login

        self.assertFalse(authenticated) # check is authenticated

    # AUTHENTICATE USER MANUALLY
    '''
    INTRODUCE MANUALLY USERNAME AND PASSWORD
    '''
    # def test_QSOAPlatform_authenticate_manually(self):
    #     username = 'username'
    #     password = 'password' # password in SHA-256

    #     qsoa = QSOAPlatform(username, password)

    #     authenticated = qsoa.echostatus() # check login

    #     self.assertTrue(authenticated) # check is True

    # AUTHENTICATE USER CONFIG FILE
    def test_QSOAPlatform_authenticate_configFile(self):
        qsoa = QSOAPlatform(configFile=True)

        authenticated = qsoa.echostatus() # check login

        self.assertTrue(authenticated) # check is True


##################_____AUTHENTICATE_____##################

class Test_Authenticate(unittest.TestCase):

    # AUTHENTICATE USER MANUALLY
    '''
    INTRODUCE MANUALLY USERNAME AND PASSWORD
    '''
    # def test_authenticate_manually(self):
    #     qsoa = QSOAPlatform()

    #     username = 'username'
    #     password = 'password' # password encoded in Base64

    #     authenticated = qsoa.authenticate(username, password) # authentication

    #     self.assertTrue(authenticated) # check username is authenticated

    # AUTHENTICATE USER MANUALLY ERROR BAD CREDENTIALS
    def test_authenticate_manually_badCredentials(self):
        qsoa = QSOAPlatform()

        username = 'username'
        password = 'password'

        authenticated = qsoa.authenticate(username, password) # authentication

        self.assertFalse(authenticated) # check username is authenticated
    
    # AUTHENTICATE USER CONFIG FILE
    '''
    CREATE .QPATH CONFIG FILE
    '''
    # def test_authenticate_configFile(self):
    #     qsoa = QSOAPlatform()

    #     authenticated = qsoa.authenticate() # authentication

    #     self.assertTrue(authenticated) # check username is authenticated


##################_____AUTHENTICATE EX_____##################

class Test_AuthenticateEx(unittest.TestCase):

    # AUTHENTICATE EX USER MANUALLY
    '''
    INTRODUCE MANUALLY USERNAME AND PASSWORD
    '''
    # def test_authenticateEx_manually(self):
    #     qsoa = QSOAPlatform()

    #     username = 'username'
    #     password = 'password' # password in SHA-256

    #     authenticated = qsoa.authenticateEx(username, password) # authentication

    #     self.assertTrue(authenticated) # check username is authenticated

    # AUTHENTICATE EX USER MANUALLY ERROR BAD CREDENTIALS
    def test_authenticateEx_manually_badCredentials(self):
        qsoa = QSOAPlatform()

        username = 'username'
        password = 'password'

        authenticated = qsoa.authenticateEx(username, password) # authentication

        self.assertFalse(authenticated) # check username is authenticated
    
    # AUTHENTICATE EX USER CONFIG FILE
    '''
    CREATE .QPATH CONFIG FILE
    '''
    def test_authenticateEx_configFile(self):
        qsoa = QSOAPlatform()

        authenticated = qsoa.authenticateEx() # authentication

        self.assertTrue(authenticated) # check username is authenticated


##################_____ECHOSTATUS_____##################

class Test_Echostatus(unittest.TestCase):

    # CHECK USER SESSION STATUS
    def test_echostatus(self):
        qsoa = QSOAPlatform()

        qsoa.authenticateEx() # authentication

        status = qsoa.echostatus() # check user session status

        self.assertTrue(status) # check user session status


##################_____ECHOUSER_____##################

class Test_Echouser(unittest.TestCase):

    # CHECK LOGIN STATUS
    def test_echouser(self):
        qsoa = QSOAPlatform()

        qsoa.authenticateEx() # authentication

        login = qsoa.echouser() # check login status

        self.assertIsNotNone(login) # check login status


##################_____GET VERSION_____##################

class Test_GetVersion(unittest.TestCase):

    # GET VERSION
    def test_getVersion(self):
        qsoa = QSOAPlatform()

        qsoa.authenticateEx() # authentication

        version = qsoa.getVersion() # get version

        self.assertIsNotNone(version) # check version


##################_____GET QUANTUM SOLUTION LIST_____##################

class Test_GetQuantumSolutionList(unittest.TestCase):

    # GET QUANTUM SOLUTION LIST
    def test_getQuantumSolutionList(self):
        qsoa = QSOAPlatform()

        qsoa.authenticateEx() # authentication

        solutionList = qsoa.getQuantumSolutionList() # get quantum solution list

        self.assertIsInstance(solutionList, dict) # check solutions' dictionary


##################_____GET QUANTUM SOLUTIONS_____##################

class Test_GetQuantumSolutions(unittest.TestCase):

    # GET QUANTUM SOLUTIONS
    def test_getQuantumSolutions(self):
        qsoa = QSOAPlatform()

        qsoa.authenticateEx() # authentication

        solutions = qsoa.getQuantumSolutions() # get quantum solutions

        self.assertIsInstance(solutions, list) # check returns a list

        firstSolution = solutions[0]
        self.assertEqual(str(type(firstSolution)), "<class 'quantumpath_pythonsdk.classes.Solution.Solution'>") # check solution is an object Solution


##################_____GET QUANTUM SOLUTION NAME_____##################

class Test_GetQuantumSolutionName(unittest.TestCase):

    # GET QUANTUM SOLUTION NAME
    def test_getQuantumSolutionName(self):
        qsoa = QSOAPlatform()

        qsoa.authenticateEx() # authentication

        solutionName = qsoa.getQuantumSolutionName(idSolution_g) # get quantum solution name

        self.assertIsInstance(solutionName, str) # check solution name

    # GET QUANTUM SOLUTION NAME BAD ID SOLUTION
    def test_getQuantumSolutionName_badIdSolution(self):
        qsoa = QSOAPlatform()

        qsoa.authenticateEx() # authentication

        idSolution_g = 999
        solutionName = qsoa.getQuantumSolutionName(idSolution_g) # get quantum solution name

        self.assertIsNone(solutionName) # check solution name


##################_____GET QUANTUM DEVICE LIST_____##################

class Test_GetQuantumDeviceList(unittest.TestCase):

    # GET QUANTUM DEVICE LIST
    def test_getQuantumDeviceList(self):
        qsoa = QSOAPlatform()

        qsoa.authenticateEx() # authentication

        deviceList = qsoa.getQuantumDeviceList(idSolution_g) # get quantum device list

        self.assertIsInstance(deviceList, dict) # check devices' dictionary
    
    # GET QUANTUM DEVICE LIST BAD ID SOLUTION
    def test_getQuantumDeviceList_badIdSolution(self):
        qsoa = QSOAPlatform()

        qsoa.authenticateEx() # authentication

        idSolution_g = 999
        deviceList = qsoa.getQuantumDeviceList(idSolution_g) # get quantum device list

        self.assertIsNone(deviceList) # check devices' dictionary


##################_____GET QUANTUM DEVICES_____##################

class Test_GetQuantumDevices(unittest.TestCase):

    # GET QUANTUM DEVICES
    def test_getQuantumDevices(self):
        qsoa = QSOAPlatform()

        qsoa.authenticateEx() # authentication

        devices = qsoa.getQuantumDevices(idSolution_g) # get quantum devices

        self.assertIsInstance(devices, list) # check returns a list

        firstDevice = devices[0]
        self.assertEqual(str(type(firstDevice)), "<class 'quantumpath_pythonsdk.classes.Device.Device'>") # check device is an object Device

    # GET QUANTUM DEVICES BAD ID SOLUTION
    def test_getQuantumDevices_badIdSolution(self):
        qsoa = QSOAPlatform()

        qsoa.authenticateEx() # authentication

        idSolution_g = 999
        devices = qsoa.getQuantumDevices(idSolution_g) # get quantum devices

        self.assertEqual(devices, []) # check returns an empty list


##################_____GET QUANTUM DEVICE NAME_____##################

class Test_GetQuantumDeviceName(unittest.TestCase):

    # GET QUANTUM DEVICE NAME
    def test_getQuantumDeviceName(self):
        qsoa = QSOAPlatform()

        qsoa.authenticateEx() # authentication

        deviceName = qsoa.getQuantumDeviceName(idSolution_g, idDevice_g) # get quantum device name

        self.assertIsInstance(deviceName, str) # check device name
    
    # GET QUANTUM DEVICE NAME BAD ID SOLUTION
    def test_getQuantumDeviceName_badIdSolution(self):
        qsoa = QSOAPlatform()

        qsoa.authenticateEx() # authentication

        idSolution_g = 999
        deviceName = qsoa.getQuantumDeviceName(idSolution_g, idDevice_g) # get quantum device name

        self.assertIsNone(deviceName) # check device name
    
    # GET QUANTUM DEVICE NAME BAD ID DEVICE
    def test_getQuantumDeviceName_badIdDevice(self):
        qsoa = QSOAPlatform()

        qsoa.authenticateEx() # authentication

        idDevice_g = 999
        deviceName = qsoa.getQuantumDeviceName(idSolution_g, idDevice_g) # get quantum device name

        self.assertIsNone(deviceName) # check device name


##################_____GET QUANTUM FLOW LIST_____##################

class Test_GetQuantumFlowList(unittest.TestCase):

    # GET QUANTUM FLOW LIST
    def test_getQuantumFlowList(self):
        qsoa = QSOAPlatform()

        qsoa.authenticateEx() # authentication

        flowList = qsoa.getQuantumFlowList(idSolution_g) # get quantum flow list

        self.assertIsInstance(flowList, dict) # check flows' dictionary


    # GET QUANTUM FLOW LIST BAD ID SOLUTION
    def test_getQuantumFlowList_badIdSolution(self):
        qsoa = QSOAPlatform()

        qsoa.authenticateEx() # authentication

        idSolution_g = 999
        flowList = qsoa.getQuantumFlowList(idSolution_g) # get quantum flow list

        self.assertIsNone(flowList) # check flows' dictionary


##################_____GET QUANTUM FLOWS_____##################

class Test_GetQuantumFlows(unittest.TestCase):

    # GET QUANTUM FLOWS
    def test_getQuantumFlows(self):
        qsoa = QSOAPlatform()

        qsoa.authenticateEx() # authentication

        flows = qsoa.getQuantumFlows(idSolution_g) # get quantum flows

        self.assertIsInstance(flows, list) # check returns a list

        firstFlow = flows[0]
        self.assertEqual(str(type(firstFlow)), "<class 'quantumpath_pythonsdk.classes.Flow.Flow'>") # check flow is an object Flow
    
    # GET QUANTUM FLOWS BAD ID SOLUTION
    def test_getQuantumFlows_badIdSolution(self):
        qsoa = QSOAPlatform()

        qsoa.authenticateEx() # authentication

        idSolution_g = 999
        flows = qsoa.getQuantumFlows(idSolution_g) # get quantum flows

        self.assertEqual(flows, []) # check returns an empty list


##################_____GET QUANTUM FLOW NAME_____##################

class Test_GetQuantumFlowName(unittest.TestCase):

    # GET QUANTUM FLOW NAME
    def test_getQuantumFlowName(self):
        qsoa = QSOAPlatform()

        qsoa.authenticateEx() # authentication

        flowName = qsoa.getQuantumFlowName(idSolution_g, idFlow_g) # get quantum flow name

        self.assertIsInstance(flowName, str) # check flow name
    
    # GET QUANTUM FLOW NAME BAD ID SOLUTION
    def test_getQuantumFlowName_badIdSolution(self):
        qsoa = QSOAPlatform()

        qsoa.authenticateEx() # authentication

        idSolution_g = 999
        flowName = qsoa.getQuantumFlowName(idSolution_g, idFlow_g) # get quantum flow name

        self.assertIsNone(flowName) # check flow name
    
    # GET QUANTUM FLOW NAME BAD ID FLOW
    def test_getQuantumFlowName_badIdFlow(self):
        qsoa = QSOAPlatform()

        qsoa.authenticateEx() # authentication

        idFlow_g = 999
        flowName = qsoa.getQuantumFlowName(idSolution_g, idFlow_g) # get quantum flow name

        self.assertIsNone(flowName) # check flow name


##################_____RUN QUANTUM APPLICATION_____##################

class Test_RunQuantumApplication(unittest.TestCase):

    # RUN QUANTUM APPLICATION GATES
    def test_runQuantumApplication_gates(self):
        qsoa = QSOAPlatform()

        qsoa.authenticateEx() # authentication

        applicationName = 'Gates_Project'
        application = qsoa.runQuantumApplication(applicationName, idSolution_g, idFlow_g, idDevice_g) # run quantum application gates

        self.assertIsNotNone(application) # check quantum application gates

    # RUN QUANTUM APPLICATION ANNEALING
    def test_runQuantumApplication_annealing(self):
        qsoa = QSOAPlatform()

        qsoa.authenticateEx() # authentication

        applicationName = 'Annealing_Project'

        application = qsoa.runQuantumApplication(applicationName, idSolution_a, idFlow_a, idDevice_a) # run annealing application

        self.assertIsNotNone(application) # check quantum application annealing

    # RUN QUANTUM APPLICATION BAD ID SOLUTION
    def test_runQuantumApplication_gates_badIdSolution(self):
        qsoa = QSOAPlatform()

        qsoa.authenticateEx() # authentication

        applicationName = 'Gates_Project'
        idSolution_g = 999
        application = qsoa.runQuantumApplication(applicationName, idSolution_g, idFlow_g, idDevice_g) # run quantum application gates

        self.assertIsNone(application) # check quantum application gates

    # RUN QUANTUM APPLICATION BAD ID FLOW
    def test_runQuantumApplication_gates_badIdFlow(self):
        qsoa = QSOAPlatform()

        qsoa.authenticateEx() # authentication

        applicationName = 'Gates_Project'
        idFlow_g = 999
        application = qsoa.runQuantumApplication(applicationName, idSolution_g, idFlow_g, idDevice_g) # run quantum application gates

        self.assertIsNotNone(application) # check quantum application gates

    # RUN QUANTUM APPLICATION BAD ID DEVICE
    def test_runQuantumApplication_gates_badIdDevice(self):
        qsoa = QSOAPlatform()

        qsoa.authenticateEx() # authentication

        applicationName = 'Gates_Project'
        idDevice_g = 999
        application = qsoa.runQuantumApplication(applicationName, idSolution_g, idFlow_g, idDevice_g) # run quantum application gates

        self.assertIsNotNone(application) # check quantum application gates


##################_____RUN QUANTUM EXECUTION RESPONSE_____##################

class Test_RunQuantumExecutionResponse(unittest.TestCase):

    # GET QUANTUM EXECTUTION RESPONSE NO RESULT
    def test_getQuantumExecutionResponse_noResult(self):
        qsoa = QSOAPlatform()

        qsoa.authenticateEx() # authentication

        applicationName = 'Project'
        application = qsoa.runQuantumApplication(applicationName, idSolution_g, idFlow_g, idDevice_g) # run quantum gates application

        execution = qsoa.getQuantumExecutionResponse(application) # get quantum execution response

        self.assertEqual(execution.getExitCode(), 'ERR') # check exit code
        self.assertEqual(execution.getExitMessage(), 'Sequence contains no elements') # check exit message
        self.assertIsNone(execution.getSolutionName()) # check solution name
        self.assertIsNone(execution.getFlowName()) # check flow name
        self.assertIsNone(execution.getDeviceName()) # check device name
        self.assertIsNone(execution.getHistogram()) # check returns histogram
        self.assertIsNone(execution.getDuration()) # check execution token

    # GET QUANTUM EXECTUTION RESPONSE APPLICATION OBJECT
    def test_getQuantumExecutionResponse_applicationObject(self):
        qsoa = QSOAPlatform()

        qsoa.authenticateEx() # authentication

        applicationName = 'Project'
        application = qsoa.runQuantumApplication(applicationName, idSolution_g, idFlow_g, idDevice_g) # run quantum gates application

        for i in range(10):
            time.sleep(2)
            execution = qsoa.getQuantumExecutionResponse(application) # get quantum execution response

            if execution.getExitCode() == 'OK':
                break

        self.assertEqual(execution.getExitCode(), 'OK') # check exit code
        self.assertIsNone(execution.getExitMessage()) # check exit message
        self.assertIsInstance(execution.getSolutionName(), str) # check solution name
        self.assertIsInstance(execution.getFlowName(), str) # check flow name
        self.assertIsInstance(execution.getDeviceName(), str) # check device name
        self.assertIsInstance(execution.getHistogram(), dict) # check returns histogram
        self.assertIsInstance(execution.getDuration(), int) # check execution token
    
    # GET QUANTUM EXECTUTION RESPONSE BAD APPLICATION OBJECT
    def test_getQuantumExecutionResponse_badApplicationObject(self):
        qsoa = QSOAPlatform()

        qsoa.authenticateEx() # authentication

        applicationName = 'Project'
        idSolution_g = 999
        idFlow_g = 999
        idDevice_g = 999
        application = qsoa.runQuantumApplication(applicationName, idSolution_g, idFlow_g, idDevice_g) # run quantum gates application

        self.assertIsNone(application) # check execution

    # GET QUANTUM EXECTUTION RESPONSE GATES TOKEN
    def test_getQuantumExecutionResponse_gates_token(self):
        qsoa = QSOAPlatform()

        qsoa.authenticateEx() # authentication

        executionToken = '019a60ae-7f6b-402e-a6a5-a4c59b91c728'
        execution = qsoa.getQuantumExecutionResponse(executionToken, idSolution_g, idFlow_g) # get quantum execution response

        self.assertEqual(execution.getExitCode(), 'OK') # check exit code
        self.assertIsNone(execution.getExitMessage()) # check exit message
        self.assertIsInstance(execution.getSolutionName(), str) # check solution name
        self.assertIsInstance(execution.getFlowName(), str) # check flow name
        self.assertIsInstance(execution.getDeviceName(), str) # check device name
        self.assertIsInstance(execution.getHistogram(), dict) # check returns histogram
        self.assertIsInstance(execution.getDuration(), int) # check execution token

    # GET QUANTUM EXECTUTION RESPONSE ANNEALING TOKEN
    def test_getQuantumExecutionResponse_annealing_token(self):
        qsoa = QSOAPlatform()

        qsoa.authenticateEx() # authentication

        executionToken = '10a763c4-4456-4c42-ad2b-46759886d7a8'
        execution = qsoa.getQuantumExecutionResponse(executionToken, idSolution_a, idFlow_a) # get quantum execution response

        self.assertEqual(execution.getExitCode(), 'OK') # check exit code
        self.assertIsNone(execution.getExitMessage()) # check exit message
        self.assertIsInstance(execution.getSolutionName(), str) # check solution name
        self.assertIsInstance(execution.getFlowName(), str) # check flow name
        self.assertIsInstance(execution.getDeviceName(), str) # check device name
        self.assertIsInstance(execution.getHistogram(), dict) # check returns histogram
        self.assertIsInstance(execution.getDuration(), int) # check execution token


##################_____REPRESENT RESULTS_____##################

class Test_RepresentResults(unittest.TestCase):

    # REPRESENT RESULTS GATES
    def test_representResults_gates(self):
        qsoa = QSOAPlatform()

        qsoa.authenticateEx() # authentication

        executionToken = '019a60ae-7f6b-402e-a6a5-a4c59b91c728'
        execution = qsoa.getQuantumExecutionResponse(executionToken, idSolution_g, idFlow_g) # get quantum execution response

        representation = qsoa.representResults(execution) # get representation

        self.assertEqual(representation, 'Results Ploted') # check results
    
    # REPRESENT RESULTS ANNEALING
    def test_representResults_annealing(self):
        qsoa = QSOAPlatform()

        qsoa.authenticateEx() # authentication

        executionToken = '10a763c4-4456-4c42-ad2b-46759886d7a8'
        execution = qsoa.getQuantumExecutionResponse(executionToken, idSolution_a, idFlow_a) # get quantum execution response

        representation = qsoa.representResults(execution) # get representation

        self.assertIsInstance(representation, str) # check results


##################_____GET ASSET CATALOG_____##################

class Test_GetAssetCatalog(unittest.TestCase):

    #  GET ASSET CATALOG
    def test_getAssetCatalog(self):
        qsoa = QSOAPlatform()

        qsoa.authenticateEx() # authentication

        assetType = 'CIRCUIT'
        assetLevel = 'VL'
        assetCatalog = qsoa.getAssetCatalog(idSolution_g, assetType, assetLevel) # get asset catalog

        self.assertIsInstance(assetCatalog, list) # check returns a list

        firstAsset = assetCatalog[0]
        self.assertEqual(str(type(firstAsset)), "<class 'quantumpath_pythonsdk.classes.Asset.Asset'>") # check asset is an object Asset

    #  GET ASSET CATALOG BAD INPUTS
    def test_getAssetCatalog_badInputs(self):
        qsoa = QSOAPlatform()

        qsoa.authenticateEx() # authentication

        assetType = 'type'
        assetLevel = 'level'
        assetCatalog = qsoa.getAssetCatalog(idSolution_g, assetType, assetLevel) # get asset catalog

        self.assertEqual(assetCatalog, []) # check returns an empty list


class Test_GetAsset(unittest.TestCase):

    # GET ASSET
    def test_getAsset(self):
        qsoa = QSOAPlatform()

        qsoa.authenticateEx() # authentication

        assetType = 'CIRCUIT'
        assetLevel = 'VL'
        asset = qsoa.getAsset(idAsset, assetType, assetLevel) # get asset

        self.assertIsNotNone(asset) # check result
    
    # GET ASSET BAD INPUTS
    def test_getAsset_badInputs(self):
        qsoa = QSOAPlatform()

        qsoa.authenticateEx() # authentication

        idAsset = 999
        assetType = 'type'
        assetLevel = 'level'
        asset = qsoa.getAsset(idAsset, assetType, assetLevel) # get asset

        self.assertIsNone(asset) # check result


class Test_CreateAsset(unittest.TestCase):

    # CREATE ASSET
    def test_createAsset(self):
        qsoa = QSOAPlatform()

        qsoa.authenticateEx() # authentication

        assetName = 'Example1'
        assetNamespace = 'Example'
        assetDescription = '&lt;b&gt;Example&lt;/b&gt; demo qSOA v2'
        assetBody = 'circuit={"cols":[["H"],["CTRL","X"],["Measure"]]}'
        assetType = 'GATES'
        assetLevel = 'VL'

        assetManagementData = qsoa.createAsset(idSolution_g, assetName, assetNamespace, assetDescription, assetBody, assetType, assetLevel) # get asset management data

        self.assertIsNotNone(assetManagementData) # check result
    

    # CREATE ASSET EXISTING CIRCUIT
    def test_createAsset_existingCircuit(self):
        qsoa = QSOAPlatform()

        qsoa.authenticateEx() # authentication
        circuit = qsoa.CircuitGates() # create circuit
        circuit.h(0)
        circuit.cx(0, 1)
        circuit.measure(0)

        assetName = 'Example3'
        assetNamespace = 'Example'
        assetDescription = '&lt;b&gt;Example&lt;/b&gt; demo qSOA v2'
        assetBody = circuit
        assetType = 'GATES'
        assetLevel = 'VL'

        assetManagementData = qsoa.createAsset(idSolution_g, assetName, assetNamespace, assetDescription, assetBody, assetType, assetLevel) # get asset management data

        self.assertIsNotNone(assetManagementData) # check result
    

    # CREATE ASSET EXISTING FLOW
    def test_createAsset_existingFlow(self):
        qsoa = QSOAPlatform()

        qsoa.authenticateEx() # authentication
        flow = qsoa.NewFlow() # create flow
        startNode = flow.startNode() # existing node
        initNode = flow.initNode(0) # existing node
        circuitNode = flow.circuitNode('circuitName') # existing node
        repeatNode = flow.repeatNode(1000) # existing node
        endNode = flow.endNode() # existing node

        flow.linkNodes(startNode, initNode) # link nodes
        flow.linkNodes(initNode, circuitNode) # link nodes
        flow.linkNodes(circuitNode, repeatNode) # link nodes
        flow.linkNodes(repeatNode, endNode) # link nodes

        assetName = 'Flow1'
        assetNamespace = 'Example'
        assetDescription = 'Flow Description'
        assetBody = flow
        assetType = 'FLOW'
        assetLevel = 'VL'

        assetManagementData = qsoa.createAsset(idSolution_g, assetName, assetNamespace, assetDescription, assetBody, assetType, assetLevel) # get asset management data
        
        self.assertIsNotNone(assetManagementData) # check result
    

    # CREATE ASSET BAD INPUTS
    def test_createAsset_badInputs(self):
        qsoa = QSOAPlatform()

        qsoa.authenticateEx() # authentication

        idSolution_g = 999
        assetName = 'Example'
        assetNamespace = 'Example'
        assetDescription = '&lt;b&gt;Example&lt;/b&gt; demo qSOA v2'
        assetBody = 'circuit={"cols":[["H"],["CTRL","X"],["Measure"]]}'
        assetType = 'GATES'
        assetLevel = 'VL'

        assetManagementData = qsoa.createAsset(idSolution_g, assetName, assetNamespace, assetDescription, assetBody, assetType, assetLevel) # get asset management data

        self.assertIsNone(assetManagementData) # check result


class Test_UpdateAsset(unittest.TestCase):

    # UPDATE ASSET
    def test_updateAsset(self):
        qsoa = QSOAPlatform()

        qsoa.authenticateEx() # authentication
        assetType = 'CIRCUIT'
        assetLevel = 'VL'
        asset = qsoa.getAsset(idAsset, assetType, assetLevel) # get asset

        assetManagementData = qsoa.updateAsset(asset, assetDescription='test') # get asset management data

        self.assertIsNotNone(assetManagementData) # check result
    

    # UPDATE ASSET EXISTING CIRCUIT
    def test_updateAsset_existingCircuit(self):
        qsoa = QSOAPlatform()

        qsoa.authenticateEx() # authentication
        circuit = qsoa.CircuitGates() # create circuit
        circuit.h(0)
        circuit.cx(0, 1)
        circuit.measure(0)

        assetType = 'CIRCUIT'
        assetLevel = 'VL'
        asset = qsoa.getAsset(idAsset, assetType, assetLevel) # get asset

        assetManagementData = qsoa.updateAsset(asset, assetBody=circuit) # get asset management data

        self.assertIsNotNone(assetManagementData) # check result

    
    # UPDATE ASSET EXISTING FLOW
    def test_updateAsset_existingFlow(self):
        qsoa = QSOAPlatform()

        qsoa.authenticateEx() # authentication
        flow = qsoa.NewFlow() # create circuit
        startNode = flow.startNode() # existing node
        initNode = flow.initNode(0) # existing node
        circuitNode = flow.circuitNode('circuitName') # existing node
        repeatNode = flow.repeatNode(1000) # existing node
        endNode = flow.endNode() # existing node
        flow.linkNodes(startNode, initNode) # link nodes
        flow.linkNodes(initNode, circuitNode) # link nodes
        flow.linkNodes(circuitNode, repeatNode) # link nodes
        flow.linkNodes(repeatNode, endNode) # link nodes

        assetType = 'CIRCUIT'
        assetLevel = 'VL'
        asset = qsoa.getAsset(idAsset, assetType, assetLevel) # get asset

        assetManagementData = qsoa.updateAsset(asset, assetBody=flow) # get asset management data

        self.assertIsNotNone(assetManagementData) # check result


    # UPDATE ASSET BAD INPUTS
    def test_updateAsset_badInputs(self):
        qsoa = QSOAPlatform()

        qsoa.authenticateEx() # authentication
        idAsset = 999
        assetType = 'type'
        assetLevel = 'level'
        asset = qsoa.getAsset(idAsset, assetType, assetLevel) # get asset

        assetManagementData = qsoa.updateAsset(asset, assetDescription = '&lt;b&gt;Entanglement&lt;/b&gt; test') # get asset management data

        self.assertIsNone(assetManagementData) # check result


class Test_DeleteAsset(unittest.TestCase):

    # DELETE ASSET OBJECT
    def test_deleteAsset_object(self):
        qsoa = QSOAPlatform()

        qsoa.authenticateEx() # authentication
        assetName = 'Example_Delete'
        assetNamespace = 'Example'
        assetDescription = '&lt;b&gt;Example&lt;/b&gt; demo qSOA v2'
        assetBody = 'circuit={"cols":[["H"],["CTRL","X"],["Measure"]]}'
        assetType = 'GATES'
        assetLevel = 'VL'
        createdAsset = qsoa.createAsset(idSolution_g, assetName, assetNamespace, assetDescription, assetBody, assetType, assetLevel) # create asset

        if createdAsset:
            assetType = 'CIRCUIT'
            assetLevel = 'VL'
            assetCatalog = qsoa.getAssetCatalog(idSolution_g, assetType, assetLevel) # get asset catalog
            lastAsset = assetCatalog[-1]

            assetDeleted = qsoa.deleteAsset(lastAsset) # delete asset

        self.assertTrue(assetDeleted) # check result


    # DELETE ASSET MANUALLY
    def test_deleteAsset_manually(self):
        qsoa = QSOAPlatform()

        qsoa.authenticateEx() # authentication
        assetName = 'Example_Delete'
        assetNamespace = 'Example'
        assetDescription = '&lt;b&gt;Example&lt;/b&gt; demo qSOA v2'
        assetBody = 'circuit={"cols":[["H"],["CTRL","X"],["Measure"]]}'
        assetType = 'GATES'
        assetLevel = 'VL'
        createdAsset = qsoa.createAsset(idSolution_g, assetName, assetNamespace, assetDescription, assetBody, assetType, assetLevel) # create asset

        if createdAsset:
            assetType = 'CIRCUIT'
            assetLevel = 'VL'
            assetCatalog = qsoa.getAssetCatalog(idSolution_g, assetType, assetLevel) # get asset catalog
            lastAsset = assetCatalog[-1]

            assetDeleted = qsoa.deleteAsset(lastAsset.getId(), assetType) # delete asset

        self.assertTrue(assetDeleted) # check result


class Test_GetAssetManagementResult(unittest.TestCase):

    # GET ASSET MANAGEMENT RESULT
    def test_getAssetManagementResult(self):
        qsoa = QSOAPlatform()
        
        qsoa.authenticateEx() # authentication

        lifecycleToken = 'b88e67b2-2935-42d0-bbff-832b9fb8632c'

        assetManagementResult = qsoa.getAssetManagementResult(lifecycleToken) # get asset management data

        self.assertIsNotNone(assetManagementResult) # check result


if __name__ == '__main__':
    unittest.main()