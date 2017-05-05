
import utility.models as md


class AveragePrice(md.index):
	"""
	Take the average price of all the stocks in the group
	"""
	def __init__(self):
		pass
	def register(self,*args,**kwargs):
		pass
	def sandoxtest(self):
		pass
	def isvalid(self):
		pass
	def finalize(self):
		pass
	def compute(self):
		self.register(description="testing",name="SMA greater than 10",label="SMA10",value=33,resulttype=int,
						scale=['absolute','%'],operations=['<','>','<=','>=','!=','between'],computefeatures=True)
		self.register(description="testing",name="SMA greater than 20",label="SMA20",value=33,resulttype=int,
						scale=['absolute','%'],operations=['<','>','<=','>=','!=','between'],computefeatures=True)



