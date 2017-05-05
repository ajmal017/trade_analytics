import os
import inspect
import utility.models as md

"""
- keeps track of .py files in a folder
- all information in each .py is pulled as meta information
- each .py is imported separately
- you have to manually sync to db, thewhole .py is synced
- when you edit, the whole .py is edited at once
- you can have same function names or class names across files
- each inherited class should have unique id/label
- syncs the code and the meta information with db
- define a default file that defines the base classes and all the required packages needed
- keeps track of

"""

def GetClasses(ff):
	D=[]
	for pp in inspect.getmembers(inspect.getmembers(ff)):
		if inspect.isclass(pp[1]):
			if issubclass(pp[1],md.index):
				D.append( {'classname': pp[0],'description':inspect.getdoc(pp[1]),'filename':ff,'name':md.index.name} )
			elif issubclass(pp[1],md.feature):
				D.append( {'classname': pp[0],'description':inspect.getdoc(pp[1]),'filename':ff,'name':md.feature.name} )
			elif issubclass(pp[1],md.query):
				D.append( {'classname': pp[0],'description':inspect.getdoc(pp[1]),'filename':ff,'name':md.query.name} )
			else:
				raise NotImplemented("model class not implemented")


