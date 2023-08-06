import nltk  # synset 
import pymysql
_conn = pymysql.connect(host='localhost',port=3336,user='root',password='cikuutest!',db='snt')

nltk_tok =  lambda snt: nltk.word_tokenize(snt)  #return tok array
nltk_pos =  lambda toks: nltk.pos_tag(toks) #[('i', 'NN'), ('hate', 'VBP'), ('study', 'NN'), ('on', 'IN'), ('monday', 'NN'), ('.', '.'), ('Jim', 'NNP'), ('like', 'IN'), ('rabbit', 'NN'), ('.', '.')]

words= nltk.word_tokenize('i hate study on monday. Jim like rabbit.')
pos_tags =nltk.pos_tag(words)
print(pos_tags)


def select(sql): 
	cursor = _conn.cursor()
	cursor.execute(sql)
	data = cursor.fetchall()
	cursor.close()
	return data
	
def update(sid, ske): 
	cursor = _conn.cursor()
	cursor.execute( "update possnt set nltk = '%s' where sid = %d" % (ske.replace("'","''"),  sid))
	cursor.close()

if __name__ == '__main__':
	rows = select("select sid,ske from possnt")
	for row in rows: 
		try:
			toks = row[1].split(" ")
			tagged = nltk.pos_tag(toks)
			update(row[0], " ".join([ t[0] + "_" + t[1] for t in tagged]))
		except Exception:
			 print ('**str(Exception):\t', str(Exception))
	print(">>finished ")