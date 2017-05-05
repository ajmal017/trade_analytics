
import utility.models as md


class AveragePrice(md.index):
	"""
	Take the average price of all the stocks in the group
	"""
	
	def __init__(self,*args,**kwargs):
		super(AveragePrice,self).__init__(*args,**kwargs)
		
		self.register(description="testing",name="SMA greater than 10",label="SMA10",resulttype=int,
						scale=['absolute','%'],operations=['<','>','<=','>=','!=','between'],computefeatures=True)
		self.register(description="testing",name="SMA greater than 20",label="SMA20",resulttype=int,
						scale=['absolute','%'],operations=['<','>','<=','>=','!=','between'],computefeatures=True)

	def compute(self):
		self.setvalue("SMA10",33)
		self.setvalue("SMA20",50)



