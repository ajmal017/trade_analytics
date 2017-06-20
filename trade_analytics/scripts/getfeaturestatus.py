


from featureapp import models as ftmd
def run():
	# Download all data
	print "ToDo = ",ftmd.ComputeStatus_Feature.objects.filter(Status='ToDo').count()
	print "Success = ",ftmd.ComputeStatus_Feature.objects.filter(Status='Success').count()
	print "Fail = ",ftmd.ComputeStatus_Feature.objects.filter(Status='Fail').count()
	print "Run = ",ftmd.ComputeStatus_Feature.objects.filter(Status='Run').count()
	





