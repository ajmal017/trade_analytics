# -*- coding: utf-8 -*-
"""
Created on Wed Jan 14 01:11:54 2015
Custom Clustering Code + Machine Learning + Optimization
@author: nagnanamus
"""
import numpy as np
from sklearn import cluster

import sys
if sys.platform not in ['win32','win64']:
    import cvxopt as cvxopt
    import cvxpy as cvx

import scipy as scipy


# Some test cases
D1=np.array([-5,1,2,3,6,7,8,9,15])
D2=np.array([1,2, 4,5, 8,9, 12,13,14,15])



# Algo 1 for clustering 1D consequtive data. This is  a simple iterative
# program that cluster the data to the nearest group. new groups are created 
# when pts are separated with distances grater the the mean separation.

# Input  : is T is numpy array
# Output : is cluster groups that are also numpy arrays arranged in a list
#           consecutively
# parameters : ClstStr is the strength of the distance grouping i.e. if 2 
#              elements are within mean(diff)*ClstStr then they are 
#              grouped together
                
#              Groups smaller that MinGrpSize are eliminated
                
def ConsecutiveClustering_1Ddata_algo1(T,MinGrpSize=3,ClstStr=2):
    diff=np.abs(np.diff(T))
    md=np.mean(diff)*ClstStr
    grps=[[T[0]]]
    for i in range(1,len(T)-1):
        if np.abs(T[i]-T[i-1])<=np.abs(T[i]-T[i+1]):
            if np.abs(T[i]-T[i-1]) >= md:
                grps.append([T[i]])
            else:
                grps[-1].append(T[i])    
        
        if np.abs(T[i]-T[i-1]) > np.abs(T[i]-T[i+1]):
            grps.append([T[i]])
    
    hh=len(T)-1       
    if np.abs(T[hh]-T[hh-1])<=md:
        grps[-1].append(T[hh])
    else:
        grps.append([T[hh]])   
     
    Gp=[]
    for g in grps:
        if len(g)>3:
            Gp.append(g)
             
    return Gp
    
    
    
    
# Algo 2 for clustering 1D consequtive data. This is  a simple iterative
# program that cluster the data to the nearest group. new groups are created 
# 2 at a trime by considering the max separation distance within each group

# Input  : is T is numpy array
# Output : is cluster groups that are also numpy arrays arranged in a list
#           consecutively
# parameters : ClstStr is the strength of the distance grouping i.e. if 2 
#              elements are within mean(diff)*ClstStr then they are 
#              grouped together
                
#              Groups smaller that MinGrpSize are eliminated
                
def ConsecutiveClustering_1Ddata_algo2(T,MinGrpSize=3,ClstStr=2):
    diff=np.abs(np.diff(T))
    md=np.mean(diff)*ClstStr
    grps=[T]
    while 1:
        for i in range(0,len(grps)):
            t=grps[i]
            diff=np.abs(np.diff(t))
            
        s=np.argmax(np.abs(diff))
        grps.append(T[0:s])
        grps.append(T[s:])        


# input M is numpy array column vector
# output is cluters and their labels
# You can specify the number of cluster you want,
# or let the algorithm decide the number of clusters
def KmeansClustering_1Ddata_algo1(M,NClust='optimal',MinGrpSize=5):
    if NClust!='optimal':
        ss=cluster.KMeans(n_clusters=NClust).fit(M)
        return [ss.cluster_centers_, ss.labels_]
    
    opt_slopes=-1
    for i in range(1,30):
        #print i
        ss=cluster.KMeans(n_clusters=i).fit(M)
        #ss.cluster_centers_
        for j in range(1,i):
            #print [j,ss.labels_[ss.labels_==j].size]
            if ss.labels_[ss.labels_==j].size<=MinGrpSize:
                opt_slopes=i-1
                #print opt_slopes 
                break
        if opt_slopes>0:
            break
    
   
    ss=cluster.KMeans(n_clusters=opt_slopes).fit(M)
    return [ss.cluster_centers_, ss.labels_]

def OptLineFit_cvx(y,t,bias,vlambdaBias,weights):

    
    n = y.size
    
    x = cvx.Variable(2)
    if bias=='bottom':
        obj = cvx.Minimize(0.5 * cvx.sum_squares(cvx.mul_elemwise(weights,y - x[1]*t-x[2])
                       + vlambdaBias*cvx.sum_entries(cvx.max_elemwise(x[1]*t+x[2]-y,0)) ) )
    elif bias=='top':
        obj = cvx.Minimize(0.5 * cvx.sum_squares(cvx.mul_elemwise(weights,y - x[1]*t-x[2])
                       + vlambdaBias*cvx.sum_entries(cvx.max_elemwise(y-x[1]*t-x[2],0)) ) )
    else:
        sys.exit('error no option top or bottom ?')

        
    prob = cvx.Problem(obj)
    # ECOS and SCS solvers fail to converge before
    # the iteration limit. Use CVXOPT instead.
    prob.solve(solver=cvx.CVXOPT,verbose=False)

    #print 'Solver status: ', prob.status
    # Check for error.
    if prob.status != cvx.OPTIMAL:
        raise Exception("Solver did not converge!")  
        
    return np.array(x.value)

