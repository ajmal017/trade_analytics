# -*- coding: utf-8 -*-
"""
Created on Mon Jun 15 17:29:31 2015

@author: nagnanamus

Maintain All the tables
"""

import os.path
import CTA.GenConfig as GC
import pandas as pd
import numpy as np
import os
from os import listdir
from os.path import isfile, join
import subprocess as sbp
import time 
import sys



def ReIndexAndOptimizeTables_HDF5(tablink,tabname=None,limitto=None,mv2new='No',datacols=[],index2datetime=False):
    if tabname==None:
        onlyfiles = [ f for f in listdir(tablink) if isfile(join(tablink,f)) and '.h5' in f ]
    elif isinstance(tabname, list)==False:
        onlyfiles = [tabname]
    
    if limitto==None:
        pass
    else:
        onlyfiles=[f for f in onlyfiles if limitto in f]
        
    ik=1    
    for ff in onlyfiles:
        print([ik,len(onlyfiles)])
        ik=ik+1
        store=pd.HDFStore(join(tablink,ff))
        tempstore=pd.HDFStore(join(tablink,'temp_'+ff))

        if type(datacols)==str:
            datacols=[datacols]     
        
        strkeys=store.keys()
        for ss in strkeys:
            print(ss)
            ss=ss[1:]
            try:
                reader = pd.read_hdf(join(tablink,ff),ss, chunksize=100000)
            except:
                reader=[store[ss]]
            ind=0
            k=0
            for chunk in reader:
                k=k+1            
                print(k)
                
                # change index to datetime if needed
                if index2datetime==False:
                    chunk.index=range(ind,ind+len(chunk))
                else:
                    chunk.index=pd.to_datetime(chunk.index)
                    
                # apply the column dtypes if needed    
                chunk,minitmsz=CleanUpDataFrame(chunk)
                    
                if len(datacols)==0:
                    dc=True
                else:
                    dc=datacols
                #newdict = {key:min_itemsizes[key] for key in min_itemsizes.keys() if key in list(chunk.columns)}    
                tempstore.append(ss,chunk,data_columns = dc,index=False,format='table',min_itemsize=minitmsz)
                ind=ind+len(chunk)
                
        # creating an index now 
        for ss in strkeys:        
            tempstore.create_table_index(ss, optlevel=9, kind='full')
        
        store.close()
        tempstore.close()
        
        ot=-1
        
        orgfl=join(tablink,'temp_'+ff)
        tpfl=join(tablink,'temp2_'+ff)
        print('packing file '+orgfl)
        ot=sbp.call(["/home/nagnanamus/anaconda3/bin/ptrepack","--chunkshape=auto","--propindexes","--complevel=9","--complib=blosc",orgfl,tpfl],stderr=sbp.STDOUT)
        time.sleep(1)
        if ot==0:
            sbp.call(["rm",orgfl],stderr=sbp.STDOUT)
            time.sleep(1)
            sbp.call(["mv",tpfl,orgfl],stderr=sbp.STDOUT)
            time.sleep(1)
            
            if mv2new.lower()=='Yes'.lower():
                sbp.call(["rm",join(tablink,ff)],stderr=sbp.STDOUT)
                time.sleep(1)
                sbp.call(["mv",join(tablink,'temp_'+ff),join(tablink,ff)],stderr=sbp.STDOUT)
                
        else:
            print('Could not pretpack the file so deleting the temp ptrepack file')
            if os.path.isfile(tpfl): 
                sbp.call(["rm",tpfl],stderr=sbp.STDOUT)




        
