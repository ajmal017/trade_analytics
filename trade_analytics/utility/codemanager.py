import os
import inspect
import utility.models as md
from types import ModuleType
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


def import_computeindexclass(codestr,modulename,membername=None):
	compiled = compile(codestr, '', 'exec')
	module = ModuleType(modulename)
	exec(compiled, module.__dict__)
	if membername:
		return (module,eval("module.%s"%membername))
	else:
		return (module,None)





def GetClasses(module):
	D=[]
	for pp in inspect.getmembers(module):
		if inspect.isclass(pp[1]):
			if issubclass(pp[1],md.index):
				D.append( {'classname': pp[0],'description':inspect.getdoc(pp[1]),'name':md.index.name} )
			elif issubclass(pp[1],md.feature):
				D.append( {'classname': pp[0],'description':inspect.getdoc(pp[1]),'name':md.feature.name} )
			elif issubclass(pp[1],md.query):
				D.append( {'classname': pp[0],'description':inspect.getdoc(pp[1]),'name':md.query.name} )
			elif issubclass(pp[1],md.chart):
				D.append( {'classname': pp[0],'description':inspect.getdoc(pp[1]),'name':md.chart.name} )
			else:
				raise NotImplemented("model class not implemented")

	return D
