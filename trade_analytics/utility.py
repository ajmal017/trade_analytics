import multiprocessing as mp
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

    def parallelrun(self):

        if self.method=='celery':
            for compute_list in self.paralist:
                self.func.delay(*compute_list)
        else:
            P=[]
            lock=mp.Lock()
            for compute_list in self.paralist:
                # print "compute_list = ", tuple(compute_list)
                # if type(compute_list)==tuple:

                P.append( mp.Process(target=self.func,args=compute_list,kwargs={'lock':lock}) ) 

            for p in P:
                p.start()
                time.sleep(1)
                # time.sleep(1)

            for p in P:
                p.join()
                time.sleep(1)

        print "Submitted / Done jobs"