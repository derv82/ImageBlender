#!/usr/bin/python

class ImageResponse(object):
	def __init__(self):
		self.images = []
		self.exhausted = False
		self.error = None
		self.retryableError = True
