# 2022.6.29  
from uvirun import *
import spacy
if not hasattr(spacy, 'nlp'): spacy.nlp  = spacy.load('en_core_web_sm')

@app.get('/spacy/tok', tags=["spacy"])
def spacy_tok(text:str='The boy is happy. The quick fox jumped over the lazy dog.',chunks:bool=False): 
	''' select * from url('http://cpu76.wrask.com:8000/spacy/tok', JSONEachRow, 'i UInt32, head UInt32, off UInt32, lex String, text_with_ws String,lem String, pos String, tag String, dep String, gov String') ''' 
	doc = spacy.nlp(text) 
	dic = { t.i: {'i':t.i, "head":t.head.i, 'off':t.idx, 'lex':t.text, 'text_with_ws':t.text_with_ws, 'lem':t.lemma_, 'pos':t.pos_, 'tag':t.tag_, 'dep':t.dep_, "gov":t.head.lemma_ + "_" + t.head.pos_ }  for t in doc }
	if chunks: 
		[v.update({"chunks":[]}) for k,v in dic.items()]
		[ dic[ sp.end - 1 ]['chunks'].append( {'lempos': doc[sp.end - 1].lemma_ + "_NOUN", "type":"NP", "chunk":sp.text.lower() } ) for sp in doc.noun_chunks]   ## start/end ? 
	return [ v for v in dic.values()]  # colored VERB html

@app.get('/spacy/trp', tags=["spacy"])
def spacy_trp(text:str='The boy is happy. The quick fox jumped over the lazy dog.'): 
	''' select * from url('http://cpu76.wrask.com:8000/spacy/trp', JSONEachRow, 'rel String, gov String, dep String') ''' 
	return [{'rel':f"{t.dep_}_{t.head.pos_}_{t.pos_}", "gov":t.head.lemma_, 'dep':t.lemma_}  for t in spacy.nlp(text)  ]

@app.get('/spacy/highlight', tags=["spacy"])
def doc_highlight(text:str='The boy is happy. The quick fox jumped over the lazy dog.', pos:str='ADJ'):
	''' return html, with pos highlighted ''' 
	doc = spacy.nlp(text) 
	arr = [ ("<b>" if t.pos_ == pos else "") + t.text_with_ws + ("</b>" if t.pos_ == pos else "") for t in doc]
	return "".join(arr) 

@app.get('/spacy/toks', tags=["spacy"])
def spacy_toks(text:str='The boy is happy. The quick fox jumped over the lazy dog.',chunks:bool=False, sino:str='sino', native:str='dic'): 
	''' [{'i': 0, 'head': 1, 'lex': 'The', 'lem': 'the', 'pos': 'DET', 'tag': 'DT', 'dep': 'det', 'gov': 'boy_NOUN', 'chunks': []}, {'i': 1, 'head': 2, 'lex': 'boy', 'lem': 'boy', 'pos': 'NOUN', 'tag': 'NN', 'dep': 'nsubj', 'gov': 'be_AUX', 'chunks': [{'lempos': 'boy_NOUN', 'type': 'NP', 'chunk': 'the boy'}]}, {'i': 2, 'head': 2, 'lex': 'is', 'lem': 'be', 'pos': 'AUX', 'tag': 'VBZ', 'dep': 'ROOT', 'gov': 'be_AUX', 'chunks': []}, {'i': 3, 'head': 2, 'lex': 'happy', 'lem': 'happy', 'pos': 'ADJ', 'tag': 'JJ', 'dep': 'acomp', 'gov': 'be_AUX', 'chunks': []}, {'i': 4, 'head': 2, 'lex': '.', 'lem': '.', 'pos': 'PUNCT', 'tag': '.', 'dep': 'punct', 'gov': 'be_AUX', 'chunks': []}] JSONEachRow format , added 2022.6.25 ''' 
	from dic.word_idf import word_idf 
	from dic.word_awl import word_awl
	from cos_fastapi  import cos_lemma_keyness
	doc = spacy.nlp(text) 
	dic = { t.i: {'i':t.i, "head":t.head.i, 'off':t.idx, 'idf': word_idf.get(t.text.lower(), 0),'awl': 1 if t.text.lower() in word_awl else 0, 
		'keyness': cos_lemma_keyness(t.pos_, t.lemma_, sino, native) if t.pos_ in ('NOUN','VERB','ADJ','ADV') else 0 , 
		'lex':t.text, 'text_with_ws':t.text_with_ws, 'lem':t.lemma_, 'pos':t.pos_, 'tag':t.tag_, 'dep':t.dep_, "gov":t.head.lemma_ + "_" + t.head.pos_ }  for t in doc}
	if chunks: 
		[v.update({"chunks":[]}) for k,v in dic.items()]
		[ dic[ sp.end - 1 ]['chunks'].append( {'lempos': doc[sp.end - 1].lemma_ + "_NOUN", "type":"NP", "chunk":sp.text.lower() } ) for sp in doc.noun_chunks]   ## start/end ? 
	return [ v for v in dic.values()]  # colored VERB html

@app.get('/spacy/dsk', tags=["spacy"])
def dsk(text:str='The boy is happy. The quick fox jumped over the lazy dog.'):
	res = requests.post("http://gpu120.wrask.com:8180/gecdsk", json={"essay_or_snts":text}).json()
	snts = [ dict( mkf.get("meta",{}), **{"feedback": [ v for cate, v in mkf.get('feedback',{}).items() ] } ) for mkf in res.get('snt',[])]
	return {
	#"feedback": [v for mkf in res.get('snt',[]) for cate, v in mkf.get('feedback',{}).items()], 
	"snt": snts, 
	"info": res.get('info',{}), 
	}

@app.get("/spacy/terms", tags=["spacy"])
def nlp_terms(text:str="The quick fox jumped over the lazy dog. The justice delayed is justice denied."):
	''' for sqlite indexing, 2022.3.4 '''
	tdoc = spacy.nlp(text)
	arr = []
	for sent in tdoc.sents: 
		doc = sent.as_doc()
		arr.append( { "snt": sent.text, 
		"tokens": [ {"id": t.i,"offset":t.idx, "word": t.text, "lemma":t.lemma_, "is_stop":t.is_stop, "parent": -1, "np_root": False, "pos": t.pos_, "tag": t.tag_, "dep": t.dep_,"text_with_ws": t.text_with_ws, "head": t.head.i , "sent_start": t.is_sent_start, "sent_end":t.is_sent_end}  for t in doc], 
		"triples": [ {"id":t.i,"offset":t.idx, "rel": t.dep_, "govlem":t.head.lemma_, "govpos": t.head.pos_, "deplem": t.lemma_, "deppos": t.pos_} for t in doc], 
		"chunk": [ {"id": np.start, "offset": doc[np.start].idx, "lem": doc[np.end-1].lemma_, "chunk":np.text, "end":np.end} for np in doc.noun_chunks], 
		} )
	return arr 

@app.get("/spacy/sntbr", tags=["spacy"])
def nlp_sntbr(text:str="The quick fox jumped over the lazy dog. The justice delayed is justice denied.", trim:bool=True):
	'''  '''
	return spacy.sntbr(text, trim) 

@app.post("/spacy/wordidf", tags=["spacy"])
def nlp_wordidf(words:list=["niche","dilemma","consider","consider**"], default_idf:float=0):
	'''  '''
	from dic.word_idf import word_idf 
	return  { w: word_idf.get(w, default_idf) for w in words}

if __name__ == "__main__":  #uvicorn.run(app, host='0.0.0.0', port=19200)
	print (spacy_trp())	