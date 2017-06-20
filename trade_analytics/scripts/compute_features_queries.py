

from featureapp import tasks as fttks
from queryapp import tasks as qrytks

def run():
	# Download all data
	# dtamd.Stockprice.objects.all().delete()
	# stklibs.resetstockmeta()
	

	fttks.processfeatures()
	qrytks.processqueries()
	
