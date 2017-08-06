
from datascience import tasks as dtsctks

def run(*args):
	# Download all data
	# dtamd.Stockprice.objects.all().delete()
	# stklibs.resetstockmeta()
	projectId= args[0]
	dtsctks.TrainProject(projectId)

	
