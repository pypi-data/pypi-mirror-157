# 2022.6.30  #uvicorn trf_unmasker_fastapi:app --reload --port 80 --host 0.0.0.0
from uvirun import *

@app.get('/trf/unmasker', tags=["unmasker"])
def unmasker(q:str="The goal of life is [MASK].", model:str='native', topk:int=10, verbose:bool=False): 
	''' model: native/nju/fengtai/sino/sci/gblog/twit	'''
	from transformers import pipeline
	if not hasattr(unmasker, model): 
		setattr(unmasker, model, pipeline('fill-mask', model=f'/data/model/unmasker/distilbert-base-uncased-{model}') )
	arr = getattr(unmasker, model)(q, top_k = topk) #result: [{'score': 0.03619174659252167, 'token': 8404, 'token_str': 'happiness', 'sequence': 'the goal of life is happiness.'}, {'score': 0.030553610995411873, 'token': 7691, 'token_str': 'survival', 'sequence': 'the goal of life is survival.'}, {'score': 0.016977205872535706, 'token': 12611, 'token_str': 'salvation', 'sequence': 'the goal of life is salvation.'}, {'score': 0.016698481515049934, 'token': 4071, 'token_str': 'freedom', 'sequence': 'the goal of life is freedom.'}, {'score': 0.015267301350831985, 'token': 8499, 'token_str': 'unity', 'sequence': 'the goal of life is unity.'}]
	return [ dict( row, **{"name": model}) for row in arr ] if verbose else [ {"name": model, "word": row["token_str"], "score": round(row["score"], 4)} for row in arr ]

@app.get('/trf/unmaskers', tags=["unmasker"])
def unmaskers(q:str="The goal of life is [MASK].", models:str='native,nju', topk:int=10): 
	''' model: native/nju/fengtai/sino/sci/gblog/twit  2022.7.1 '''
	arr = []
	[ arr.extend(unmasker(q, model, topk)) for model in models.strip().split(',') ]
	return arr

if __name__ == '__main__': #print (models['native']("The goal of life is [MASK]."))
	print("result:", unmaskers())