import pandas as pd
import numpy as np
import scipy as sc
import json
import multiprocessing as mp


# store=pd.HDFStore('data.h5')


with open('Symbol.json','r') as F:
	Symbols=json.load(F)
N=len(Symbols)

def getall(i):
	T0=pd.datetime(2018,1,1).date()
	Tf=pd.datetime(2018,3,9).date()

	with open('Symbol.json','r') as F:
		Symbols=json.load(F)

	N=len(Symbols)
	A=np.zeros((1,N))

	store=pd.HDFStore('data.h5')
	print i
	s1=Symbols[i]
	x=store[s1].loc[T0:Tf,'Close'].values
	if len(x)<10:
		with open('CloseCorr_'+str(i)+'.npz','w') as F:
			np.save(F,A)  
		return


	x=x-min(x)
	a=max(x)
	if a>0:
		x=x/a

	for j in range(i,len(Symbols)):
		s2=Symbols[j]
		y=store[s2].loc[T0:Tf,'Close'].values
		if len(y)<10:
			continue

		y=y-min(y)
		b=max(y)
		if b>0:
			y=y/b

		n=min(len(x),len(y))
		A[0,j]=np.corrcoef(x[0:n],y[0:n])[0,1]

	with open('CloseCorr_'+str(i)+'.npz','w') as F:
		np.save(F,A)       

	store.close()

if __name__=='__main__':
	print __name__

	p = mp.Pool(4)
	p.map(getall, range(N))

	# P=[]
	
	# for i in range(N):
	# 	P.append( mp.Process(target=getall,args=(i,) ) )


	# print __name__
	# for p in P:
	# 	p.start()
		
	# for p in P:
	# 	p.join()


# for i in range(0,len(Symbols)):
#     print i
#     s1=Symbols[i]
#     x=store[s1].loc[T0:Tf,'Close'].values
#     if len(x)<10:
#       continue

#     x=x-min(x)
#     a=max(x)
#     x=x/a
#     for j in range(i,len(Symbols)):
#         s2=Symbols[j]
#         y=store[s2].loc[T0:Tf,'Close'].values
#         if len(y)<10:
#           continue

#         y=y-min(y)
#         b=max(y)
#         y=y/b

#         n=min(len(x),len(y))
#         A[i,j]=np.corrcoef(x[0:n],y[0:n])[0,1]

# with open('CloseCorr.npz','w') as F:
#     np.save(F,A)           
	
# store.close()
