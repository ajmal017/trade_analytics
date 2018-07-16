
from dataapp import tasks as dtatks
from stockapp import models as stkmd
import computeapp.models as cmpmd

def RunDataDownload():
	# get chumks of ids to work on. This is a iterable of lists
	compute_session=cmpmd.ComputeSession.make_newsession('PriceUpdate','None')
	# run in parallel
	stocks=stkmd.Stockmeta.objects.filter(Derived=False).values_list('id',flat=True)
	for stk in stocks:
		dtatks.UpdatePriceData.delay(stk,compute_session.id)




def run():
	RunDataDownload()
	
