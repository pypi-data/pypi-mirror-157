# 2022-2-13  cp from cikuu/bin/es.py 
import json,fire,sys, os, hashlib ,time , requests
from collections import Counter , defaultdict
import warnings
warnings.filterwarnings("ignore")

def index_doc(did, doc):  
	''' arr: additional attr, such as filename , '''
	import en  
	from en import terms,verbnet
	from en.dims import docs_to_dims
	attach = lambda doc: ( terms.attach(doc), verbnet.attach(doc), doc.user_data )[-1]  # return ssv, defaultdict(dict)

	arr  = {} #{"did": did}
	snts = [snt.text for snt in doc.sents]
	docs = [snt.as_doc() for snt in doc.sents] #spacy.getdoc(snt)

	if len(docs) > 1 : # at least 2 snts will be treated as a document
		dims = docs_to_dims(snts, docs)
		dims.update({'type':'doc', "sntnum":len(snts), "wordnum": sum([ len(snt) for snt in snts]), 'tm': time.time()})
		arr[did] = dims 

	for idx, sdoc in enumerate(docs):
		arr[f"{did}-{idx}"] = {'type':'snt', 'snt':snts[idx], 'pred_offset': en.pred_offset(sdoc), 
				'postag':' '.join([f"{t.text}_{t.lemma_}_{t.pos_}_{t.tag_}" if t.text == t.text.lower() else f"{t.text}_{t.text.lower()}_{t.lemma_}_{t.pos_}_{t.tag_}" for t in sdoc]),
				'src': f"{did}-{idx}",  'tc': len(sdoc)} # src = sentid 
		ssv = attach(sdoc) 
		for id, sour in ssv.items():
			sour.update({"src":f"{did}-{idx}"}) # sid
			arr[f"{did}-{idx}-{id}"] = sour
	return arr

from so import * 
cursor_sql = lambda query, cursor: requests.post(f"http://{requests.eshost}:{requests.esport}/_sql", json={"query":query, "cursor":cursor}).json() #  move to so/__init__ later

def sqlsi(query): #select lex, count(*)
	si = Counter()
	cursor=''
	while True : 
		res = cursor_sql(query, cursor)  
		si.update( dict(res['rows']) )
		cursor = res.get('cursor','') 
		if not cursor: break
	return dict(si.most_common())

