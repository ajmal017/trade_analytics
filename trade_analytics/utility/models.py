import abc

class basecode(object):
	def __init__(self):
		self.meta={}

	def register(self,*args,**kwargs):
		"""
		register the meta information: like description, names labels etc
		need unique label
		"""
		if 'label' not in kwargs:
			raise KeyError("label is required")

		if 'label' not in self.meta.keys():
			self.meta['label']={}

		for key,value in kwargs:
			self.meta['label'][key]=value

	def setvalue(self,key,value):
		if key not in self.meta:
			raise KeyError(key+" not registered")
		self.meta[key]['value']=value

	def sandoxtest(self):
		pass
	def isvalid(self):
		pass
	def compute(self):
		pass
	def finalize(self):
		"""
		return the final
		"""
		pass



class index(basecode):
	name='index'
	


class feature(basecode):
	name='feature'
	

class query(basecode):
	name='query'
