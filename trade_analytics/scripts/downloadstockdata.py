
from dataapp import tasks as dtatks
from dataapp import models as dtamd
from stockapp import libs as stklibs
def run():
	# Download all data
	# dtamd.Stockprice.objects.all().delete()
	# stklibs.resetstockmeta()
	dtatks.RunDataDownload()
	
