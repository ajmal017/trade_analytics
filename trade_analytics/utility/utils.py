

def chunkify(L,n):
	for i in range(0,len(L),n):
		yield L[i:i+n]