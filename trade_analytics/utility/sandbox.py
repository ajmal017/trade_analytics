import multiprocessing as mp
import time

class sandbox(object):
	"""
	run a function in a sandbox, limiting time and memory
	"""
	def __init__(self,codestr,callstr):
		self.codestr=codestr
		self.callstr=callstr
	def run(self):
		def func(codestr,callstr):	
			codeobj=compile(codestr,'dummy','exec')
			exec(codeobj)

			exec(codestr)
		p=mp.Process(target=func,args=(self.codestr,self.callstr))
		p.start()

		time.sleep(2)

		if p.is_alive():
			p.terminate()
			p.join(2)
			self.error ="Terminated : takes more than 2 seconds"