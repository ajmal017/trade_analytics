import multiprocessing as mp
from Queue import Empty
import time
import pickle as pkl
import zlib
import pdb
import copy
import Queue




def get_celery_worker_status():
    ERROR_KEY = "ERROR"
    try:
        from celery.task.control import inspect
        insp = inspect()
        d = insp.stats()
        if not d:
            d = { ERROR_KEY: 'No running Celery workers were found.' }
    except IOError as e:
        from errno import errorcode
        msg = "Error connecting to the backend: " + str(e)
        if len(e.args) > 0 and errorcode.get(e.args[0]) == 'ECONNREFUSED':
            msg += ' Check that the RabbitMQ server is running.'
        d = { ERROR_KEY: msg }
    except ImportError as e:
        d = { ERROR_KEY: str(e)}
    return d
    

def chunks(L,N):
    for i in range(0,len(L),N):
        yield L[i:i+N]

def Q2list(func,Q,*args,**kwargs):
    def wrapfunc(*args,**kwargs):
        while(not Q.empty()):
            try:
                q=Q.get_nowait()
                time.sleep(0.1)
            except Empty:
                print "queue is empty"
                continue
            if type(q)==list or type(q)==tuple:
                pass
            else:    
                q=list(q)
            
            func(q,*args,**kwargs)
    return wrapfunc


class ParallelCompute(object):
    """ 
    - Still have to make it fail safe
    - Provision to look at success/fails
    - Provision to block/nonblock
    - Provisions to chunk list
    - Provision for queue -> producer/consuer
    - Provision for locks,queues
    - Provision for exception free
    - Provisions for dynamic and static arguments to functions
     

    """
    def __init__(self,paralist,func):
        self.func=func
        self.paralist=paralist

        celery_status=get_celery_worker_status()
        if celery_status==True and hasattr(func,'delay')==True:
            self.method='celery'
        else:
            self.method='Process'

    def SingleRun(self):
        for compute_list in chunks(self.paralist,1):
            self.func(compute_list,) 

        print "Done Single Core"

    def ParallelRun(self,chunkby=100,Semaphore=True,Lock=True):

        if self.method=='celery':
            for compute_list in self.paralist:
                self.func.delay(*compute_list)
        else:
            P=[]
            Ncores=mp.cpu_count()
            if Lock:
                lock=mp.Lock()
            else:
                lock=None

            if Semaphore:
                semaphore = mp.Semaphore(Ncores-1)
            else:
                semaphore = None

            for compute_list in chunks(self.paralist,chunkby):
                # print "compute_list = ", tuple(compute_list)
                # if type(compute_list)==tuple:
                print lock,semaphore
                P.append( mp.Process(target=self.func,args=(compute_list,),kwargs={'semaphore':semaphore,'lock':lock}) ) 

            for p in P:
                p.start()
                time.sleep(1)
                # time.sleep(1)

            for p in P:
                p.join()
                time.sleep(1)

        print "Submitted / Done jobs on ",Ncores, " with semaphore on ",Ncores-1

    def ConsumerQueuerun(self,chunkby=100,Lock=True):
        Ncores=mp.cpu_count()
        if Lock:
            lock=mp.Lock()
        else:
            lock=None

        Q=mp.Queue()
        for compute_list in chunks(self.paralist,chunkby):
            Q.put(compute_list )
        time.sleep(0.1)

        func=Q2list(self.func,Q)
        P=[]
        for i in range(Ncores-1):
            P.append( mp.Process(target=func,args=(),kwargs={'lock':lock,'semaphore':None}) ) 

        for p in P:
            p.start()
            time.sleep(1)

        for p in P:
            p.join()
            time.sleep(1)

        print "Submitted / Done jobs on ",Ncores, " with #consumer ",Ncores-1



###################################################################################
####################  MULTIPROCESSING CONSUMER ####################################
###################################################################################


