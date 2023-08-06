# 2022.6.30 cp from uvicorn corpusly-19200:app --host 0.0.0.0 --port 19200 --reload
from uvirun import *
from util import likelihood

@app.post('/util/dualarr_keyness')
def dualarr_keyness(src:dict={"one":2, "two":12}, tgt:dict={"three":3, "one":1}, sum1:float=None, sum2:float=None, threshold:float=0.0, leftonly:bool=False): 
	'''  "src": {"one":2, "two":12}, "tgt": {"three":3, "one":1}, added 2021.10.24  '''
	if not sum1: sum1 = sum([i for s,i in src.items()])
	if not sum2: sum2 = sum([i for s,i in tgt.items()])
	if not sum1: sum1 = 0.0001
	if not sum2: sum2 = 0.0001
	words = set(src.keys()) | set(tgt.keys()) if not leftonly else set(src.keys())
	res  = [(w, src.get(w,0), tgt.get(w,0), sum1, sum2, likelihood(src.get(w,0.01), tgt.get(w,0.01), sum1, sum2))  for w in words]
	res.sort(key=lambda a:a[-1], reverse=True)
	return [ar for ar in res if abs(ar[-1]) > threshold ]

if __name__ == "__main__":  
	print (dualarr_keyness())
	uvicorn.run(app, host='0.0.0.0', port=80)