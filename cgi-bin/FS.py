#!/usr/bin/python

class FS(object):
	'''
		Filesystem class, for interacting with the filesystem.
	'''
	BATCH_SIZE = 4

	@staticmethod
	def getImageDir(search_term=''):
		from os import path, mkdir
		directory = path.join('..', 'images', search_term)
		if not path.exists(directory):
			mkdir(directory)
		return directory

	@staticmethod
	def getStoredImages(search_term, start_index):
		'''
			Args:
				search_term
				start_index

			Returns:
				List of Image objects containing image info

			Raise:
				Exception when there are no images and we should not fetch more
		'''
		from os import path
		directory = FS.getImageDir(search_term)

		from ImageResponse import ImageResponse		
		response = ImageResponse()

		allFilePath = path.join(directory, "all.json")
		if not path.exists(allFilePath):
			# Search term hasn't had any results yet
			return response # return empty response

		allContents = FS.getAllJSON(allFilePath)
		jsonFiles      = allContents.get('jsonFiles', [])
		nextImageIndex = allContents.get('nextImageIndex', 0)
		exhausted      = allContents.get('exhausted', False)

		# Check if there are more images requested than we have
		if start_index + FS.BATCH_SIZE >= len(jsonFiles) and exhausted:
			# Raise exception if we should not fetch more images
			response.exhausted = True
			response.error = "No more images found"
			response.retryableError = False
			return response

		images = []
		for jsonFile in jsonFiles[start_index:start_index + FS.BATCH_SIZE]:
			jsonFilePath = path.join(directory, jsonFile)
			images.append(FS.getImageFromFile(jsonFilePath))

		response.images = images
		response.exhausted = exhausted
		return response

	@staticmethod
	def getAllJSON(allFilePath):
		f = open(allFilePath, 'r')
		allJSON = f.read()
		f.close()

		from json import loads
		return loads(allJSON)

	@staticmethod
	def getImageFromFile(jsonFile):
		f = open(jsonFile, 'r')
		jsonImageText = f.read()
		f.close()

		from json import loads
		jsonImage = loads(jsonImageText)

		from Image import Image
		return Image(json=jsonImage)

	@staticmethod
	def saveSummaryOfImages(images, directory, exhausted, next_image_index):
		'''
			Appends to the summary of the images to the "all.json" file
			located in the given directory.

			Sample:
			directory/all.json:
			{
				"jsonFiles" : ["<imgid>.json", "<imgid>.json"],
				"exhausted" : true,
				"nextImageIndex" : 40,
			}
		'''
		from json import loads, dumps
		from os import path, mkdir

		if not path.exists(directory):
			mkdir(directory)

		allJsonPath = path.join(directory, 'all.json')
		if path.exists(allJsonPath):
			f = open(allJsonPath, 'r')
			allJsonText = f.read()
			f.close()
			allJson = loads(allJsonText)
		else:
			allJson = {
				'jsonFiles' : [],
				'exhausted' : False,
				'nextImageIndex' : 0,
			}

		for image in images:
			# Add image to list of all images
			allJson['jsonFiles'].append("%s.json" % image.imageID)
		allJson['nextImageIndex'] = next_image_index

		# Persist to filesystem
		f = open(allJsonPath, 'w')
		f.write(dumps(allJson, indent=2))
		f.close()

	@staticmethod
	def saveImageToFile(image, directory):
		from os import path
		save_path = path.join(directory, '%s.json' % image.imageID)
		f = open(save_path, 'w')
		f.write(image.toJSON())
		f.close()

	@staticmethod
	def recordSearchTerm(term):
		from os import path
		from json import loads, dumps
		terms_path = path.join(FS.getImageDir(), 'all.json')
		if path.exists(terms_path):
			f = open(terms_path, 'r')
			jsonText = f.read()
			f.close()

			result = loads(jsonText)
			if term.lower().strip() not in result['terms']:
				result['terms'].append(term.lower().strip())
		else:
			result = {
				'terms' : [term]
			}

		f = open(terms_path, 'w')
		f.write(dumps(result, indent=2))
		f.close()

	@staticmethod
	def getSearchTerms(start, count):
		from os import path
		terms_path = path.join(FS.getImageDir(), 'all.json')
		if path.exists(terms_path):
			f = open(terms_path, 'r')
			jsonText = f.read()
			f.close()

			from json import loads
			result = loads(jsonText)
			count = min(len(result['terms']), count)
			result['terms'] = result['terms'][start:count]
		else:
			result = {
				'terms' : []
			}
		return result

if __name__ == '__main__':
	'''
	image = FS.getImageFromFile('butterflies/1.json')
	print image.toJSON()
	'''
	response = FS.getStoredImages('butterflies', 0)
	for image in response.images:
		print image.toJSON()
