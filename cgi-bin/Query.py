#!/usr/bin/python

from os import environ
from ImageResponse import ImageResponse
from FS import FS
from Google import Google

class Query(object):

	@staticmethod
	def getMoreImages(search_term, search_index):
		ipAddress = environ.get('REMOTE_ADDR', '127.0.0.1')

		# Add search term to list
		FS.recordSearchTerm(search_term)

		# Load images from disk if we've already retrieved them
		response = FS.getStoredImages(search_term, search_index)
		if len(response.images) > 0:
			# Return 'em if we got 'em
			return response

		# Fetch new images
		response = Google.searchImages(search_term,
		                             search_index, 
		                             source_ip = ipAddress,
		                             safe = "off")

		if response.error != None:
			return response # No error

		directory = FS.getImageDir(search_term)

		# Add images to summary
		FS.saveSummaryOfImages(response.images, 
			                directory,
			                response.exhausted,
			                search_index + FS.BATCH_SIZE)

		# Save image info in separate files
		for image in response.images:
			FS.saveImageToFile(image, directory)

		return response

if __name__ == '__main__':
	images = Query.getMoreImages('butterflies', 0)
	for image in images:
		print image.toJSON()

