import sys
sys.path.append('c:\\Users\\alonso.martint\\developer\\QuantumPath_PyhonSDK')

from QuantumPathQSOAPySDK import QSOAPlatform

qsoa = QSOAPlatform(configFile=True)

solutionList = qsoa.getQuantumSolutionList()

activeEnvironment = qsoa.setActiveEnvironment('lab')

print('Solution List:', solutionList)