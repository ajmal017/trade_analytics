



@mnt.logperf('datascience',printit=True)
def CreateStockData_ShardsBySymbol(T0TFSymbol_dict_X,T0TFSymbol_dict_Y,dataId):
	"""
	T0TFSymbol_dict= [{'T0':,'Tf':,'Symbol':},{}]
	"""
	dfinstants_X=pd.DataFrame(T0TFSymbol_dict_X)
	dfinstants_Y=pd.DataFrame(T0TFSymbol_dict_Y)

	BatchData=dtalibs.Getbatchdata([dfinstants_X,dfinstants_Y],padding=['OnTop','FromBottom'])

	X,MetaX=BatchData[0]
	Y,MetaY=BatchData[1]

	
	
	data=dtscmd.Data.objects.get(id=dataId)	
	shard=dtscmd.DataShard(Data=data)
	shard.save()
	print "starting to save"
	shard.savedata(X=X,Y=Y,Meta={'MetaX':MetaX,'MetaY':MetaY})

