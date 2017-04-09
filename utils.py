# ! /usr/local/bin python
# -*- coding:utf-8 -*-

'''
Builders for product brands and product names

@author = Yong Zhang
@email = yzhang067@e.ntu.edu.sg

'''

import re
import unicodedata
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

def remove_punct(string):
	"""
	I assume that all punctuations except \:, \. and \' should 
	be removed from a brand or product name.
	"""
	string = string.lower()
	string = deaccent(string)
	string = re.sub(r"[^a-zA-Z0-9:\.\']", ' ', string)
	return ' '.join(string.split())

def deaccent(text):
    """
    Remove accentuation from the given string. 
    Return input string with accents removed, as unicode.

    >>> deaccent("Böker")
    u'boker'

    """
    if not isinstance(text, unicode):
        # assume utf8 for byte strings, use default (strict) error handling
        text = text.decode('utf8')
    norm = unicodedata.normalize("NFD", text)
    result = ''.join(ch for ch in norm if unicodedata.category(ch) != 'Mn')

    return unicodedata.normalize("NFC", to_unicode(result))

def to_unicode(text, encoding='utf8', errors='strict'):
    """Convert a string (bytestring in `encoding` or unicode), to unicode."""
    if isinstance(text, unicode):
        return text
    return unicode(text, encoding, errors=errors)

