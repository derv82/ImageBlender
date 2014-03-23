#!/usr/bin/python

class Query(object):

	@staticmethod
	def getMoreImages(search_term, search_index):
		from os import environ
		ipAddress = environ.get('REMOTE_ADDR', '127.0.0.1')

		from FS import FS
		# Load images from disk if we've already retrieved them
		images = FS.getStoredImages(search_term, search_index)
		if len(images) > 0:
			# Return 'em if we got 'em
			return images

		# Fetch new images
		from Google import Google
		images = Google.searchImages(search_term,
		                             search_index, 
		                             source_ip = ipAddress,
		                             safe = "off")

		FS.saveImagesToFile(images, 
			                FS.getImageDir(search_term),
			                search_index + FS.BATCH_SIZE)

		return images


if __name__ == '__main__':
	images = Query.getMoreImages('butterflies', 0)
	for image in images:
		print image.toJSON()

