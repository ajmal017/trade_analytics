import time
import functools
import logging
import pandas as pd
import sys,traceback

def replaceNaN2None(x):
	if type(x)==list:
		for i in range(len(x)):
			x[i]=replaceNaN2None(x[i])

		return x
	elif type(x)==tuple:
		a=[]
		for i in range(len(x)):
			a.append(replaceNaN2None(x[i]))
		x=tuple(a)
		return x

	elif type(x)==dict:
		for k,v in x.items():
			x[k]=replaceNaN2None(v)
		return x
	else:
		if pd.isnull(x):
			return None	
		else:
			return x


class logperf(object):
	def __init__(self,modulename,appendmsg='',printit=True):
		self.logger=logging.getLogger(modulename)
		self.printit=printit
		self.appendmsg=appendmsg

	def __call__(self,func):
		@functools.wraps(func)
		def wrappedfunc(*args,**kwargs):
			starttime=time.clock()
			c=func(*args,**kwargs)
			t=time.clock()-starttime
			msg="TIMING : "+func.__name__+" time = "+str(t)+" on "+time.strftime("%Y-%m-%d %I:%M:%S")+" with args: (%s,%s)"%(str(args)[0:100],str(kwargs)[0:100])+" "+self.appendmsg 
			self.logger.info(msg)
			if self.printit:
				print msg
			return c 

		return wrappedfunc



class logexception(object):
	def __init__(self,modulename,returnONerror=None,appendmsg='',printit=True):
		self.logger=logging.getLogger(modulename)
		self.printit=printit
		self.appendmsg=appendmsg
		self.returnONerror=returnONerror

	def __call__(self,func):
		@functools.wraps(func)
		def wrappedfunc(*args,**kwargs):
			try:
				c=func(*args,**kwargs)
				return c
			except Exception as ex:
				exc_type, exc_value, exc_traceback = sys.exc_info()
				traceback.print_tb(exc_traceback, limit=1, file=sys.stdout)
				traceback.print_exception(exc_type, exc_value, exc_traceback,limit=2, file=sys.stdout)
				traceback.print_exc()
				formatted_lines = traceback.format_exc().splitlines()
				print formatted_lines[0]
				print formatted_lines[-1]
				print "*** format_exception:"
				print repr(traceback.format_exception(exc_type, exc_value,
													  exc_traceback))
				print "*** extract_tb:"
				print repr(traceback.extract_tb(exc_traceback))
				print "*** format_tb:"
				print repr(traceback.format_tb(exc_traceback))
				print "*** tb_lineno:", exc_traceback.tb_lineno

				msg="EXCEPTION : "+func.__name__+" on "+time.strftime("%Y-%m-%d %I:%M:%S")+" with args: (%s,%s)"%(str(args)[0:100],str(kwargs)[0:100])+" "+self.appendmsg +" "+ex.__name__+" "+str(ex)
				self.logger.error(msg)
				self.logger.exception(msg)
				if self.printit:
					print msg
				return self.returnONerror

			
		return wrappedfunc