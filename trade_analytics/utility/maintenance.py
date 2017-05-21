import time
import functools
import logging
import pandas as pd

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
			msg="TIMING : "+func.__name__+str(t)+" on "+time.strftime("%Y-%m-%d %I:%M:%S")+" with args: (%s,%s)"%(args,kwargs)+" "+self.appendmsg 
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
				msg="EXCEPTION : "+func.__name__+" on "+time.strftime("%Y-%m-%d %I:%M:%S")+" with args: (%s,%s)"%(args,kwargs)+" "+self.appendmsg +" "+ex.__name__+" "+str(ex)
				self.logger.error(msg)
				self.logger.exception(msg)
				if self.printit:
					print msg
				return self.returnONerror

			
		return wrappedfunc