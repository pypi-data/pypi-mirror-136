import PyEFVLib
from PyEFVLib.BoundaryConditions import DirichletBoundaryCondition, NeumannBoundaryCondition 
import json, os, numpy as np

class NumericalSettings:
	def __init__(self, timeStep, finalTime=np.inf, tolerance=1e-4, maxNumberOfIterations=1000):
		self.timeStep = timeStep
		self.finalTime = finalTime
		self.tolerance = tolerance
		self.maxNumberOfIterations = maxNumberOfIterations

	def init(self, problemData):
		self.problemData = problemData

		self.problemData.timeStep = self.timeStep
		self.problemData.finalTime = self.finalTime
		self.problemData.tolerance = self.tolerance
		self.problemData.maxNumberOfIterations = self.maxNumberOfIterations

class PropertyData:
	def __init__(self, propertiesDict):
		self.propertiesDict = propertiesDict
		self.properties = list(list(self.propertiesDict.values())[0].keys())

	def init(self, problemData):
		self.problemData = problemData
		self.regions = self.problemData.grid.gridData.regionsNames

		for regionName in self.propertiesDict.keys():
			if not regionName in self.problemData.grid.gridData.regionsNames:
				print(f"Warning! Region {regionName} not in the grid.")
		for regionName in self.problemData.grid.gridData.regionsNames:
			if not regionName in self.propertiesDict.keys():
				raise Exception(f"Error, must specify {regionName} properties.")

	def get(self, propertyName, handle=0):
		if handle in range(len(self.regions)):
			if propertyName in self.properties:
				return self.propertiesDict[self.regions[handle] ][propertyName]
			else:
				raise Exception(f"Property {propertyName} not defined")
		else:
			raise Exception(f"Invalid region handle {handle}")

	def set(self, handle, propertyName, value):
		if handle in range(len(self.regions)):
			if propertyName in self.properties:
				self.propertiesDict[self.regions[handle] ][propertyName] = value
			else:
				raise Exception(f"Property {propertyName} not defined")
		else:
			raise Exception(f"Invalid region handle {handle}")

class BoundaryConditions:
	def __init__(self, boundaryConditionsDict):
		self.boundaryConditionsDict = boundaryConditionsDict

	def init(self, problemData):
		self.problemData = problemData

		variables = self.boundaryConditionsDict.keys()
		boundaryNames = self.problemData.grid.gridData.boundariesNames

		for boundaryName in list(self.boundaryConditionsDict.values())[0].keys():
			if boundaryName != "InitialValue" and not boundaryName in boundaryNames:
				print(f"Warning! Boundary {boundaryName} not in the grid.")
		for boundaryName in boundaryNames:
			if not boundaryName in list(self.boundaryConditionsDict.values())[0].keys():
				raise Exception(f"Error, must specify {boundaryName} condition.")

		self.neumannBoundaries   = { variable : [] for variable in variables }
		self.dirichletBoundaries = { variable : [] for variable in variables }
		self.boundaryConditions  = [ dict() for boundary in self.problemData.grid.boundaries ]

		def getFunction(expr):
			from numpy import pi, sin, cos, tan, arcsin, arccos, arctan, sinh, cosh, tanh, arcsinh, arccosh, arctanh, sqrt, e , log, exp, inf, mod, floor
			def function(x,y,z):
				return eval( expr.replace('x',str(x)).replace('y',str(y)).replace('z',str(z)) )
			return function
		
		self.initialValues = dict()
		for variable in variables:
			initialValue = self.boundaryConditionsDict[variable]["InitialValue"]
			numberOfVertices = self.problemData.grid.numberOfVertices
			if np.isscalar(initialValue) and not isinstance(initialValue, (str,)):
				self.initialValues[variable] = np.repeat( initialValue, numberOfVertices )
			elif isinstance( initialValue, (list, np.ndarray) ):
				if len(initialValue) == numberOfVertices:
					self.initialValues[variable] = np.array(initialValue)
				else:
					raise Exception(f"Length of \"{variable}\" InitialValue must be equal to the number of vertices ({numberOfVertices})")
			elif isinstance( initialValue, (str,) ):
				function = getFunction(initialValue)
				self.initialValues[variable] = np.array([function(v.x,v.y,v.z) for v in self.problemData.grid.vertices])

		bcHandle = 0
		for idx, boundary in enumerate(self.problemData.grid.boundaries):
			for variable in variables:
				if self.boundaryConditionsDict[variable][boundary.name]["type"] == PyEFVLib.Constant:
					expression = False
				elif self.boundaryConditionsDict[variable][boundary.name]["type"] == PyEFVLib.Variable:
					expression = True
				else:
					raise Exception(f"Invalid Boundary Condition Type {self.boundaryConditionsDict[variable][boundary.name]['type']}")

				if self.boundaryConditionsDict[variable][boundary.name]["condition"] == PyEFVLib.Neumann:
					bcValue = self.boundaryConditionsDict[variable][boundary.name]["value"]
					bc = NeumannBoundaryCondition(self.problemData.grid, boundary, bcValue, bcHandle, expression=expression)
					self.neumannBoundaries[variable].append(bc)
					self.boundaryConditions[idx][variable] = bc
					
				elif self.boundaryConditionsDict[variable][boundary.name]["condition"] == PyEFVLib.Dirichlet:
					bcValue = self.boundaryConditionsDict[variable][boundary.name]["value"]
					bc = DirichletBoundaryCondition(self.problemData.grid, boundary, bcValue, bcHandle, expression=expression)
					self.dirichletBoundaries[variable].append(bc)
					self.boundaryConditions[idx][variable] = bc
					
				else:
					raise Exception("Invalid boundary condition!")
				bcHandle += 1


		self.problemData.dirichletBoundaries = self.dirichletBoundaries
		self.problemData.neumannBoundaries   = self.neumannBoundaries
		self.problemData.boundaryConditions  = self.boundaryConditions
		self.problemData.initialValues  	 = self.initialValues

class ProblemData:
	def __init__(self, 
		meshFilePath,
		propertyData,
		boundaryConditions=None,
		numericalSettings=NumericalSettings(0.0),
		outputFilePath=None,
	):
		self.meshFilePath		= meshFilePath
		self.outputFilePath		= outputFilePath
		self.propertyData 		= propertyData

		self.parsePaths()
		self.createGrid()
		numericalSettings.init(self)
		propertyData.init(self)
		if boundaryConditions:
			boundaryConditions.init(self)

	def parsePaths(self):
		self.libraryPath = os.path.realpath( os.path.join(os.path.dirname(__file__), *(2*[os.path.pardir])) )
		meshesPath = os.path.realpath( os.path.join(os.path.dirname(__file__), *(1*[os.path.pardir]), "meshes") )
		resultsPath = os.path.realpath( os.path.join(os.path.dirname(__file__), *(1*[os.path.pardir]), "results") )

		self.meshFilePath = os.path.join(*self.meshFilePath.replace("{MESHES}", meshesPath).split("/"))
		self.outputFilePath = os.path.join(*self.outputFilePath.replace("{RESULTS}",resultsPath).split("/"))

	def createGrid(self):
		self.grid = PyEFVLib.read(self.meshFilePath)