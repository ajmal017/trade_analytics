from __future__ import division
# import stockapp.models as stkmd
# import dataapp.models as dtamd
import dataapp.libs as dtalibs
# import pandas as pd
from featureapp.libs import registerfeature, featuremodel
# import os
filename=__name__.split('.')[-1]





# --------------  features has to be the name of the class ------------------
# Define your features in this class

class features(featuremodel):

    @registerfeature(filename=filename,category='Price',returntype=float,query=True,operators=['<','>','<=','>=','inrange','!=','!inrange'],null=False,cache=True)
    def SMA20(self,T):
        """
        sma10
        """
        return 32
    
    



# --------- This is required to sync the features to the database -------------
features.finalize(filename)