def BreakDown_ReIndex_Optimize_Tables_HDF5(tablink,tabname,mv2new='No',datacols=[]):
 
    if tabname=='':
        onlyfiles = [ f for f in listdir(tablink) if isfile(join(tablink,f)) and '.h5' in f ]
    else:
        onlyfiles = [tabname]
        
    for ff in onlyfiles:
        store=pd.HDFStore(join(tablink,ff))
        tempstore=pd.HDFStore(join(tablink,'temp_'+ff))
        
        if type(datacols)==str:
            datacols=[datacols]     
        
        
        for ss in store.keys():
            print(ss)
            ss=ss[1:]
            reader = pd.read_hdf(join(tablink,ff),ss, chunksize=100000)
            ind=0
            k=0
            leaf=1
            
            for chunk in reader:
                
                sl=ss+'/T'+str(leaf)+'T'
                k=k+1            
                print(k)
                chunk.index=range(ind,ind+len(chunk))
                if len(datacols)==0:
                    dc=True
                else:
                    dc=datacols
                
                chunk,minitmsz=CleanUpDataFrame(chunk)
                tempstore.append(sl,chunk,data_columns = dc,index=False,format='table',min_itemsize=minitmsz)
                ind=ind+len(chunk)
                if np.remainder(ind,1000000)==0:
                    leaf=leaf+1
                    tempstore.create_table_index(sl, optlevel=9, kind='full')
                    
          
        tempstore.close()
        
        ot=-1
        
        orgfl=join(tablink,'temp_'+ff)
        tpfl=join(tablink,'temp2_'+ff)
        print('packing file '+orgfl)
        ot=sbp.call(["ptrepack","--chunkshape=auto","--propindexes","--complevel=9","--complib=blosc",orgfl,tpfl],stderr=sbp.STDOUT)
        time.sleep(1)
        if ot==0:
            sbp.call(["rm",orgfl],stderr=sbp.STDOUT)
            time.sleep(1)
            sbp.call(["mv",tpfl,orgfl],stderr=sbp.STDOUT)
            time.sleep(1)            
            if mv2new.lower()=='Yes'.lower():
                sbp.call(["rm",join(tablink,ff)],stderr=sbp.STDOUT)
                time.sleep(1)
                sbp.call(["mv",join(tablink,'temp_'+ff),join(tablink,ff)],stderr=sbp.STDOUT)
        else:
            print('Could not pretpack the file so deleting the temp one')
            if os.path.isfile(tpfl): 
                sbp.call(["rm",tpfl],stderr=sbp.STDOUT)
    
    
#%% Concatenate to existing table or else crweate a new table :

def ConcatDataFrame2Table_windows(HDFtablink,HDFtabname,HDFleaftag,DF,opt=0,pc=0,RoOptmize=False):
    
    for ss in np.array(windows_std):
        dd=DF[DF['window']==ss]
        if dd.empty:
            continue
        leafname=HDFleaftag+str(ss)
        ConcatDataFrame2Table_recursive(HDFtablink,HDFtabname,leafname,dd,opt=opt,pc=pc,data_columns = True,RoOptmize=RoOptmize)

#recursively add it to the leaf of the table 
# create a new temp file with all the columns, add the data to it
# delete the original, copy temp to original leafname
# opt is for side ways concat
def ConcatDataFrame2Table_recursive(tablink,tabname,leafname,dd,opt=0,pc=0,data_columns = True,RoOptmize=False):
    
    if os.path.isfile(join(tablink,tabname))==False:
        dd,ffminsize=CleanUpDataFrame(dd)
        dd.to_hdf(join(tablink,tabname),leafname,format='table')
        if RoOptmize==True:
            ReIndexAndOptimizeTables_HDF5(tablink,tabname,mv2new='Yes') 
        return
    if os.path.isfile(join(tablink,tabname))==True:
        store=pd.HDFStore(join(tablink,tabname))                
        if leafname not in store.keys():
            dd,ffminsize=CleanUpDataFrame(dd)
            dd.to_hdf(join(tablink,tabname),leafname,format='table')
            store.close()
            if RoOptmize==True:
                ReIndexAndOptimizeTables_HDF5(tablink,tabname,mv2new='Yes')             
            return
        else:
            store.close()
            
            
    store_temp=pd.HDFStore(join(tablink,'temp_'+tabname))
    reader = pd.read_hdf(join(tablink,tabname),leafname, chunksize=100000)
    dd,ddminsize=CleanUpDataFrame(dd)
    for chunk in reader:        
        chunk=SidewaysConcatDataFrames_smart(chunk,dd,tabname,opt,pc=pc)
        chunk,ffminsize=CleanUpDataFrame(chunk)
        store_temp.append(leafname,chunk,data_columns = True,index=False,format='table',min_itemsize=ffminsize)
        
    store_temp.close()
    sbp.call(["rm",join(tablink,tabname)],stderr=sbp.STDOUT)
    time.sleep(1)
    sbp.call(["mv",join(tablink,'temp_'+tabname),join(tablink,tabname)],stderr=sbp.STDOUT)
    
    if RoOptmize==True:
        ReIndexAndOptimizeTables_HDF5(tablink,tabname,mv2new='Yes')       


    
    
    
