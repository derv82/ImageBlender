#!/usr/bin/python

class Query(object):

	@staticmethod
	def getMoreImages(search_term, search_index):
		from os import environ
		ipAddress = environ.get('REMOTE_ADDR', '127.0.0.1')

		from ImageResponse import ImageResponse
		from FS import FS
		# Load images from disk if we've already retrieved them
		response = FS.getStoredImages(search_term, search_index)
		if len(response.images) > 0:
			# Return 'em if we got 'em
			return response

		# Fetch new images
		from Google import Google
		response = Google.searchImages(search_term,
		                             search_index, 
		                             source_ip = ipAddress,
		                             safe = "off")

		if response.error != None:
			# No error
			return response

		directory = FS.getImageDir(search_term)
		FS.saveSummaryOfImages(response.images, 
			                directory,
			                response.exhausted,
			                search_index + FS.BATCH_SIZE)

		for image in response.images:
			# Save image info to filesystem in separate file
			FS.saveImageToFile(image, directory)

		return response


if __name__ == '__main__':
	images = Query.getMoreImages('butterflies', 0)
	for image in images:
		print image.toJSON()