# input is the numpy array y
def OptTrendFit_cvx(y,vlambda,weights):

    
    n = y.size
    # Form second difference matrix.
    e = np.mat(np.ones((1, n)))
    D = scipy.sparse.spdiags(np.vstack((e, -2*e, e)), range(3), n-2, n)
    # Convert D to cvxopt sparse format, due to bug in scipy which prevents
    # overloading neccessary for CVXPY. Use COOrdinate format as intermediate.
    # D_coo = D.tocoo()
    # D = cvxopt.spmatrix(D_coo.data, D_coo.row.tolist(), D_coo.col.tolist())

    # Set regularization parameter.

    # Solve l1 trend filtering problem.
    x = cvx.Variable(n)
    obj = cvx.Minimize(0.5 * cvx.sum_squares(cvx.mul_elemwise(weights,y - x))
                       + vlambda * cvx.norm(D*x, 1) )
    prob = cvx.Problem(obj)
    # ECOS and SCS solvers fail to converge before
    # the iteration limit. Use CVXOPT instead.
    prob.solve(solver=cvx.CVXOPT,verbose=False)

    #print 'Solver status: ', prob.status
    # Check for error.
    if prob.status != cvx.OPTIMAL:
        raise Exception("Solver did not converge!")  
        
    return np.array(x.value)


# This optimization places a cost thatmost oof thepoints are above the trend line    
# input is the numpy array y
# vlambdaBias is the penalty of allowing the points to be on the other side of the trend lien
def OptBottomTrendFit_cvx(y,vlambda,vlambdaBias,weights):
    n = y.size
    # Form second difference matrix.
    e = np.mat(np.ones((1, n)))
    D = scipy.sparse.spdiags(np.vstack((e, -2*e, e)), range(3), n-2, n)
    # Convert D to cvxopt sparse format, due to bug in scipy which prevents
    # overloading neccessary for CVXPY. Use COOrdinate format as intermediate.
    # D_coo = D.tocoo()
    # D = cvxopt.spmatrix(D_coo.data, D_coo.row.tolist(), D_coo.col.tolist())
    cvx.sum_entries
    # Set regularization parameter.

    # Solve l1 trend filtering problem.
    x = cvx.Variable(n)
    obj = cvx.Minimize(0.5 * cvx.sum_squares(cvx.mul_elemwise(weights,y - x))+ vlambdaBias*cvx.sum_entries(cvx.max_elemwise(x-y,0))
                       + vlambda * cvx.norm(D*x, 1) )
    prob = cvx.Problem(obj)
    # ECOS and SCS solvers fail to converge before
    # the iteration limit. Use CVXOPT instead.
    prob.solve(solver=cvx.CVXOPT,verbose=False)

    #print 'Solver status: ', prob.status
    # Check for error.
    if prob.status != cvx.OPTIMAL:
        raise Exception("Solver did not converge!")  
        
    return np.array(x.value)    
    
    
# This optimization places a cost thatmost oof thepoints are above the trend line    
# input is the numpy array y
# vlambdaBias is the penalty of allowing the points to be on the other side of the trend lien
def OptTopTrendFit_cvx(y,vlambda,vlambdaBias,weights):

    n = y.size
    # Form second difference matrix.
    e = np.mat(np.ones((1, n)))
    D = scipy.sparse.spdiags(np.vstack((e, -2*e, e)), range(3), n-2, n)
    # Convert D to cvxopt sparse format, due to bug in scipy which prevents
    # overloading neccessary for CVXPY. Use COOrdinate format as intermediate.
    # D_coo = D.tocoo()
    # D = cvxopt.spmatrix(D_coo.data, D_coo.row.tolist(), D_coo.col.tolist())
    cvx.sum_entries
    # Set regularization parameter.

    # Solve l1 trend filtering problem.
    x = cvx.Variable(n)
    obj = cvx.Minimize(0.5 * cvx.sum_squares(cvx.mul_elemwise(weights,y - x))+ vlambdaBias*cvx.sum_entries(cvx.max_elemwise(y-x,0))
                       + vlambda * cvx.norm(D*x, 1) )
    prob = cvx.Problem(obj)
    # ECOS and SCS solvers fail to converge before
    # the iteration limit. Use CVXOPT instead.
    prob.solve(solver=cvx.CVXOPT,verbose=False)

    #print 'Solver status: ', prob.status
    # Check for error.
    if prob.status != cvx.OPTIMAL:
        raise Exception("Solver did not converge!")  
        
    return np.array(x.value)        