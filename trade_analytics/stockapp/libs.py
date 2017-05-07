from utility  import codemanager as cdmng
import stockapp.models as md
import utility.models as utmd
import os
import imp
import shutil
import pandas as pd
import time






def addIndex(SymbolName,stkgrp,index,Sector=None,Industry=None,User=None):
	if md.Stockmeta.objects.filter(Symbol=SymbolName).exists():
		return {'status':'Fail','what':"Symbol "+SymbolName+" already exists"}
	# add the symbol to stockmeta
	stk=md.Stockmeta(Symbol=SymbolName,Status='Active',Update=False,Derived=True,ComputeFeature=True,Sector=Sector,Industry=Industry,User=User)
	stk.save()

	stkgrpind=md.StockGroupIndex(Symbol=stk,Index=index,StockGroup=stkgrp)
	stkgrpind.save()
	return {'status':'Success','what':"Symbol "+SymbolName+" added to database"}

def SyncIndices_files2db():
	IndexCodes=md.IndexComputeCode.objects.all()
	for indcode in IndexCodes:
		if indcode.File is None:
			indcode.File=indcode.getfilepath()

		foo = imp.load_source(indcode.getimportpath(),indcode.File)
		D=cdmng.GetClasses(foo)

		# if a class is in db but not in the new file, then delete the class and its related labels
		for indclass in md.IndexComputeClass.objects.filter(IndexComputeCode=indcode):
			flg=False
			for d in D:
				if d['classname']==indclass.ClassName:
					flg=True
			if flg==False:
				md.Index.objects.filter(IndexComputeClass=indclass).delete()
				indclass.delete()

		# if a label is present in db but not in new file, then delete the label and the class
		for indx in md.Index.objects.filter(IndexComputeClass__IndexComputeCode__id=indcode.id):
			flg=False
			for d in D:
				exec("from %(module)s import %(class)s"%{'module':indcode.getimportpath(),'class': d['classname']})
				C=eval("%(class)s()"%{'class': d['classname']} )
				if indx.IndexLabel in C.meta.keys():
					flg=True
			if flg==False:
				indx.delete()

		for d in D:
			if d['name']==utmd.index.name:
				if md.IndexComputeClass.objects.filter(IndexComputeCode=indcode,ClassName=d['classname']).exists():
					indclass=md.IndexComputeClass.objects.get(IndexComputeCode=indcode,ClassName=d['classname'])
					indclass.IndexDescription=d['description']
				else:
					indclass=md.IndexComputeClass(IndexComputeCode=indcode,ClassName=d['classname'], ClassDescription=d['description'] )
				indclass.save()

				exec("from %(module)s import %(class)s"%{'module':indcode.getimportpath(),'class': d['classname']})
				C=eval("%(class)s()"%{'class': d['classname']} )
				for indx in C.meta.keys():
					if md.Index.objects.filter(IndexLabel=indx ).exists():
						index=md.Index.objects.get(IndexLabel=indx )
						index.IndexComputeClass=indclass
						index.IndexName=C.meta[indx]['name']
						index.IndexDescription=C.meta[indx]['description']
						index.IndexResultType=str(C.meta[indx]['resulttype'])
						index.computefeatures=C.meta[indx]['computefeatures']
						index.save()

					else: 
						index=md.Index(IndexComputeClass=indclass,IndexName=C.meta[indx]['name'],IndexDescription=C.meta[indx]['description'],
								IndexLabel=indx,IndexResultType=str(C.meta[indx]['resulttype']),computefeatures=C.meta[indx]['computefeatures'])
						index.save()


		with open(indcode.File,'r') as codestr:
			indcode.Code=codestr.read()
		
		indcode.save()
		
		

def SyncIndices_db2files():
	IndexCodes=md.IndexComputeCode.objects.all()
	for indcode in IndexCodes:
		if indcode.File is None:
			indcode.File=indcode.getfilepath()

		if os.path.isfile(indcode.File):
			filetime=pd.to_datetime(time.ctime(os.path.getmtime(indcode.File)))
			if indcode.updated_at<filetime:
				# first make a copy of that file and then copy dbfile to disk
				shutil.move(indcode.File,indcode.File.replace('.py',filetime.strftime("%Y-%m-%d_%H-%M-%S")+'.py'))

		with open(indcode.File,'w') as codestr:
			codestr.write(indcode.Code)