import pandas as pd
import numpy as np

# tol is tolerance for tol number of days. so even though it misses out for tol days it still counts as consecutive
def Rallylength(x,tol=2):
	if len(x)==0:
		return [[]]
	if len(x)==1:
		return [[x]]
		
	x=np.array(x)
	x=np.append(x,x[-1]+1)

	Q=[]
	cnt=0
	j=0
	for i in range(1,len(x)):
		if x[i]-x[i-1]<=tol:
			cnt=cnt+1
			pass
		else:
			Q.append(x[j:i])
			j=i
			cnt=0
		# print x[i]
	if cnt>0:
		Q.append(x[j:i])
	return Q



def f(x):
	return x

def testmax(data):
	import os
	from django.conf import settings
	fname=os.path.join( settings.BASE_DIR,'research' ,'FeaturesCode_check.py' )
	import py_compile

	name=data['name']
	code_str=data['code_str']
	data={
		'df':pd.read_json(data['df']),
		'T':data['T'],
		'TrendsMid':pd.read_json( data['TrendsMid'] ),
		'TrendsTop':pd.read_json( data['TrendsTop'] ),
		'TrendsBottom':pd.read_json( data['TrendsBottom'] ),
		'DebugOutput':{},
		}

	ss='import pandas as pd\nimport numpy as np \n\n'
	ss=ss+'from research.feature_exec import Rallylength'+'\n\n'
	ss=ss+str(code_str)
	ss=ss+'\n\n'+'#---'*30+'\n\n'

	with open( fname,'w') as featfile:
		featfile.write("%s" % ss)
	py_compile.compile(fname)

	import research.FeaturesCode_check as FCck
	import json
	

	# code=compile(code_str,'<string>','exec')
	# exec(code)
	x= eval('FCck.'+name+'(data)')
	return [  x, data['DebugOutput']  ]

def check_feature_code(testdata,code_str,name):
	from multiprocessing import Process, Queue, Pool
	import time

	for ss in ['__','import','builtin','write','os.','os ','sys.','sys ','write','open','close','with','system','set','get']:
		if ss in code_str:
			return (False,'Feature code cannot contain "'+ss+'"',None)

	if 'def '+name+'(data):' not in code_str:
		return (False,'Feature function code should have '+'def '+name+'(df):',None)

	if 'return' not in code_str:
		return (False,'Feature function code should return a value '+'def '+name+'(df):',None)

	errs=(ZeroDivisionError,NameError,IndentationError,TabError,SystemError,SystemExit,TypeError,UnboundLocalError,UnicodeError,EOFError)
	
	try:
		code=compile(code_str,'<string>','exec')
	except errs as e:
		return (False,e,None)
	# else:
	# 	return (False,'error in compile code',None)

	exec(code)

	qq = Queue()
	starttime=time.time()

	kpp = Pool(1)
	import sys
	try:
		res = kpp.apply_async(testmax,[testdata,] )
		kpp.close()
		x=res.get(timeout=2)
	except OSError as err:
		return (False, "OS error: {0}".format(err),None)
		print()
	except ValueError:
		return (False, "value error",None)
	except errs as e:
		return (False,e,None)
	except:
		return (False, "Unexpected error: "+str(sys.exc_info()[0]),None)

		

	print "time taken is "+str(time.time()-starttime)
	import json
	if type(x[0])==int or type(x[0])==float:
		return (True, 'Feature Computed' , json.dumps(x,indent=4) )
	else:
		return (False, 'Feature function should return float or int',None)
	# except:
	# 	return (False,'error in running code',None)


def process_feature_code(data,code_str,name):
	import research.FeaturesCode as FC
	
	# code=compile(code_str,'<string>','exec')
	# exec(code)
	x= eval('FC.'+name+'(data)')
	if np.isnan(x)==True:
		x=None
	return x




