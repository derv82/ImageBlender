#!/usr/bin/python

from cgi   import FieldStorage
from cgitb import enable as cgi_enable; cgi_enable()
from os    import environ
from json  import dumps, JSONEncoder
from traceback import format_exc
from Image import Image

class API(object):
	@staticmethod
	def main():
		keys = API.getKeys()

		if not 'method' in keys:
			raise Exception('required "method" not found in keys')

		method = keys.get('method')
		if method == 'getImages':
			return API.getImages(keys)
		elif method == 'getSearchTerms':
			pass
		return None

	@staticmethod
	def getImages(keys):
		if not 'search_term' in keys or \
		   not 'search_index' in keys:
			raise Exception('required "search_term" and "search_index" not provided')
		
		search_term  = keys.get('search_term')
		search_index = keys.get('search_index')
		if not search_index.isdigit():
			raise Exception('search_index is not numeric: %s' % search_index)
		search_index = int(search_index)

		from Query import Query
		images = Query.getMoreImages(search_term, search_index)

		return images

	@staticmethod
	def getKeys():
		''' Get dict of keys/values passed in query string '''
		from urllib import unquote
		form = FieldStorage()
		keys = {}
		for key in form.keys():
			if form[key].value != 'undefined':
				keys[key] = unquote(form[key].value)
		return keys

	@staticmethod
	def get_cookies():
		''' Get dict of keys/values passed in cookie '''
		if not 'HTTP_COOKIE' in environ: return {}
		cookies = {}
		txt = environ['HTTP_COOKIE']
		for line in txt.split(';'):
			if not '=' in line: continue
			pairs = line.strip().split('=')
			cookies[pairs[0]] = pairs[1]
		return cookies

class ImageEncoder(JSONEncoder):
    def default(self, obj):
    	if isinstance(obj, Image):
            return obj.toDict()

        return json.JSONEncoder.default(self, obj)

if __name__ == '__main__':
	print 'Content-Type: application/json'
	print ''

	try:
		images = API.main()
		response = {
			'images' : images
		}
		print dumps(response, indent=2, cls=ImageEncoder)
	except Exception, e:
		response = {
			'error' : 'error occurred',
			'trace' : format_exc()
		}
		print dumps(response, indent=2)
		
		from sys import stderr
		stderr.write('%s\n' % format_exc())
	print "\n\n"
	