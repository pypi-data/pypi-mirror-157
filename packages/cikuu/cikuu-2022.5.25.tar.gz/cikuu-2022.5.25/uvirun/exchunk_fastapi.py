# 2022.6.30
# pay attention to -> pay _jj attention to 
# 2022.2.10  uvicorn exchunk:app --host 0.0.0.0 --port 7058 --reload | 8004 @ cpu76
from uvirun import *
import spacy , traceback, sys,sqlite3
from spacy.matcher import Matcher
from collections import	Counter, defaultdict
if not hasattr(spacy,'nlp'): spacy.nlp	= spacy.load('en_core_web_sm')
merge_nps	= spacy.nlp.create_pipe("merge_noun_chunks")

#redis.rule	= redis.Redis("127.0.0.1", port=9221, db=1, decode_responses=True) # added 2022.2.19
conn	= sqlite3.connect("grampos.svdb", check_same_thread=False)  # how to set readonly ? 
getdb	= lambda keys=['pay _jj attention to','is _rb beautiful'] : { row[0] : row[1] for row in conn.execute("select s,v from sv where s in ('"+"','".join([k for k in keys])+"')") } # in ('one','two')
conn.execute(f'CREATE TABLE IF NOT EXISTS sv (s varchar(512) PRIMARY KEY, v blob)')

matcher	= Matcher(spacy.nlp.vocab)  # :1 , verb's offset 
NP_start= {"ENT_TYPE": "NP", "IS_SENT_START": True}
VERB	= {"POS": {"IN": ["VERB"]}}
VBN		= {"TAG": {"IN": ["VBN"]}}
NOUN	= {"POS": {"IN": ["NOUN"]}}
DET		= {"POS": {"IN": ["DET"]}}
TO		= {"TAG": {"IN": ["TO"]}}
BE		= {"LEMMA": "be"}
NN		= {"TAG": {"IN": ["NN"]}}
JJ		= {"TAG": {"IN": ["JJ"]}}
ADP		= {"POS": {"IN": ["ADP"]}}
PUNCT	= {"IS_PUNCT": True}

#  pay attention to:_jj:1  =>  close:133,closer:27
matcher.add("1:_jj:pay attention to", [[VERB,NOUN,ADP]]) # make use of , pay attention to -> pay _jj attention to 
matcher.add("1:_rb:is pretty/destroyed", [[BE,JJ],[BE,VBN]])
matcher.add("2:_rb:finished homework", [[VERB,NOUN,PUNCT]])
matcher.add("3:_rb:solve the problem", [[VERB,DET,NOUN,PUNCT]])
matcher.add("1:_rb:to open the door", [[TO,VERB,DET,NOUN],[TO,VERB,NOUN],[TO,VERB,{"POS":"PRP$"}]])  
matcher.add("2:_jj:make it *dead simple to", [[VERB,{"LEMMA": "it"},JJ,TO]]) #It will make it *dead simple to utilize the tools.

def chunk_ex(doc):
	for name, ibeg, iend in matcher(doc):
		offset, tag = spacy.nlp.vocab[name].text.split(':')[0:2]
		offset = int(offset) 
		yield { "ibeg":ibeg, "iend":iend, "tag":tag, "offset": offset, "pattern": " ".join( doc[i].text.lower() if i - ibeg != offset else  tag + " " + doc[i].text.lower() for i in range(ibeg, iend)) }

@app.get('/exchunk/snt')
def exchunk_snt(snt:str="I pay attention to the box, and she is beautiful.", verbose:bool=False): 
	''' It will make it simple to utilize the tools.  
	* dead  * super,  2022.2.10 '''
	doc = spacy.nlp(snt)
	res = list(chunk_ex(doc))
	for np in doc.noun_chunks:
		if doc[np.start].pos_ == 'DET' : 
			if len(np) == 2  and doc[np.start+1].pos_ == 'NOUN': 
				res.append( {"ibeg":np.start, "iend":np.end, "tag":'_jj' , "offset":1, "pattern": doc[np.start].text.lower() + " _jj " +  doc[np.start+1].text.lower() } ) 
			elif len(np) == 3  and doc[np.start+1].tag_ == 'JJ'  and doc[np.start+2].pos_ == 'NOUN': 
				res.append( {"ibeg":np.start, "iend":np.end, "tag":'_rb' , "offset":1, "pattern": doc[np.start].text.lower() + " _rb " +  doc[np.start+1:np.start+3].text.lower() } ) 

	dic = getdb([ar['pattern'] for ar in res]) 
	[ ar.update({"cands": dic[ ar['pattern'] ]}) for ar in res if ar['pattern'] in dic ]
	return res if verbose else [ar for ar in res if 'cands' in ar ] 

@app.post('/exchunk/snts')
def exchunk_snts(snts:list): 
	''' ["I pay attention to the box, and she is beautiful.","The quick fox jumped over the lazy dog."] '''
	return {snt: exchunk_snt(snt) for snt in snts}

@app.post('/exchunk/newrule')
def exchunk_newrule(rule:list, offset:int=1, tag:str='_jj', note:str=""): 
	''' [{"LEMMA": "be"},
           {"POS": "ADP"},
           {"POS": "PRON"},
           {"POS": "NOUN"},
           {"POS": "PUNCT"}] 
	https://explosion.ai/demos/matcher '''
	matcher.add(f"{offset}:{tag}:{note}", rule)  # submit to database later 
	return redis.rule.set(json.dumps(rule), f"{offset}:{tag}:{note}")	

if __name__ == "__main__":  
	#doc = spacy.nlp("I paid attention to the big box, and it is beautiful.") 
	#print (list(chunk_ex(doc))) #[(1, 4, '_jj', 1, 'paid _jj attention to'), (9, 11, '_jj', 1, 'is _jj beautiful')]
	print( exchunk_snt("It will make it simple to utilize the tools.", True))

'''
a girl	_dt _n	_dt _adj _n	a beautiful/tall/smart girl	
on the playground	_in _dt _n	_in _dt _n _n 	on the school playground	
in the morning	_in _dt _n	_in _dt _adj _n 	in the early morning	
To better your english skills	_to _v _prp$ _n	_to _rb _v _prp$ _n	To quickly better your english skills	
The building was destroyed	_n _v _vbn	_n _v _rb _vbn	The building was total destroyed	
finish homework	_v _n	_v _n _rb	finish homeword finally	
you should solve the problem 	_md _v _n	_md _v _n _rb	you should solve the problem properly	

overcome difficulty/dobj_VERB_NOUN  => {"ref":{"surmount difficulty/dobj_VERB_NOUN":0.83, "conque difficulty/dobj_VERB_NOUN":0.23} }
'''