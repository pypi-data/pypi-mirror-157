# 2022.7.2 cp from es_fastapi.py 
from uvirun import *
from util import likelihood
import re
requests.eshp	= os.getenv("eshp", "es.corpusly.com:9200") # host & port 
sntsum	= lambda cp: requests.post(f"http://{requests.eshp}/_sql",json={"query": f"select count(*) from {cp} where type ='snt'"}).json()['rows'][0][0]
toksum	= lambda cp: requests.post(f"http://{requests.eshp}/_sql",json={"query": f"select count(*) from {cp} where type ='tok'"}).json()['rows'][0][0]

@app.get('/corpusly/rows')
def rows(query="select lem, count(*) cnt  from gzjc where type = 'tok' and pos != 'PUNCT' group by lem order by cnt desc limit 10", raw:bool=False):
	''' # select gov, count(*) cnt from gzjc where type = 'tok' and lem='door' and pos='NOUN' and dep='dobj' group by gov'''
	res = requests.post(f"http://{requests.eshp}/_sql",json={"query": query}).json() 
	return res['rows'] if raw else  [  dict(zip([ ar['name'] for ar in res['columns'] ] , ar)) for ar in res.get('rows',[]) ] 

@app.get('/corpusly/sum/{cps}/{type}')
def corpus_sum(cps:str='gzjc,clec', type:str="snt"):
	''' {'gzjc': 8873, 'clec': 75322} '''
	return {cp: requests.post(f"http://{requests.eshp}/_sql",json={"query": f"select count(*) from {cp} where type ='{type}'"}).json()['rows'][0][0] for cp in cps.strip().split(',')}

@app.get("/corpusly/kwic")
def corpus_kwic(cp:str='dic', w:str="opened", topk:int=10, left_tag:str="<b>", right_tag:str="</b>"): 
	''' search snt using word,  | select snt,postag, tc from gzjc where type = 'snt' and match(snt, 'books') | 2022.6.19 '''
	return [ {"snt": re.sub(rf"\b({w})\b", f"{left_tag}{w}{right_tag}", snt), "tc": tc } for snt, postag, tc in rows(f"select snt, postag, tc from {cp.strip().split(',')[0]} where type = 'snt' and match (snt, '{w}') limit {topk}", raw=True)]

@app.get('/corpusly/xcnt/{cp}/{type}/{column}')
def corpusly_xcnt( column:str='lex', cp:str='dic', type:str='tok', where:str="", order:str="order by cnt desc limit 10" ):
	''' where:  and lem='book'  | JSONCompactColumns  * select lex,count(*) cnt from dic where type = 'tok' and lem= 'book' group by lex '''
	query  = f"select {column}, count(*) cnt from {cp} where type = '{type}' {where} group by {column} {order}"
	res = requests.post(f"http://{requests.eshp}/_sql",json={"query": query}).json() 
	return [  { column: ar[0], "cnt": ar[1]} for ar in res['rows'] ] 

@app.get("/corpusly/stats")
def corpus_stats(names:str=None, types:str="doc,snt,np,tok,trp,vp"):
	''' doc,snt,np,tok,simple_sent,vtov,vvbg,vp, added 2022.5.21 '''
	names = name.strip().split(',') if names else [ar['name'] for ar in sqlrows("show tables")  if not ar['name'].startswith(".") and ar['type'] == 'TABLE' and ar['kind'] == 'INDEX']
	types = types.replace(",", "','")
	return [ dict( dict(rows(f"select type, count(*) cnt from {name} where type in ('{types}') group by type")), **{"name":name} ) for name in names]

@app.get("/corpusly/mf")
def corpus_mf(cps:str="gzjc,clec", w:str="considered", topk:int=3, with_snt:bool=False):
	dic =  {cp: round(1000000 * phrase_num(w, cp) / (sntnum(cp)+0.1), 2 ) for cp in cps.strip().split(',') }
	return [ {"cp":cp, "mf":mf, "snts": json.dumps(kwic(cp, w, topk)) } for cp,mf in dic.items()] if with_snt else [ {"cp":cp, "mf":mf } for cp,mf in dic.items()]

@app.get("/corpusly/srcsnts")
def corpus_srcsnts(query:str="select src from gzjc where type='tok' and lem='book' and pos='NOUN' limit 10",highlight:str='book', left_tag:str="<b>", right_tag:str="</b>"):  #, cp:str='gzjc'
	''' '''
	cp = query.split("where")[0].strip().split('from')[-1].strip()
	srclist = "','".join([ src for src, in rows(query)])
	return [{'snt':re.sub(rf"\b({highlight})\b", f"{left_tag}{highlight}{right_tag}", snt)} for snt, in rows(f"select snt from {cp} where type='snt' and src in ('{srclist}')")]

@app.get("/corpusly/lempos/snts")
def lempos_snts(cp:str='gzjc', lem:str='book', pos:str='VERB', topk:int=3, left_tag:str="<b>", right_tag:str="</b>"): 
	''' "select snt from gzjc where type = 'snt' and kp = 'book_VERB' limit 2" , added 2022.6.24 '''
	query = f"select snt from {cp} where type = 'snt' and kp = '{lem}_{pos}' limit {topk}"
	return [{'snt':re.sub(rf"\b({lem})\b", f"{left_tag}{lem}{right_tag}", snt)} for snt, in rows(query)]	

@app.get("/corpusly/trp/snts")
def trp_snts(cp:str='gzjc', word:str='door', rel:str='~dobj_VERB_NOUN', cur:str='open',  topk:int=3): 
	query = f"select snt from {cp} where type = 'snt' and kp = '{rel[1:]}/{cur} {word}' limit {topk}" if rel.startswith('~') else f"select snt from {cp} where type = 'snt' and kp = '{rel}/{word} {cur}' limit {topk}"
	print (query, flush=True)
	return [{'snt':snt} for snt, in rows(query)]

@app.get('/corpusly/dualsql_keyness')
def text_keyness(sql1:str= "select lem,  count(*) from inau where type = 'tok' and pos='VERB'  group by lem", sql2:str="select lem,  count(*) from gzjc where type = 'tok' and pos='VERB' group by lem", threshold:float=0.0): 
	''' keyness of sql1, sql2, added 2021.10.24  '''
	src = dict(requests.post(f"http://{requests.eshost}:{requests.esport}/_sql",json={"query": sql1}).json()['rows'])
	tgt = dict(requests.post(f"http://{requests.eshost}:{requests.esport}/_sql",json={"query": sql2}).json()['rows'])
	return [ {"word": word, 'cnt1':c1, 'cnt2':c2, 'sum1':r1, 'sum2':r2, 'keyness':keyness} for word, c1, c2, r1, r2, keyness in dualarr_keyness(src, tgt, threshold) ]

if __name__ == "__main__":   #uvicorn.run(app, host='0.0.0.0', port=80)
	print (rows() )
	print ( corpus_sum())
	#	print (rows("show tables"))
	#print ( corpus_kwic()) 