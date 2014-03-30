#!/usr/bin/python

from cgi   import FieldStorage
from cgitb import enable as cgi_enable; cgi_enable()
from os    import environ, remove, path
from json  import dumps, JSONEncoder
from traceback import format_exc
from Image import Image
from FS import FS

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
			return API.getSearchTerms(keys)

		elif method == 'saveBlendedImage':
			return API.saveBlendedImage(keys)

		elif method == 'downloadImage':
			return API.downloadImage(keys)

		raise Exception('method not found: %s' % method)


	@staticmethod
	def getImages(keys):
		if not 'search_term' in keys or \
		   not 'search_index' in keys:
			raise Exception('required "search_term" and "search_index" not provided')
		
		search_term  = keys.get('search_term')
		search_term = API.sanitizeTerm(search_term)

		search_index = keys.get('search_index')
		if not search_index.isdigit():
			raise Exception('search_index is not numeric: %s' % search_index)
		search_index = int(search_index)

		from ImageResponse import ImageResponse
		from Query import Query
		response = Query.getMoreImages(search_term, search_index)

		result = {
			'images'    : response.images,
			'exhausted' : response.exhausted
		}
		if response.error != None:
			result['error'] = response.error
			result['retryableError'] = response.retryableError
		return result

	@staticmethod
	def getSearchTerms(keys):
		start = int(keys.get('start', '0'))
		count = int(keys.get('count', '0'))
		return FS.getSearchTerms(start=start, count=count)

	@staticmethod
	def downloadImage(keys):
		if 'url'        not in keys: raise Exception('url required')
		if 'searchTerm' not in keys: raise Exception('searchTerm required')
		if 'imageID'    not in keys: raise Exception('imageID required')
		if 'imageIndex' not in keys: raise Exception('imageIndex required')

		url = keys.get('url')
		searchTerm  = keys.get('searchTerm')
		sanitizedSearchTerm = API.sanitizeTerm(searchTerm)
		imageID = keys.get('imageID')
		imageIndex = keys.get('imageIndex')
		
		import re
		m = re.search('\\.(jpg|jpeg|png|gif|JPG|JPEG|PNG|GIF)', url)
		if m == None:
			raise Exception('image does not contain an image extension')
		saveAsName = '%s.%s' % (imageID, m.group(1))
		saveAsDir  = FS.getImageDir(search_term=searchTerm)
		saveAsFile = path.join(saveAsDir, saveAsName)

		from Httpy import Httpy
		httpy = Httpy()
		try:
			metadata = httpy.get_meta(url, timeout=2, raise_exception=True)
			if 'Content-Type' not in metadata or 'image' not in metadata['Content-Type']:
				raise Exception('Image at %s is not an image: %s' \
					% (url, metadata.get('Content-Type', 'none')))
			success = httpy.download(url, saveAsFile, timeout=10, raise_exception=True)
			if not success:
				remove(saveAsFile) # Delete file
				raise Exception('Failed to download file.')
		except Exception, e:
			if path.exists(saveAsFile):
				remove(saveAsFile)
			raise e

		localImagePath = path.join('images', searchTerm, saveAsName)
		jsonImageFile = path.join(saveAsDir, '%s.json' % imageID)
		# Save new image path to json file
		f = open(jsonImageFile, 'r')
		jsonText = f.read()
		f.close()

		from json import loads, dumps
		json = loads(jsonText)
		json['localPath'] = localImagePath

		f = open(jsonImageFile, 'w')
		f.write(dumps(json, indent=2))
		f.close()

		return {
			'url' : localImagePath,
			'imageID' : imageID
		}

	@staticmethod
	def saveBlendedImage(keys):
		searchTerm = API.sanitizeTerm(keys.get('searchTerm'))
		imageCount = keys.get('getVisibleImageCount')
		imageData = keys.get('imageData')
		extension = keys.get('extension')

		import time
		timestamp = int(time.time())

		savePath = 'blends/%s-%d.%s' \
				% (searchTerm, timestamp, extension)
		
		import re
		m = re.search('data:.*,.*', imageData)
		if m == None:
			raise Exception('imageData must be in format data:image/<type>,<base64>, got: ' + imageData)

		# Borrowed from http://stackoverflow.com/questions/19579078/kineticjs-todataurl-gives-incorrect-padding-error-in-python
		params,data = imageData.split(',')
		params = params.split(';')
		if 'base64' in params:
			data = data.decode('base64')
		for param in params:
			if param.startswith('charset='):
				data = unquote(data).decode(param.split('=', 1)[-1])

		f = open(path.join('..', savePath), 'w')
		f.write(data)
		f.close()

		return {
			'savePath' : savePath
		}

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
	def sanitizeTerm(term):
		valid_chars = ' -.,"\'abcdefghijklmnopqrstuvwxyz1234567890'
		sanitized = ''.join(c for c in term if c.lower() in valid_chars)
		sanitized = sanitized.replace(' ', '%20')
		return sanitized

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
		response = API.main()
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
	