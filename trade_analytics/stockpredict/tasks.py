## Create Raw Stock Datasets ##################

@shared_task
def CreateBaseStockData_ShardsBySymbol(SymbolId,funcId,dataId):
	Func=dtscmd.ComputeFunc.objects.filter(id=funcId).last().getfunc()
	DataXY=Func(SymbolId,'Train')

	data=dtscmd.Data.objects.get(id=dataId)	
	shard=dtscmd.DataShard(Data=data)
	shard.save()
	print "starting to save : ",SymbolId
	shard.savedata(X=DataXY[0][0],Y=DataXY[1][0],Meta={'MetaX':DataXY[0][1],'MetaY':DataXY[1][1]})

@shared_task
def CreateBaseStockData_bySymbols(funcId,dataId):
	SymbolIds=stkmd.Stockmeta.objects.all().values_list('id',flat=True)
	for SymbolId in SymbolIds:
		CreateBaseStockData_ShardsBySymbol.delay(SymbolId,funcId,dataId)

