


from stockapp import models as stkmd
def run():
	# Download all data
	print "ToDo = ",stkmd.ComputeStatus_Stockdownload.objects.filter(Status='ToDo').count()
	print "Success = ",stkmd.ComputeStatus_Stockdownload.objects.filter(Status='Success').count()
	print "Fail = ",stkmd.ComputeStatus_Stockdownload.objects.filter(Status='Fail').count()
	print "Run = ",stkmd.ComputeStatus_Stockdownload.objects.filter(Status='Run').count()
	





