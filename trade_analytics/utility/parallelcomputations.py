import multiprocessing as mp
from Queue import Empty
import time
import pdb

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
            Q.put((compute_list,) )
        time.sleep(0.1)

        func=Q2list(self.func,Q)
        P=[]
        for i in range(Ncores-1):
            P.append( mp.Process(target=func,args=(),kwargs={'lock':lock}) ) 

        for p in P:
            p.start()
            time.sleep(1)

        for p in P:
            p.join()
            time.sleep(1)

        print "Submitted / Done jobs on ",Ncores, " with #consumer ",Ncores-1
