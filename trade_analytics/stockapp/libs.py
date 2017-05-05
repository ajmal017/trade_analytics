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
				indclass.save()

				exec("""
					from %(module)s import %(class)s
					C=%(class)s() 
					""")
				for indx in C.meta.keys():
					if md.Index.objects.filter(IndexLabel=C.meta[indx]['label'] ).exists():
						index=md.Index.objects.get(IndexLabel=C.meta[indx]['label'] )
						index.IndexClass=indclass
						index.IndexName=C.meta[indx]['name']
						index.IndexDescription=C.meta[indx]['description']
						index.IndexResultType=str(C.meta[indx]['resulttype'])
						index.computefeatures=C.meta[indx]['computefeatures']
						index.save()

					else: 
						index=md.Index(IndexClass=indclass,IndexName=C.meta[indx]['name'],IndexDescription=C.meta[indx]['description'],
								IndexLabel=C.meta[indx]['label'],IndexResultType=str(C.meta[indx]['resulttype']),computefeatures=C.meta[indx]['computefeatures'])
						index.save()

		with open(indcode.File,'r') as codestr:
			indcode.Code=codestr.read()
		
		

def SyncIndices_db2files():
	IndexCodes=md.IndexCode.objects.all()
	for indcode in IndexCodes:
		if indcode.File is None:
			indcode.File=indcode.getfilepath()

		with open(indcode.File,'w') as codestr:
			codestr.write(indcode.Code)