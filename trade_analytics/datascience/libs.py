import cloudpickle as cldpkl
from dill.source import getsource
from datascience import models as dtscmd

def register_dataset(project_Name,project_Info,Datatype,GroupName,tag,data_format,Modeltype,use_project_ifexists=True):

	# project_Name="PredictReturn_TSLA", 
	# use_project_ifexists=True,
	# project_Info={'description': "Testing the algorithms on TSLA to predict next 10 day return \n"+
	#                              "Data taken on every Friday"},
	# Datatype='RawProcessed',
	# GroupName="Fullstocktime",
	# tag="1",
	# data_format='npz',
	# Modeltype='Regression',

	if dtscmd.Project.objects.filter(Name=project_Name).exists()==True:
		print "Project ",project_Name, " already exists"
		project=dtscmd.Project.objects.get(Name=project_Name)

		if use_project_ifexists:
			pass	
		else:
			print "project already exists"
			# return None

	else:
		project=dtscmd.Project(Name=project_Name,Info=project_Info)
		project.save()

	if dtscmd.Data.objects.filter(Project=project,GroupName=GroupName,tag=tag,Datatype=Datatype,Dataformat=data_format,Modeltype=Modeltype).exists():
		data=dtscmd.Data.objects.get(Project=project,GroupName=GroupName,tag=tag,Datatype=Datatype,Dataformat=data_format,Modeltype=Modeltype)
		print "The dataset already exists"
		# return None

	else:
		data=dtscmd.Data(Project=project,GroupName=GroupName,tag=tag,Datatype=Datatype,Dataformat=data_format,Modeltype=Modeltype)
		data.save()
		data.initialize()

	print ("project id","data id")," : ",(project.id,data.id)
	return project.id,data.id


# @register_func(overwrite_if_exists=False)
class registerfunc(object):
	def __init__(self,Group='',RequiredGroup=[],RequiredImports=[],overwrite_if_exists=False):
		self.Group=Group
		self.RequiredImports=RequiredImports
		self.RequiredGroup=RequiredGroup
		self.overwrite_if_exists=overwrite_if_exists
   	def __call__(self,func):
   		func.id=None

   		if self.overwrite_if_exists:
   			if dtscmd.ComputeFunc.objects.filter(Name=func.__name__,Group=self.Group).exists():
   				print "over writing previous function"
   				cf=dtscmd.ComputeFunc.objects.get(Name=func.__name__,Group=self.Group)
   			else:
   				print "creating new func"
   				cf=dtscmd.ComputeFunc(Name=func.__name__,Group=self.Group)
   		else:
   			print "creating new func"
			cf=dtscmd.ComputeFunc(Name=func.__name__,Group=self.Group)

   		cf.Info['doc']=func.__doc__
   		cf.PklCode=cldpkl.dumps(func)
   		cf.RequiredGroup['Group']=self.RequiredGroup
   		cf.RequiredImports['import']=self.RequiredImports

   		# cf.PklCode=cf.PklCode.replace('\0','#*0*')
   		# cf.PklCode=''

   		try:
   			cf.SrcCode=getsource(func)
   		except:
   			cf.SrcCode=''

   		cf.save()
   		print "saving function : ", cf.Name

   		func.id=cf.id
 		print "function id = ",cf.id
   		return func


# def getfunc(id):
# 	funcObj=dtscmd.ComputeFunc.objects.get(id=id)
# 	for imp in funcObj.RequiredImports['import']:
# 		exec(imp)
# 	func=cldpkl.loads(funcObj.PklCode)