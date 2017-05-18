


from stockapp import tasks as stktks
from featureapp import models as ftmd
def run():
	# Download all data
	# stktks.SyncPrice2Meta()
	ftmd.FeatureComputeCode.Sync_files2db()
	





