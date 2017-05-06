from utility  import codemanager as cdmng
import stockapp.models as md
import utility.models as utmd
import os
import imp


importss="""
from %(module)s import %(class)s
C=%(class)s() 
"""

def SyncIndices_files2db():
	IndexCodes=md.IndexCode.objects.all()
	for indcode in IndexCodes:
		if indcode.File is None:
			indcode.File=indcode.getfilepath()

		foo = imp.load_source(indcode.getimportpath(),indcode.File)
		D=cdmng.GetClasses(indcode.File,foo)
		print "D = ", D
		for d in D:
			if d['name']==utmd.index.name:
				if md.IndexClass.objects.filter(IndexCode=indcode,ClassName=d['classname']).exists():
					indclass=md.IndexClass.objects.get(IndexCode=indcode,ClassName=d['classname'])
					indclass.IndexDescription=d['description']
				else:
					indclass=md.IndexClass(IndexCode=indcode,ClassName=d['classname'], ClassDescription=d['description'] )
				indclass.save()

				C=None
				ss=importss%{'module':indcode.getimportpath(),'class': d['classname']}
				exec(ss)
				print "C.meta = ", C.meta
				for indx in C.meta.keys():
					if md.Index.objects.filter(IndexLabel=indx ).exists():
						index=md.Index.objects.get(IndexLabel=indx )
						index.IndexClass=indclass
						index.IndexName=C.meta[indx]['name']
						index.IndexDescription=C.meta[indx]['description']
						index.IndexResultType=str(C.meta[indx]['resulttype'])
						index.computefeatures=C.meta[indx]['computefeatures']
						index.save()

					else: 
						index=md.Index(IndexClass=indclass,IndexName=C.meta[indx]['name'],IndexDescription=C.meta[indx]['description'],
								IndexLabel=indx,IndexResultType=str(C.meta[indx]['resulttype']),computefeatures=C.meta[indx]['computefeatures'])
						index.save()

		with open(indcode.File,'r') as codestr:
			indcode.Code=codestr.read()
		
		indcode.save()
		

def SyncIndices_db2files():
	IndexCodes=md.IndexCode.objects.all()
	for indcode in IndexCodes:
		if indcode.File is None:
			indcode.File=indcode.getfilepath()

		with open(indcode.File,'w') as codestr:
			codestr.write(indcode.Code)