#TODO: Verify this    
 
#extra columns are the non-clashing columns only   
# real side ways concat and remain lengthwise concat: manage the duplicates also    

    
def SidewaysConcatDataFrames_smart(MF,df,tabname,opt,pc=0,reindix=True):
    if MF.empty:
        return df
    if len(MF.columns)==0 and len(MF.index)>0:
        return df.loc[MF.index]
    if len(MF.index)==0:
        return df
        
    if opt==0: # 'Just append below,remove duplicate entries (index), ignore the extra columns' MF cols remains the smae
        MF=pd.concat([MF,df[ list(set(MF.columns) & set(df.columns)) ] ])
        MF=Append_IndexCol(MF,tabname)
        MF.drop_duplicates(subset=['IndexCol'],inplace=True)
        MF.drop('IndexCol', axis=1, inplace=True)   

    elif opt==0.5: # 'Just append below,remove duplicate entries (index)
        MF=pd.concat([MF,df])
        MF=Append_IndexCol(MF,tabname)
        MF.drop_duplicates(subset=['IndexCol'],inplace=True)
        MF.drop('IndexCol', axis=1, inplace=True)   
        
    elif opt==1: # 'Side concat if index same, add remaining indicies at bottom, keep the extra columns'
        MF=Append_IndexCol(MF,tabname)
        df=Append_IndexCol(df,tabname)
        
        MF['PrevIndex']=MF.index
        df['PrevIndex']=df.index
        
        MF.index=MF['IndexCol']
        df.index=df['IndexCol']

        MF=pd.concat([MF,df[ list(set(df.columns) - set(MF.columns)) ] ],axis=1,join_axes=[MF.index])
        NonComInd=list( set(df.index)-set(MF.index) )
        
        MF=pd.concat([MF,df.loc[NonComInd]])
        if reindix==True:
            MF.index=MF['PrevIndex']
        else:
            MF.index=range(0,len(MF))
            
        MF.drop('IndexCol', axis=1, inplace=True)   
        MF.drop('PrevIndex', axis=1, inplace=True)   
        
    elif opt==2: # 'Side concat if index same, ignore remaining indicies i.e.....dont append remaining indicies
        MF=Append_IndexCol(MF,tabname)
        df=Append_IndexCol(df,tabname)
        
        MF['PrevIndex']=MF.index
        df['PrevIndex']=df.index
        
        MF.index=MF['IndexCol']
        df.index=df['IndexCol']
        

        MF=pd.concat([MF,df[ list(set(df.columns) - set(MF.columns)) ] ],axis=1,join_axes=[MF.index])
        NonComInd=list( set(df.index)-set(MF.index) )
        
        if reindix==True:
            MF.index=MF['PrevIndex']
        else:
            MF.index=range(0,len(MF))
            
        MF.drop('IndexCol', axis=1, inplace=True)   
        MF.drop('PrevIndex', axis=1, inplace=True)   
       
    else:
        sys.exit('Error with concat error')
        
        
    
    return MF
        
