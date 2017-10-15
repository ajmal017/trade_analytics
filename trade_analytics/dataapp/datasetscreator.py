
from dataapp import DataManager

def CreateStockData_base_bySymbol(SymbolId,TFs,Mode):
	DM=DataManager(SymbolIds=[SymbolId])
	Symbol=DM.Stockmeta.objects.get(id=SymbolId)
	DM=DataManager(SymbolId,RequiredCols=None,Append2RequiredCols=[],DF=None)
	Data=[]

	width=270
	width_fut=70

	T0TF_dict_X=map(lambda x: { 'TF' :x.date(),'width':width,'Symbol':Symbol },TFs )
	if Mode=='Train':
		T0TF_dict_Y=map(lambda x: { 'T0':x.date(), 'width':width_fut,'Symbol':Symbol },TFs)
	else:
		T0TF_dict_Y=None

	for X,Meta in DM.Iterbatchdata_Ordered([T0TF_dict_X,T0TF_dict_Y],padding=True,roundT2dfdate=False):
		Data.append((X,Meta))


	return Data

def CreateStockData_base_byTF(TF,Mode):
	DM=DataManager()
	Symbols=DM.Stockmeta.objects.all()
	DM=DataManager(list(Symbols.values_list('id',flat=True)),RequiredCols=None,Append2RequiredCols=[],DF=None)
	Data=[]

	width=270
	width_fut=70

	T0TF_dict_X=map(lambda x: { 'TF' :TF.date(),'width':width,'Symbol':x.Symbol },Symbols )
	if Mode=='Train':
		T0TF_dict_Y=map(lambda x: { 'T0':TF.date(), 'width':width_fut,'Symbol':x.Symbol },Symbols)
	else:
		T0TF_dict_Y=None

	for X,Meta in DM.Iterbatchdata_Ordered([T0TF_dict_X,T0TF_dict_Y],padding=True,roundT2dfdate=False):
		Data.append((X,Meta))


	return Data