def MPadapter(func):
    def wrapper(inQ,outQ,quitevent,runevent,*args,**kwargs):
        i=0
        print "started ",mp.current_process()
        while(1):
            try:
                q=inQ.get_nowait()
                fargs=q.get('args',())+args
                fkwargs=copy.deepcopy(kwargs)
                fkwargs.update( q.get('kwargs',{}) )
                
                runevent.set()
                img=func(*fargs,**fkwargs)
                runevent.clear()

                outQ.put({'input':q,'output':img})
                time.sleep(0.1)
                i=i+1
            except Queue.Empty:
                time.sleep(0.5)

            if quitevent.is_set():
                print "event set"
                print "consumed tasks = ",i," on ",mp.current_process()
                break
    return wrapper


class MPconsumer(object):
    def __init__(self,N,func,usecache=True,constarg=(),constkwarg={}):
        self.usecache=usecache
        self.inQ=mp.Queue()
        self.outQ=mp.Queue()
        self.event=mp.Event()
        self.event.clear()
        self.in_counter=0
        self.out_counter=0
        
        self.resultscache={} # input:ouput
        self.resultsorder={} # counter: input
        
        
        self.P=[]
        self.RunFlags=[]

        func=MPadapter(func)
        
        for i in range(N):
            runevent=mp.Event()
            self.P.append( mp.Process(target=func,args=(self.inQ,self.outQ,self.event,runevent),kwargs=constkwarg) )
            self.RunFlags.append(runevent)

    def append2Q(self,q):
        if type(q)!=dict:
            print "please put your arguments in a dict"
            return False
#         if self.skipdone:
#             print "result already exists use cache to retrive results"
        
        if self.usecache:
            qpkl=pkl.dumps(q)
            if qpkl in self.resultscache:
                print "reusing cached result"
                q['counter']=self.in_counter
                self.in_counter=self.in_counter+1
                self.outQ.put({'input':q,'output':self.resultscache[qpkl]})
                time.sleep(0.1)
                return True
        
        q['counter']=self.in_counter
        self.in_counter=self.in_counter+1
        self.inQ.put(q)
        time.sleep(0.1)
        return True
    
    def readresultcache(self):
        cnt=self.out_counter
        self.out_counter=self.out_counter+1
        result= self.resultscache[ self.resultsorder[cnt] ]
        return result
    
    def getQ(self):
        q=None
        while True:
            try:
                q=self.outQ.get_nowait()
                cnt=q['input']['counter']
                del q['input']['counter']
                if self.usecache:
                    qpkl=pkl.dumps(q['input'])
                    self.resultscache[qpkl]=q['output']
                    self.resultsorder[cnt]=qpkl
                    if self.out_counter in self.resultsorder:
                        result= self.readresultcache()
                        break
                        
                else:
                    self.out_counter=self.out_counter+1
                    result=q['output']
                    break
                    
            except Queue.Empty:
                if self.usecache:
                    if self.out_counter in self.resultsorder:
                        result= self.readresultcache()
                        break
                 
            time.sleep(0.5)
                    
        return result
    
    def updatecache(self):
        while True:
            try:
                q=self.outQ.get_nowait()
                cnt=q['input']['counter']
                del q['input']['counter']
                qpkl=pkl.dumps(q['input'])
                self.resultscache[qpkl]=q['output']
                self.resultsorder[cnt]=qpkl
                    
            except Queue.Empty:
                break
                 
            time.sleep(0.5)
                    
    def getresult(self,arg):
        qpkl=pkl.dumps(arg)
        while qpkl not in self.resultscache:
            self.updatecache()
            time.sleep(0.5)

        return self.resultscache[qpkl]

    def clearQs(self):
        while True:
            try:
                self.inQ.get_nowait()
            except Queue.Empty:
                break
            
            time.sleep(0.1)
            
        while True:
            try:
                self.outQ.get_nowait()
            except Queue.Empty:
                stillrunning=False
                for ev in self.RunFlags:
                    if ev.is_set():
                        stillrunning=True
                if stillrunning==False:
                    break

            time.sleep(0.2)


                
                
    def start(self):
        for p in self.P:
            p.start()
        print "consumers started"
        
    def stop(self):
        self.event.set()
        for p in self.P:
            p.join()
            time.sleep(0.2)
        print "consumers closed"    