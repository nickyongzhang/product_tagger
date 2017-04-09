# ! /usr/local/bin python
# -*- coding:utf-8 -*-

'''
Prepare a tag table for the main script `product_tagger.py'
The table is a dictionary whose keys are either product names
or brand names. 
For all product names, values are set 'C' (core term).
For all brand names, values are set 'B' (brand name).

@author = Yong Zhang
@email = yzhang067@e.ntu.edu.sg

'''

import re
import logging
import cPickle as pickle
import nltk
from utils import remove_punct
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


def process_names(file_dir):
	"""
	For the brand and product names containing '-', generate
	two names: one take '-' as ' ' and the other as ''

	e.g. 'e-book' --> 'e book' and 'ebook'

	The other punctuations except \. and \' are excluded.
	"""
	results = []
	with open(file_dir, 'rb') as f:
		lines = f.readlines()
		for line in lines:
			if '-' in line:
				line1 = re.sub("-", ' ', line)
				results.append(remove_punct(line1))
				line2 = re.sub("-", '', line)
				results.append(remove_punct(line2))
			else:
				results.append(remove_punct(line))

	return list(set(results))

def main():
	logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

	wnl = nltk.WordNetLemmatizer()
	logging.info('Building tag dictionary from product and brand name lists')
	products = process_names('resources/product.txt')
	## Convert plural product names to singulars
	products = list(set([' '.join(wnl.lemmatize(s) for s in product.split()) for product in products]))
	brands   = process_names('resources/brand.txt')

	logging.info('If one word appears in both product names and brand names, it is regarded as product name')
	## dictionary can automatically update key values
	tagTable = dict([(b, 'B') for b in brands]+[(p, 'C') for p in products])
	logging.info('Tag dictionary built')

	logging.info('Save dictionary')
	save_file = 'resources/tagTable.pkl'
	with open(save_file,'wb') as f:
		pickle.dump(tagTable, f, -1)
	logging.info('Dictionary saved')


if __name__ == '__main__':
	main()



