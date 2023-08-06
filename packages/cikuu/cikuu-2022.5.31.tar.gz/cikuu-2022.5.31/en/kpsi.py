# 2022.7.6 cp from silite.py, since clickhouse DONOT support  sql with 'match' 
import json, traceback,sys, time, fire,pymysql,os
from collections import	Counter
import en 
from en.spacybs import Spacybs
from tqdm import tqdm
add = lambda *names: [fire.si.update({name: 1}) for name in names ]

def submit(cursor): # NOT used 
	#cursor.executemany(f"INSERT INTO table {name}(s,i) VALUES (%s, %s) ON DUPLICATE KEY UPDATE i = i + %s", [(k,v,v) for k,v in fire.si.items()] )
	for k,v in fire.si.items():
		if not "'" in k and len(k) < 128: 
			cursor.execute(f"INSERT INTO {name}(s,i) VALUES ('{k}', {v}) ON DUPLICATE KEY UPDATE i = i + {v}")
	print ( len(fire.si), flush=True)
	fire.si.clear()

def walk(doc): 
	add(f"#SNT") 
	for t in doc:
		if not t.pos_ in ('PROPN','X', 'PUNCT'): add( f"{t.lemma_}:POS:{t.pos_}")
		add(f"{t.lemma_}:LEX:{t.text.lower()}", f"LEM:{t.lemma_}", f"LEX:{t.text}", f"{t.pos_}:{t.lemma_}", "#LEX", f"#{t.pos_}", f"#{t.tag_}",f"#{t.dep_}",)
		add(f"{t.lemma_}:{t.pos_}:{t.tag_}:{t.text.lower()}",f"{t.lemma_}:{t.pos_}:{t.tag_}", f"{t.lemma_}:{t.pos_}") # book:VERB:VBG
		if t.pos_ not in ("PROPN","PUNCT"): 
			add(f"{t.head.lemma_}:{t.head.pos_}:{t.dep_}:{t.pos_}:{t.lemma_}", f"{t.head.lemma_}:{t.head.pos_}:{t.dep_}")
			if t.dep_ not in ('ROOT'): add(f"{t.lemma_}:{t.pos_}:~{t.dep_}:{t.head.pos_}:{t.head.lemma_}", f"{t.lemma_}:{t.pos_}:~{t.dep_}")
	for sp in doc.noun_chunks: #book:NOUN:np:a book
		add(f"{sp.root.lemma_.lower()}:{sp.root.pos_}:np:{sp.text.lower()}", f"{sp.root.lemma_.lower()}:{sp.root.pos_}:np", f"#np",)

	for type, chunk, start, end in en.vp_matcher(doc): #[('vend', 'consider going', 1, 3)
		add(f"{doc[start].lemma_}:{doc[start].pos_}:{type}:{chunk}") #consider:VERB:vtov:consider to go

def index(dbfile, host='127.0.0.1', port=3307, batch=100000):  
	''' clec.spacybs -> clec.kplite, 2022.7.4 '''
	print ("started index:", dbfile, flush=True)
	name = dbfile.lower().split('.')[0]
	fire.si = Counter()
	my_conn = pymysql.connect(host=host,port=port,user='root',password='cikuutest!',db='kpsi')
	with my_conn.cursor() as cursor: 
		cursor.execute(f"drop TABLE if exists {name}")
		cursor.execute(f"CREATE TABLE if not exists {name}(s varchar(128) COLLATE latin1_bin not null primary key, i int not null default 0) engine=myisam  DEFAULT CHARSET=latin1 COLLATE=latin1_bin")
		cursor.execute(f"drop TABLE if exists {name}_snt")
		cursor.execute(f"CREATE TABLE if not exists {name}_snt(sid int primary key, snt text not null, kps text not null, fulltext key `snt`(`snt`), fulltext key `kps`(`kps`) ) engine=myisam  DEFAULT CHARSET=latin1 COLLATE=latin1_bin")

		for rowid, snt, bs in tqdm(Spacybs(dbfile).items()) :
			try:
				doc =  spacy.frombs(bs)
				cursor.execute(f"insert ignore into {name}_snt(sid, snt, kps) values(%s, %s, %s)", (rowid,snt, " ".join([ f"{t.lemma_}_{t.pos_}" for t in doc] + [ f"{t.lemma_}_{t.tag_}" for t in doc] + [ f"{t.head.lemma_}_{t.head.pos_}_{t.dep_}_{t.pos_}_{t.lemma_}" for t in doc if t.pos_ not in ('PRON','PUNCT') and t.dep_ in ('dobj','nsubj','advmod','acomp','amod','compound','xcomp','ccomp')]) ))
				walk(doc)
				#if len(fire.si) >= batch :  submit(cursor)
			except Exception as e:
				print ("ex:", e, rowid, snt)

		cursor.executemany(f"insert ignore into {name}(s, i) values(%s, %s)",[(k,v) for k,v in fire.si.items()]) #cursor.executemany(f"INSERT INTO {name}(s,i) VALUES (%s, %s) ON DUPLICATE KEY UPDATE i = i + %s", [(k,v,v) for k,v in fire.si.items()] )
		my_conn.commit()
	print ("finished submitting:", dbfile, flush=True) 

