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
		try:
			json = loads(response)
		except Exception, e:
			raise Exception("Got %s while loading more images" % e.message)

		from ImageResponse import ImageResponse
		response = ImageResponse()

		if not 'responseStatus' in json:
			response.error = 'no response status while searching "%s":\n%s' \
				% (search_text, response)
			response.retryableError = False
			return response

		if 'responseStatus' in json and \
		   json['responseStatus'] != 200:
			if json['responseStatus'] == 400:
				# "out of range start"
				# Exhausted=true
				response.exhausted = True
				response.error = "No more images found"
				response.retryableError = False
				return response
			elif json['responseStatus'] == 503:
				# Retryable.
				response.error = 'Received responseStatus %d while searching "%s":\n%s' \
					% (json['responseStatus'], search_text, json['responseDetails'])
				response.retryableError = True
				return response

		if 'results' not in json['responseData']:
			response.error = 'invalid response from google while searching "%s":\n%s' \
				% (search_text, response)
			response.retryableError = False
			return response

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
		response.images = images
		return response

if __name__ == '__main__':
	response = Google.searchImages("butterfly", 0)
	for image in response.images:
		print image.toJSON()
	from FS import FS
	FS.saveSummaryOfImages(response.images, 'butterfly', response.exhausted, len(response.images))
