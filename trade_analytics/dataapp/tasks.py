from __future__ import division


import stockapp.models as stkmd
import dataapp.datadownloadmanager as dtadwnmang
import computeapp.models as cmpmd


# import pandas as pd
# import dataapp.models as dtamd
# import utility.parallelcomputations as utpc
# import itertools as itt
# import dataapp.libs as dtalibs
# make the function shared
# from django.conf import settings
from django_rq import job as shared_task


@shared_task
def UpdatePriceData(Symbols_id, compute_session_id):
    stk = stkmd.Stockmeta.objects.get(id=Symbols_id)
    compute_status_obj = cmpmd.ComputeStatus.make_newcompute(
        compute_session_id)
    ddm = dtadwnmang.DataDownloadManager(stk, compute_status_obj)
    ddm.update_data()
