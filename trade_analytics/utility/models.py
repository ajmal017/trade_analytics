import abc
import json

class Value(object):
	def __init__(self,value=None,serializer='str',deserializer='int'):
		"""
		serializer have to be functions or lambda fnctions
		"""
		self.value=value
		self.serializedvalue=None
		self.serializer=serializer
		self.deserializer=deserializer
	
	def SerializeValue(self):
		if self.serializedvalue:
			return self.serializedvalue
		F=eval(self.serializer)
		self.serializedvalue=F(self.value)

		return {'class':'Value','deserializer':self.deserializer,'serializer':self.serializer,'serializedvalue':self.serializedvalue }
	
	@classmethod
	def deserialize(cls,obj):
		obj=json.loads(obj)
		F=eval(obj['deserializer'] )
		value=F(obj['serializedvalue'])
		return cls(value=value,serializer=obj['serializer'],deserializer=obj['deserializer'])


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

		if kwargs['label'] not in self.meta.keys():
			self.meta[kwargs['label']]={}

		for key,value in kwargs.items():
			if key!='label':
				self.meta[kwargs['label']][key]=value

	def setvalue(self,key,value,serilizer=str):
		if key not in self.meta:
			raise KeyError(key+" not registered")
		self.meta[key]['value']=value

	def getvalue(self,key):
		if key not in self.meta:
			raise KeyError(key+" not registered")
		return self.meta[key]['value']

	def sandoxtest(self):
		pass
	def isvalid(self):
		pass
	def compute(self,*args,**kwargs):
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

class chart(basecode):
	name='chart'