class ES(object):
	def __init__(self, eshost='127.0.0.1',esport=9200): 
		self.host = eshost # to be removed later 
		self.port = esport 
		self.es	  = Elasticsearch([ f"http://{eshost}:{esport}" ])  
		requests.eshost	= eshost
		requests.esport	= esport
		requests.es		= Elasticsearch([ f"http://{requests.eshost}:{requests.esport}" ])  

	def addfolder(self, folder:str, pattern=".txt", idxname=None): 
		''' folder -> docbase, 2022.1.23 '''
		if idxname is None : idxname=  folder
		print("addfolder started:", folder, idxname, self.es, flush=True)
		if not self.es.indices.exists(index=idxname): self.es.indices.create(index=idxname, body=config)
		for root, dirs, files in os.walk(folder):
			for file in files: 
				if file.endswith(pattern):
					self.add(f"{folder}/{file}", idxname = idxname) 
					print (f"{folder}/{file}", flush=True)
		print("addfolder finished:", folder, idxname, self.es, flush=True)

	def annotate(self, infile, idxname): 
		''' 2022.3.24 '''
		from en import esjson
		print("annotate started:", infile, idxname, self.es, flush=True)
		if not self.es.indices.exists(idxname): self.es.indices.create(idxname, config)

		text = open(infile,'r').read().strip()
		ssv  = esjson.annotate(text ) 
		for id, sv in ssv.items(): 
			self.es.index(index = idxname, id = id, body = sv)
		print("annotate finished:", infile,idxname)

	def add(self, infile, idxname="testdoc"):
		''' add doc only , 2022.3.25 '''
		if not self.es.indices.exists(index=idxname): self.es.indices.create(index=idxname, body=config)
		start = time.time()
		text = open(infile, 'r').read().strip() 
		did	 = hashlib.md5(text.encode("utf8")).hexdigest()
		self.es.index(index=idxname, body={"doc":text,  "filename": infile, 'type':'doc'}, id = did)
		ssv  = index_doc(did, spacy.nlp(text))
		for id, sv in ssv.items(): 
			try:
				self.es.index(index = idxname, id = id, body = sv)
			except Exception as ex:
				print(">>add ex:", ex, id, sv)
		print(f"{infile} is finished, \t| using: ", time.time() - start) 

	def loadsnt(self, infile, idxname=None):
		''' add doc only , 2022.3.25 '''
		if idxname is None : idxname = infile.split('.')[0] 
		if not self.es.indices.exists(index=idxname): self.es.indices.create(index=idxname, body=config)
		start = time.time()
		for idx, line in enumerate(open(infile, 'r').readlines()): 
			ssv  = index_doc(idx, spacy.nlp(line.strip()))
			for id, sv in ssv.items(): 
				try:
					self.es.index(index = idxname, id = id, document = sv) #https://github.com/elastic/elasticsearch-py/issues/1698
				except Exception as ex:
					print(">>add ex:", ex, id, sv)
		print(f"{infile} is finished, \t| using: ", time.time() - start) 

	def sntvec(self, idxname): 
		''' add snt vec into snt, 2022.3.25 
		python -m so sntvec testdoc
		pip install -U sentence-transformers
		'''
		from sentence_transformers import SentenceTransformer
		if not hasattr(fire, 'model'): 
			fire.model = SentenceTransformer('all-MiniLM-L6-v2')
			print ("model loaded:", fire.model, flush=True)

		print("sntvec started:", idxname, flush=True) 
		for doc in helpers.scan(client=self.es, query={"query" : {"match" : {"type":"snt"}} }, index=idxname):
			sid	= doc['_id']
			snt	= doc['_source']['snt']
			vec	= fire.model.encode(snt.strip()).tolist()
			print (sid, snt, len(vec))
			self.es.index(index=idxname, body={"_snt":snt,  "sntvec": vec, 'type':'sntvec'}, id = f"{sid}-sntvec")
		print("sntvec finished:", idxname) 

	def propbank(self, idxname): 
		'''  add flair semantic tag into snt, 2022.3.25
		python -m so propbank testdoc
		'''
		from flair.models import SequenceTagger
		from flair.tokenization import SegtokSentenceSplitter
		from flair.data import Sentence
		if not hasattr(fire, 'tagger'): 
			fire.tagger = SequenceTagger.load('frame-fast')  # 115M 
			print ("flair tagger loaded:", fire.tagger, flush=True)

		print("propbank started:", idxname, flush=True) 
		for doc in helpers.scan(client=self.es, query={"query" : {"match" : {"type":"snt"}} }, index=idxname):
			try:
				sid	= doc['_id']
				snt = Sentence(doc['_source']['snt']) #George returned to Berlin to return his hat.
				fire.tagger.predict(snt)
				self.es.index(index=idxname, body={"src":sid, 'chunk': snt.to_tagged_string(), 'type':'propbank-snt'}, id = f"{sid}-propbank")
				for sp in snt.get_spans():  # tag = return.01 
					self.es.index(index=idxname, body={"src":sid,  "lem": sp.tag.split('.')[0],  "tag": sp.tag, 'lex': sp.text, 'ibeg':sp.start_pos, 'iend': sp.end_pos, 'offset': int(sp.position_string), 'type':'propbank'}, id = f"{sid}-propbank-{sp.position_string}")
			except Exception as ex:
				print ("propbank ex:", ex, doc )
		print("propbank finished:", idxname) 
	
	def init(self, idxname):
		''' init a new index '''
		if self.es.indices.exists(index=idxname):self.es.indices.delete(index=idxname)
		self.es.indices.create(index=idxname, body=config) #, body=snt_mapping
		print(">>finished " + idxname )

	def clear(self,idxname): self.es.delete_by_query(index=idxname, body={"query": {"match_all": {}}})
	def dumpid(self, idxname): [print (doc['_id'] + "\t" + json.dumps(doc['_source']))  for doc in helpers.scan(self.es,query={"query": {"match_all": {}}}, index=idxname)]
	def dumpraw(self, idxname): [print (json.dumps(doc))  for doc in helpers.scan(self.es,query={"query": {"match_all": {}}}, index=idxname)]
	def keys(self, idxname): [print(resp['_id']) for resp in  helpers.scan(client=self.es, query={"query" : {"match_all" : {}}}, scroll= "10m", index= idxname , timeout="10m") ]
	def hello(self): print (requests.es)

	def dump(self, idxname): 
		''' python -m so dump gzjc  > gzjc.esjson '''
		for doc in helpers.scan(self.es,query={"query": {"match_all": {}}}, index=idxname):
			del doc["sort"]
			del doc["_score"]
			print (json.dumps(doc))  

	def sql(self, query="select lem, count(*) cnt from dic where type = 'tok' and pos ='VERB' and lem rlike '[a-z]+' group by lem"): 
		''' python -m so sql "select lem, count(*) cnt from gzjc where type = 'tok' and pos ='VERB' and lem rlike '[a-z]+' group by lem"  > gzjc.esjson '''
		cursor=''
		while True : 
			res = requests.post(f"http://{self.host}:{self.port}/_sql", json={"query":query, "cursor":cursor}).json()
			print (json.dumps(res['rows']))
			cursor = res.get('cursor','') 
			if not cursor: break			

	def lemcnt(self, idxname, pos='LEX'): 
		''' python -m so lemcnt dic --pos VERB , 2022.6.23 '''
		si = Counter()
		query=f"select lex, count(*) cnt from {idxname} where type = 'tok' and lex rlike '[a-zA-Z]+' group by lex" if pos == 'LEX' else f"select lem, count(*) cnt from {idxname} where type = 'tok' and lem rlike '[a-z]+' group by lem" if pos == 'LEM' else f"select lem, count(*) cnt from {idxname} where type = 'tok' and pos ='{pos}' and lem rlike '[a-z]+' group by lem"
		cursor=''
		while True : 
			res = cursor_sql(query, cursor)  # res = requests.post(f"http://{self.host}:{self.port}/_sql", json={"query":query, "cursor":cursor}).json()
			si.update( dict(res['rows']) )
			cursor = res.get('cursor','') 
			if not cursor: break
		print ( json.dumps( dict({k:v for k,v in si.most_common()}, **{"_sntnum": sntnum(idxname), "_sum": sum([v for k,v in si.items()])} ) ) ) 

	def trpcnt(self, idxname, dep='dobj', gpos='VERB', dpos='NOUN', inverse:bool=False): 
		''' python -m so trpcnt dic --dep dobj , 2022.6.23 '''
		ssi = defaultdict(Counter)
		query=f"select gov, lem, count(*) cnt from {idxname} where type = 'tok' and pos = '{dpos}' and dep ='{dep}' and lem rlike '[a-z]+' and gov like '%_{gpos}' group by gov, lem"
		cursor=''
		while True : 
			res = cursor_sql(query, cursor) 
			[ ssi[ lem ].update({gov.split('_')[0]:cnt}) for gov, lem, cnt in res['rows'] ] if inverse else [ ssi[gov.split('_')[0] ].update({lem:cnt}) for gov, lem, cnt in res['rows'] ]
			cursor = res.get('cursor','') 
			if not cursor: break
		print ( json.dumps( dict({ k: dict(v.most_common()) for k,v in ssi.items()}, **{"_sntnum": sntnum(idxname) } ) ) ) 

	def poscnt(self, idxname): 
		''' python -m so poscnt dic , 2022.6.23 '''
		ssi = defaultdict(Counter)
		query=f"select lem, pos, count(*) cnt from {idxname} where type = 'tok' and lem rlike '[a-z]+' group by lem, pos"
		cursor=''
		while True : 
			res = cursor_sql(query, cursor) 
			[ ssi[ lem ].update({pos:cnt}) for lem, pos, cnt in res['rows'] if pos not in ('NNP','X')] 
			cursor = res.get('cursor','') 
			if not cursor: break
		print ( json.dumps( dict({ k: dict(v.most_common()) for k,v in ssi.items()}, **{"_sntnum": sntnum(idxname) } ) ) ) 

	def meta(self, idxname):
		''' '''
		dic = 
		{
		"wordlen": sqlsi(f"select length(lex) wc, count(*) cnt from {idxname} where type = 'tok' group by wc"), 
		"poscnt": sqlsi(f"select pos, count(*) cnt from {idxname} where type = 'tok' group by pos"), 

		"_sntnum": sntnum(idxname)
		}

	def ssi(self, query="select lem, lex, count(*) cnt from gzjc where type = 'tok' and lem rlike '[a-z]+' group by lem, lex"): 
		''' python -m so ssi ...  > gzjc.lexcnt , 2022.6.27 '''
		ssi = defaultdict(Counter)
		cursor=''
		while True : 
			res = cursor_sql(query, cursor) 
			[ ssi[ lem ].update({lex.lower():cnt}) for lem, lex, cnt in res['rows'] ] 
			cursor = res.get('cursor','') 
			if not cursor: break
		idxname = query.split("where")[0].strip().split("from")[-1].strip()
		print ( json.dumps( dict({ k: dict(v.most_common()) for k,v in ssi.items()}, **{"_sntnum": sntnum(idxname) } ) ) ) 

	def load(self, infile, idxname=None, batch=100000, refresh:bool=True): 
		''' python3 -m so load gzjc.esjson '''
		if not idxname : idxname = infile.split('.')[0]
		print(">>started: " , infile, idxname, flush=True )
		#if refresh: self.clear(idxname) 
		actions=[]
		for line in readline(infile): 
			try:
				arr = json.loads(line)  #arr.update({'_op_type':'index', '_index':idxname,}) 
				actions.append( {'_op_type':'index', '_index':idxname, '_id': arr.get('_id',None), '_source': arr.get('_source',{}) } )
				if len(actions) >= batch: 
					helpers.bulk(client=self.es,actions=actions, raise_on_error=False)
					print ( actions[-1], flush=True)
					actions = []
			except Exception as e:
				print("ex:", e)	
		if actions : helpers.bulk(client=self.es,actions=actions, raise_on_error=False)
		print(">>finished " , infile, idxname )

if __name__ == '__main__':
	fire.Fire(ES)

'''
ubuntu@es-corpusly-com-105-249:/data/cikuu/pypi/so$ python __main__.py ssi  --query "select pos, lem, count(*) cnt from gzjc where type = 'tok' and lem rlike '[a-z]+' group by pos, lem" > gzjc.poslemcnt

'''