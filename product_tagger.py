# ! /usr/local/bin python
# -*- coding:utf-8 -*-

'''
Main file of the project. 
The project aims at findng core terms, brand, and descriptions
from a product title from e-commerce websites.

The e-commerce product title lacks grammatical structure and can 
be hardly processed using context information. One characteristic 
of e-commerce product titles is that they are usually short. Therefore,
I come up with the Look up tagger approach to ahieve the objective.

The steps are as follows:
	- Construct a brand name library and a product name library. 
		Please refer to `library_builder.py'.
	- Build a tag table using the product name library and brand
		name library. Please refer to `tagTable_builder.py'.
	- Build a lookup tagger using `nltk.UnigramTagger' with the 
		built tag table.
	- After processing each product title, generate unit-, bi-, 
		and tri-grams. A lot of product and brand names contain ngrams.
	- Look up trigrams first, and then bigrams, and at last unigrams.
		Trigrams are taken with highest priority and unigrams the lowest.
	- If no product name is found in the product title after all the 
		lookup procedure, extract the last alpha noun in the title as 
		the product name. If no brand name is found, leave it empty.
	- As the product title itself is very short, we assume all the information
		in it is useful. Then all the other words are descriptive information.

Usage:
	>> tag_product(title)
	return (core_term, brand, descriptions)

Example:
	>> tag_product('Makibes Unisex Red LED Digital Band Wrist Watch')
	(u'watch', u'makibes',u'unisex red led digital band wrist')

@author = Yong Zhang
@email = yzhang067@e.ntu.edu.sg

'''

import nltk
from nltk.util import ngrams
from utils import remove_punct
import cPickle as pickle
import logging
import xlrd
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
this_dir, this_filename = os.path.split(__file__)
Table_PATH = os.path.join(this_dir, "resources", "tagTable.pkl")

def extract_words(all_words):
	"""
	Product title contains some preposition words.
	The words after preposition word usually indicate
	components, materials or intended usage. Therefore,
	there is no need to find brand and product name in
	the words after preposition. There is one exception:
	the preposition word appears in the first place.
	"""

	prepositions = ['for','with','from','of','by','on']
	MODE = 0 if all_words[0] in prepositions else 1
	if MODE:
		words = []
		for word in all_words:
			if word not in prepositions:
				words.append(word)
			else:
				break
	else:
		words = all_words	

	return words

def extract_attributes(grams, core_term, brand, tagger):
	"""
	Extract word with 'C' tag as core term.
	Extract word with 'B' tag as brand name.

	If there are multiple core terms and brand names,
	The first of brand names is taken as brand name.
	The last of core terms if taken as core term.

	"""

	core_terms, brands = [], []
	for token, tag in tagger.tag(grams):
		if tag == 'C':
			if not core_term:
				core_terms.append(token)
		elif tag == 'B':
			if not brand:
				brands.append(token)
		else:
			continue

	try:
		ct = core_terms[-1]
	except Exception, e:
		ct= core_term 

	try:
		br = brands[0]
	except Exception, e:
		br = brand

	return ct, br


def tag_product(product_title):
	"""
	Tag product_title and return core term, brand name, and discriptions.

	Input:
		string: product_title
	Return:
		string: core_term 
		string: brand 
		string: disc
	"""

	## build a tagger model
	with open(Table_PATH,'rb') as f:
		tag_table = pickle.load(f)
	tagger = nltk.UnigramTagger(model=tag_table, backoff=nltk.DefaultTagger('D'))

	## remove punctuations from product title
	product_title_tmp = remove_punct(product_title)
	## convert plurals to singulars
	wnl = nltk.WordNetLemmatizer()
	product_words = [wnl.lemmatize(s) for s in product_title_tmp.split()]
	clean_title = ' '.join(product_words)

	## build unigrams, bigrams, trigrams from which product 
	## attributes are to be extracted.
	unigrams = extract_words(product_words)
	bigrams  = [' '.join(item) for item in ngrams(unigrams, 2)]
	trigrams = [' '.join(item) for item in ngrams(unigrams, 3)]

	## Extract attributes from trigrams. If failed, extract from bigrams.
	## If still failed, extract from unigrams. If still failed, set the 
	## last alpha noun as product core term and leave brand empty.
	core_term, brand = None, None
	core_term, brand = extract_attributes(trigrams, core_term, brand, tagger)
	if not core_term or not brand:
		core_term, brand = extract_attributes(bigrams, core_term, brand, tagger)
	if not core_term or not brand:
		core_term, brand = extract_attributes(unigrams, core_term, brand, tagger)
	if not core_term:
		pos_words = nltk.pos_tag(unigrams)
		for word, tag in pos_words[::-1]:
			if tag == 'NN' and word.isalpha():
				core_term = word
				break
	if not brand:
		brand = ''

	## The words other than the core term and brand name are regarded as
	## description information.
	try:
		disc = clean_title.replace(core_term, '').replace(brand, '')
		disc = ' '.join(w for w in disc.split())		
	except Exception, e:
		info.logging('Cannot find core terms from the product title')

	return core_term, brand, disc

def extract_file(excel_sheet, filename_save):
	"""
	Extracting product attritbues from product titles in a .xlsx file
	"""
	if os.path.exists(filename_save):
		os.remove(filename_save)
	with open(filename_save, 'a') as f:
		f.write('Product name, Core terms, Brands, Discriptions\n')
		for row_idx in range(1, excel_sheet.nrows):
			product_title = excel_sheet.cell(row_idx, 1).value
			core_term, brand, disc = tag_product(product_title)
			f.write(product_title.replace(',','')+','+core_term+','+brand+','+disc+'\n')

def project_reuslt():
	"""
	Testing the tagger on project data. Uncomment `project_reuslt()' and
	comment other lines and run.

	"""
	file_dir = 'Product Data.xlsx'
	workbook = xlrd.open_workbook(file_dir)
	sheet_sample = workbook.sheet_by_index(0)
	sheet_test = workbook.sheet_by_index(1)

	extract_file(sheet_sample, 'results/sample_results.csv')
	extract_file(sheet_test, 'results/test_results.csv')	

if __name__ == '__main__':
	core_term, brand, disc = tag_product(sys.argv[1])
	print('===========')
	print('Core term: ',core_term)
	print('Brand: ',brand)
	print('Discriptions: ',disc)
	# project_reuslt()




