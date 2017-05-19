


from stockapp import tasks as stktks
from featureapp import models as ftmd
from queryapp import models as qrymd

def run():
	# Download all data
	# stktks.SyncPrice2Meta()
	ftmd.FeatureComputeCode.Sync_files2db()
	qrymd.QueryComputeCode.Sync_files2db()
	





