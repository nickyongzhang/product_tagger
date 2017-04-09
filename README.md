Product Tagger
================

Introduction
------------

The project aims at findng core terms, brand, and descriptions from a product title from e-commerce websites.

The e-commerce product title lacks grammatical structure and can be hardly processed using context information. One characteristic of e-commerce product titles is that they are usually short. Therefore, I come up with the Look up tagger approach to ahieve the objective.

The steps are as follows:

1.  Construct a brand name library and a product name library. Please refer to `library_builder.py`.
2.  Build a tag table using the product name library and brand name library. Please refer to `tagTable_builder.py`.
3.  Build a lookup tagger using \`nltk.UnigramTagger' with the built tag table.
4.  After processing each product title, generate unit-, bi-, and tri-grams. A lot of product and brand names contain ngrams.
5.  Look up trigrams first, and then bigrams, and at last unigrams. Trigrams are taken with highest priority and unigrams the lowest.
6.  If no product name is found in the product title after all the lookup procedure, extract the last alpha noun in the title as the product name. If no brand name is found, leave it empty.
7.  As the product title itself is very short, we assume all the information in it is useful. Then all the other words are descriptive information.

> Example: product title: 'Makibes Unisex Red LED Digital Band Wrist Watch')

      product core term:  'watch'
      product brand name: 'makibes'
      Descriptions: 'unisex red led digital band wrist'

Installation
------------

    $ pip install product_tagger

or

Clone this directory

Usage
-----

If install using pip:

    $ python
    >>> from product_tagger import product_tagger
    >>> product_tagger.tag_product('Makibes Unisex Red LED Digital Band Wrist Watch')
    (u'watch', u'makibes', u'unisex red led digital band wrist')

The tagger can also be called in a shell. After cloning the repository:

    $ cd product_tagger
    $ python product_tagger.py 'Makibes Unisex Red LED Digital Band Wrist Watch'
    ===========
    ('Core term: ', u'watch')
    ('Brand: ', u'makibes')
    ('Discriptions: ', u'unisex red led digital band wrist')

Project Details
---------------

The data file 'Product Data.xlsx' is proved by Shopee. Project results from the input file can be found in the folder `/results`.

The folder `/resources` contain the tagger lookup table `tagTable.pkl` together with all the files used to generate the table.

Future Work
-----------

The lookup tagging method is used in this project.

When having collected enough training data, machine learning models like HMM and CRF can be used. Actually, the lookup tagging method can be used to generate training data but manual inspection is still needed.

Requirements
------------

-   Python &gt;=2.7 or &gt;=3.3
-   nltk &gt;=3.2.1
-   requests &gt;= 2.8.1
-   lxml
-   xlrd

License
-------

Refer to LICENSE
