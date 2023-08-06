# 2022.7.3   nltk.download('all')   =>  /home/ubuntu/nltk_data 
from uvirun import * 
import nltk  # synset 
from nltk.corpus import wordnet

@app.get('/nltk/tokenize', tags=["nltk"])
def nltk_tokenize(snt:str="i hate study on monday. Jim like rabbit."):
	return nltk.word_tokenize(snt)

@app.get('/nltk/postag', tags=["nltk"])
def nltk_postag(snt:str="i hate study on monday. Jim like rabbit."):
	words= nltk.word_tokenize(snt)
	pos_tags =nltk.pos_tag(words)
	return pos_tags

@app.get('/nltk/synset', tags=["nltk"])
def nltk_synset(word:str="cat"):
	py_arr = wordnet.synsets("cat")
	print(py_arr[0].definition()) #wordnet.synset ('cat.n.02').definition()
	#print (py_arr[0].lemma_names())
	#print(wordnet.synset('cat.n.02').hyponyms())
	return py_arr

#https://www.nltk.org/howto/lm.html  entropy

if __name__ == '__main__':
	#print (nltk_tokenize())
	print(wordnet.synsets('cat'))

'''
https://www.nltk.org/howto/wordnet.html
>>> wn.synsets('dog')
[Synset('dog.n.01'), Synset('frump.n.01'), Synset('dog.n.03'), Synset('cad.n.01'),
Synset('frank.n.02'), Synset('pawl.n.01'), Synset('andiron.n.01'), Synset('chase.v.01')]
>>> wn.synsets('dog', pos=wn.VERB)
[Synset('chase.v.01')]

The other parts of speech are NOUN, ADJ and ADV. A synset is identified with a 3-part name of the form: word.pos.nn:

>>> wn.synset('dog.n.01')
Synset('dog.n.01')
>>> print(wn.synset('dog.n.01').definition())
a member of the genus Canis (probably descended from the common wolf) that has been domesticated by man since prehistoric times; occurs in many breeds
>>> len(wn.synset('dog.n.01').examples())
1
>>> print(wn.synset('dog.n.01').examples()[0])
the dog barked all night
>>> wn.synset('dog.n.01').lemmas()
[Lemma('dog.n.01.dog'), Lemma('dog.n.01.domestic_dog'), Lemma('dog.n.01.Canis_familiaris')]
>>> [str(lemma.name()) for lemma in wn.synset('dog.n.01').lemmas()]
['dog', 'domestic_dog', 'Canis_familiaris']
>>> wn.lemma('dog.n.01.dog').synset()
Synset('dog.n.01')

https://www.educba.com/nltk-wordnet/
from nltk.corpus import wordnet
py_arr = wordnet.synsets("python")
print (py_arr[0].name())
print (py_arr[0].lemmas()[0].name())
print (py_arr[0].definition())
print (py_arr[0].examples())
'''