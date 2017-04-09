# ! /usr/local/bin python
# -*- coding:utf-8 -*-

'''
Builders for product brands and product names

@author = Yong Zhang
@email = yzhang067@e.ntu.edu.sg

'''

import requests
from lxml import etree
import logging
import xlrd
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


user_agent ='''Mozilla/5.0 (Windows NT 6.1; WOW64) 
				AppleWebKit/537.36 (KHTML, like Gecko) 
				Chrome/51.0.2704.103 Safari/537.36'''
headers= {'user-agent':user_agent}


class BrandBuilder(object):
	"""
	Crawler for product brands. The crawler directly crawl 
	the page `http://www.lazada.sg/brands/'. The page contains 
	almost all the brands of ecommerce products.

	In order to build a more comprehensive brand library, other 
	sources may be considered. This may be a future work.
	Furthermore, as there are new brands comning out everyday,
	it may be good idea to update the library from time to time.
	"""
	def __init__(self):
		self.url = 'http://www.lazada.sg/brands/'

	def getSource(self):
		""" 
		get the html source code of the webpage
		"""
		html = requests.get(self.url,headers=headers).content
		return html

	def getData(self):
		"""
		parse and retrive brand names from the html source
		"""
		html = self.getSource()
		selector = etree.HTML(html)
		results = selector.xpath('//*[@id=*]/div[2]/div/a/text()')
		results.sort()

		logging.info("Totally find {} brands".format(len(results)))
		self.save(results)

	def save(self, results):
		"""
		save the results to a .txt file
		"""
		filename_save = 'resources/brand.txt'
		if os.path.exists(filename_save):
			os.remove(filename_save)

		f = open(filename_save,'a')
		for item in results:
			if item[0].isalpha() or item[0].isdigit():
				f.write(item+'\n')
		f.close()
		



class ProductBuilder(object):
	"""
	Employ the google product taxonomy to define the product names.
	This implementation is good for naming products cause google search
	engine return results based on this taxonomy.

	The category template can be downloaded from the following link
	https://support.google.com/merchants/answer/6324436?hl=en

	This class takes advantage of the taxonomy-with-ids.en-US.xls to
	generate a product core term list.

	"""
	def __init__(self, data_dir = 'resources/taxonomy-with-ids.en-US.xls'):
		self.data_dir = data_dir

	def getData(self):
		"""
		process the google product taxonomy file to output a product list
		"""
		workbook = xlrd.open_workbook(self.data_dir)
		xl_sheet = workbook.sheet_by_index(0)
		product_names = []
		for row_idx in range(xl_sheet.nrows):
			taxonomy = filter(lambda x: x.value != '', xl_sheet.row(row_idx))[-1].value
			product_names += self.generateProName(taxonomy)

		product_names = list(set(product_names))
		product_names.sort()
		logging.info("Totally find {} brands".format(len(product_names)))
		self.save(product_names)

	def generateProName(self, taxonomy):
		"""
		extract prodcut names from the google product taxonomy name 

		In the taxonomy name, we can find '&'. The words before and after
		'&' are collaterals, thus one taxonomy_name can be divided into two.

		e.g. taxonomy = 'Baby & Toddler Socks' contains two product names:
				'Baby Socks' & 'Toddler Socks'
			taxonomy = 'Baby & Toddler Socks & Tights' contains four product names:
				'Baby Socks' & 'Baby Tights' & 'Toddler Socks' & 'Toddler Tights'
		
		There are at most two '&' in one taxonomy
		
		Some collaterals contain three words
		e.g. taxonomy = 'Food, Beverages & Tobacco' contains three product names:
				'Food', 'Beverages' & 'Tobacco'

		Note that ',' always appears along with one and only one '&' while the other way around does
		not hold.
		"""

		sub_tax1, sub_tax2, sub_tax3, sub_tax4 = None, None, None, None
		product_names = []
		if ',' in taxonomy:
			splitted_tax = taxonomy.split(',')
			fst = splitted_tax[0].split()
			sec = splitted_tax[1].split()
			sub_tax1 = fst+sec[3:]
			sub_tax2 = fst[:-1]+[sec[0]]+sec[3:]
			sub_tax3 = fst[:-1]+sec[2:]
		else:
			splitted_tax = taxonomy.split('&')
			if len(splitted_tax) == 1:
				sub_tax1 = splitted_tax[0].split()
				product_names += self.processTax(sub_tax1)
			elif len(splitted_tax) == 2:
				fst = splitted_tax[0]
				sec = splitted_tax[1]
				sub_tax1 = fst.split()+sec.split()[1:]
				sub_tax2 = fst.split()[:-1]+sec.split()
				product_names += self.processTax(sub_tax1)
				product_names += self.processTax(sub_tax2)
			else:
				fst = splitted_tax[0]
				sec = splitted_tax[1]
				thr = splitted_tax[2]
				sub_tax1 = fst.split()+sec.split()[1:]+thr.split()[1:]
				sub_tax2 = fst.split()+sec.split()[1:-1]+thr.split()
				sub_tax3 = fst.split()[:-1]+sec.split()+thr.split()[1:]
				sub_tax4 = fst.split()[:-1]+sec.split()[:-1]+thr.split()

		if sub_tax1:
			product_names += self.processTax(sub_tax1)
		if sub_tax2:
			product_names += self.processTax(sub_tax2)
		if sub_tax3:
			product_names += self.processTax(sub_tax3)
		if sub_tax4:
			product_names += self.processTax(sub_tax4)

		return list(set(product_names))


	def processTax(self, tax):
		"""
		convert taxonomy name without '&' to product names
		"""
		product_names = []
		product_names.append(tax[-1])
		product_names.append(' '.join(tax[-2:]))
		product_names.append(' '.join(tax[-3:]))

		return list(set(product_names))


	def save(self, results):
		"""
		save the results to a .txt file
		"""
		filename_save = 'resources/product.txt'
		if os.path.exists(filename_save):
			os.remove(filename_save)

		f = open(filename_save,'a')
		for item in results:
			f.write(item+'\n')
		f.close()

if __name__ == '__main__':

	logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

	logging.info('Building brand list')
	brand_list = BrandBuilder()
	brand_list.getData()
	logging.info('Brand name library built')

	logging.info('Building product list')
	product_list = ProductBuilder()
	products = product_list.getData()
	logging.info('Product name library built')	

		