def SidewaysConcatDataFrames_customindex(MF,df,Indexcols,opt,pc=0,reindix=True):
    if len(MF.columns)==0 and len(MF.index)>0:
        return df.loc[MF.index]
    if len(MF.index)==0:
        return df
        
    if opt==0: # 'Just append below,remove duplicate entries (index), ignore the extra columns' MF cols remains the smae
        MF=pd.concat([MF,df[ list(set(MF.columns) & set(df.columns)) ] ])
        MF=Append_IndexCol_custom(MF,Indexcols)
        MF.drop_duplicates(subset=['IndexCol'],inplace=True)
        MF.drop('IndexCol', axis=1, inplace=True)   
        
    elif opt==1: # 'Side concat if index same, add remaining indicies at bottom, keep the extra columns'
        MF=Append_IndexCol_custom(MF,Indexcols)
        df=Append_IndexCol_custom(df,Indexcols)
        
        MF['PrevIndex']=MF.index
        df['PrevIndex']=df.index
        
        MF.index=MF['IndexCol']
        df.index=df['IndexCol']

        MF=pd.concat([MF,df[ list(set(df.columns) - set(MF.columns)) ] ],axis=1,join_axes=[MF.index])
        NonComInd=list( set(df.index)-set(MF.index) )
        
        MF=pd.concat([MF,df.loc[NonComInd]])
        if reindix==True:
            MF.index=MF['PrevIndex']
        else:
            MF.index=range(0,len(MF))
            
        MF.drop('IndexCol', axis=1, inplace=True)   
        MF.drop('PrevIndex', axis=1, inplace=True)   
        
    elif opt==2: # 'Side concat if index same, ignore remaining indicies,dont append remaining indicies
        MF=Append_IndexCol_custom(MF,Indexcols)
        df=Append_IndexCol_custom(df,Indexcols)
        
        MF['PrevIndex']=MF.index
        df['PrevIndex']=df.index
        
        MF.index=MF['IndexCol']
        df.index=df['IndexCol']
        

        MF=pd.concat([MF,df[ list(set(df.columns) - set(MF.columns)) ] ],axis=1,join_axes=[MF.index])
        NonComInd=list( set(df.index)-set(MF.index) )
        
        if reindix==True:
            MF.index=MF['PrevIndex']
        else:
            MF.index=range(0,len(MF))
            
        MF.drop('IndexCol', axis=1, inplace=True)   
        MF.drop('PrevIndex', axis=1, inplace=True)   
    


    else:
        sys.exit('Error with concat error')
        
        
    
    return MF        
        
        


#just rename the columns/leafnames of the table
def RenameColm_Leaf_Table_recursive(tablink,tabname,coldict='std',appdtype=False,leafdict={},index2datetime=False):
    store=pd.HDFStore(tablink,tabname)
    
    if len(leafdict)==0:
        leafs=store.keys()
        for ss in leafs:
            leafdict[ss]=ss            
    else:
        leafs=list( set(store.keys()) & set(leafdict.keys()) )
        leafdict2={}
        for ss in leafs:
            leafdict2[ss]=leafdict[ss]
        leafdict=leafdict2    
        
    for ss in leafs:    
        reader = pd.read_hdf(tablink,tabname,ss, chunksize=100000)
        ind=0
        for chunk in reader:
                        
            if index2datetime==False:
                chunk.index=range(ind,ind+len(chunk))
                ind=ind+len(chunk)
            else:
                chunk.index=pd.to_datetime(chunk.index)
                    
            # apply the column dtypes if needed    
            if appdtype==True:
                chunk=ApplyDtypes2DataFrame(chunk)
            # rename the columns if necessary
            if coldict=='std':
                chunk=chunk.rename(columns = ColumnRenamersDict)                    
            elif type(coldict)==dict:
                chunk=chunk.rename(columns = coldict)                    
            
            store.append(leafdict[ss]+'_temp',chunk,data_columns = True,index=False,format='table',min_itemsize=GetMinItemSizes(chunk))
            
        del store[leafdict[ss]] 
        
        reader = pd.read_hdf(tablink,tabname,leafdict[ss]+'_temp', chunksize=100000)
        for chunk in reader:
            store.append(leafdict[ss],chunk,data_columns = True,index=False,format='table',min_itemsize=GetMinItemSizes(chunk))
        
        del store[leafdict[ss]+'_temp'] 
        store.create_table_index(leafdict[ss], optlevel=9, kind='full')
    
    
               
            
