#!/usr/bin/python

class Google(object):
	
	BATCH_SIZE = 4

	@staticmethod
	def searchImages(unfiltered_search_text, start_index, source_ip='127.0.0.1', safe='off'):
		search_text = unfiltered_search_text.replace(' ', '%20')

		url = 'https://ajax.googleapis.com/ajax/services/search/images?v=1.0'
		url +=      '&q=%s' % search_text.replace(' ', '%20')
		url +=  '&start=%d' % start_index
		url += '&userip=%s' % source_ip
		url +=   '&safe=%s' % safe

		from Httpy import Httpy
		httpy = Httpy()
		try:
			response = httpy.get(url)
		except Exception, e:
			raise e

		from json import loads
		json = loads(response)

		# TODO Check for rate limit
		'''{
			"responseData": null,
			"responseDetails": "qps rate exceeded",
			"responseStatus": 503
		}'''

		if 'responseData' not in json or \
		   json['responseData'] == None or \
			 'results' not in json['responseData']:
			raise Exception(
				'invalid response from google while searching "%s":\n%s'
				% (search_text, response))

		from Image import Image
		images = []
		for (current_index, json_image) in enumerate(json['responseData']['results']):
			imageUrl = json_image['unescapedUrl']
			meta = httpy.get_meta(imageUrl, timeout=5)
			if 'Content-type' not in meta or 'image' not in meta['Content-Type']:
				# Image is not an image.
				continue
			try:
				image = Image(json=json_image)
				image.imageIndex = start_index + current_index + 1
				images.append(image)
			except Exception, e:
				# Don't fail completely when deserializing single images
				pass
		return images

if __name__ == '__main__':
	images = Google.searchImages("butterfly", 0)
	for image in images:
		print image.toJSON()
	from FS import FS
	FS.saveImagesToFile(images, 'butterfly', len(images))