if __name__	== '__main__':
	fire.Fire(index)

'''

docker run -d --restart=always --name=kpsi --env='MYSQL_ROOT_PASSWORD=cikuutest!' --volume=/data/mariadb-mysi:/var/lib/mysql -p 3307:3306 mariadb --max_allowed_packet=100M --max_connections=1000 --disable-log-bin --innodb_file_per_table=1  --read_buffer_size=64M --read_rnd_buffer_size=64M --join_buffer_size=16M --tmp_table_size=512M

select * from gzjc_snt where match(kps) against('write_VERB_dobj_NOUN_book')  limit 10;
select * from gzjc_snt where match(snt) against('book')  limit 10;

#for k,v in fire.si.items(): cursor.execute(f"insert ignore into {name}(s, i) values(%s, %s)", (k,v))

consider:VERB:vtov:considered to be|22 / consider:VERB:vtov:consider to be|22  is different
-- bnc.silite (s,i)  => clickhouse user_file    
open:VERB:dobj:NOUN:door  | open:VERB:dobj
book:NOUN:np:a book book:NOUN:npone:books
happen:VERB:VBG, 
book:LEX:books   knowledge:LEX:knowledges 
book:POS:VERB 
consider:VERB:vtov:consider to go  |  consider:VERB:vvbg:consider visiting
brink:NOUN:pp:on the brink
pretty:ADJ:ap:very pretty
consider:VERB:ROOTV
visit:VERB:vend:plan to visit

sqlite> select * from si where s like 'sound:VERB:%' and s not like 'sound:VERB:%:%';
sound:VERB:ROOT|12
sound:VERB:VB|1
sound:VERB:VBD|3
sound:VERB:VBG|1
sqlite> select * from si where s like 'consider:VERB:vtov:%';
consider:VERB:vtov:consider to be|3
sqlite>
sqlite> select * from si where s like 'VERB:%' order by i desc limit 10;
VERB:be|1315
VERB:have|698
VERB:make|417
VERB:go|394
sqlite> select * from si where s like 'sound:LEX:%';
sound:LEX:sound|21
sound:LEX:sounded|4
sound:LEX:sounding|1
sound:LEX:sounds|21
sqlite> select * from si where s like 'door:noun%' and s not like 'door:noun:%:%';
door:NOUN|26
door:NOUN:NN|21
door:NOUN:NNS|5
door:NOUN:ROOT|1
door:NOUN:advmod|1

(spacy311) (base) cikuu@gpu55:/data2/ftp/sntbs$ time python silite.py bnc.spacybs 
started index: bnc.spacybs
5311102it [2:11:43, 671.99it/s] 
finished submitting: bnc.spacybs

real	140m12.136s
user	132m10.230s
sys	6m16.526s

		for k,v in fire.si.items():
			if not "'" in k: 
				cursor.execute(f"INSERT INTO {name}(s,i) VALUES ('{k}', {v}) ON DUPLICATE KEY UPDATE i = i + {v}")


'''