def CleanUpDataFrame(dd):
      
    for ss in dd.columns:
        # apply d types
        if ss in GC.MasterColumnDict.keys():
            dd[ss]=dd[ss].astype(GC.MasterColumnDict[ss]['astype']   )
            
    for sp in GC.ColumnRenamersDict.keys():
        pp=GC.ColumnRenamersDict[sp]            
        if pp in dd.columns:
            if sp in GC.MasterColumnDict.keys():
                dd[pp]=dd[pp].astype(GC.MasterColumnDict[sp]['astype']   )
                
    # renaming the columns to the regular good names
    for ss in dd.columns:
        if ss in GC.ColumnRenamersDict.keys():
            dd.rename(columns = {ss:GC.ColumnRenamersDict[ss]},inplace=True)
    
    min_itemdict={};  
    for ss in dd.columns:        
    # get min column sizes    
        if ss in GC.min_itemsizes.keys():
            min_itemdict[ss]=GC.min_itemsizes[ss]
            
    return dd,min_itemdict   

def Append_IndexCol(dd,tabname=None):
    if tabname==None:
        dd['IndexCol']=dd.index
        return dd
        
    ddcol=dd.columns
    # Pattern Correlation and Tubes dataframe index tag
    if 'common'.lower() in tabname.lower():
        if len(set(ddcol).intersection(set(Common_table_tags)))==len(Common_table_tags):
            dd['IndexCol']=['']*len(dd)
            for ss in Common_table_tags:
                if 'date' in ss.lower():
                    dd['IndexCol']=dd['IndexCol']+dd[ss].apply(lambda x: x.strftime("%Y-%m-%d"))
                else:
                    dd['IndexCol']=dd['IndexCol']+dd[ss].astype(str)
        else:
             sys.exit("No index cols available for Common_table_tags")
             
    # Stock pair Correlation dataframe index tag
    if PathDict['CorrelationData_tabname'] in tabname:            
        if len(set(ddcol).intersection(set(CORR_table_tags)))==len(CORR_table_tags):
            dd['IndexCol']=['']*len(dd)
            for ss in CORR_table_tags:
                if 'date' in ss.lower():
                    dd['IndexCol']=dd['IndexCol']+dd[ss].apply(lambda x: x.strftime("%Y-%m-%d"))
                elif 'stock'.lower() not in ss.lower():
                    dd['IndexCol']=dd['IndexCol']+dd[ss].astype(str)
                
            dd['IndexCol']=dd['IndexCol']+dd[['Stock1','Stock2']].apply(lambda row: "".join(sorted([ row['Stock1'], row['Stock2'] ]) ) , axis=1)
                
        else:
             sys.exit("No index cols available for CorrelationData_tabname")
                
             
    return dd         

def Append_IndexCol_custom(dd,Indexcols):
    ddcol=dd.columns

    if len(set(ddcol).intersection(set(Indexcols)))==len(Indexcols):
        dd['IndexCol']=['']*len(dd)
        for ss in Indexcols:
            if 'date' in ss.lower():
                dd['IndexCol']=dd['IndexCol']+dd[ss].apply(lambda x: x.strftime("%Y-%m-%d"))
            else:
                dd['IndexCol']=dd['IndexCol']+dd[ss].astype(str) 
    else:
        sys.exit("No index cols not there in this frame")

    return dd



#def ApplyDtypes2MYSQL():
