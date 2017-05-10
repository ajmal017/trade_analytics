


from stockapp import models as stkmd
from stockapp import tasks as stktks
def run():
	# Download all data
	stktks.SyncPrice2Meta()





