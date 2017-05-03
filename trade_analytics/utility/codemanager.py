import pandas as pd
import os

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


class codemanager(object):
	"""
	- provide the folder to track and sync
	- provide the table to push into the meta information
	"""
	def __init__(self,folder,tableorm):
		if not os.path.isdir(folder):
			raise Exception("%s folder not there" % folder)
		if not os.path.isfile(os.path.join(folder,'__init__.py')):
			raise Exception("%s folder is not a module" % folder)

		self.pythonfiles=[f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder,f)) and '.py' in f  ]
		
