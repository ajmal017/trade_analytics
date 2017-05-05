from utility  import codemanager as cdmng
import stockapp.models as md
import utility.models as utmd
import os



def SyncIndices_files2db():
	IndexCodes=md.IndexCode.objects.all()
	for indcode in IndexCodes:
		if indcode.File is None:
			indcode.File=indcode.getfilepath()

		D=cdmng.GetClasses(indcode.File)
		for d in D:
			if d['name']==utmd.index.name:
				if md.IndexClass.objects.filter(IndexCode=indcode,IndexName=d['classname']).exists():
					indclass=md.IndexClass.objects.get(IndexCode=indcode,IndexName=d['classname'])
					indclass.IndexDescription=d['description']
				else:
					indclass=md.IndexClass(IndexCode=indcode,IndexName=d['classname'], IndexDescription=d['description'] )


		with open(indcode.File,'r') as codestr:
			indcode.Code=codestr.read()
		
		indclass.save()

def SyncIndices_db2files():
	IndexCodes=md.IndexCode.objects.all()
	for indcode in IndexCodes:
		if indcode.File is None:
			indcode.File=indcode.getfilepath()

		with open(indcode.File,'w') as codestr:
			indcode.Code=codestr.write()