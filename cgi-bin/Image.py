#!/usr/bin/python

class Image(object):
	def __init__(self, json=None):
		self.imageID        = None
		self.imageIndex     = 0
		self.imageExtention = None
		self.sourceURL      = None
		self.thumbURL       = None
		self.localPath      = None
		self.localThumbPath = None
		self.width   = 0
		self.height  = 0
		self.tWidth  = 0
		self.tHeight = 0
		if json != None:
			self.loadFromJSON(json)
	
	def loadFromJSON(self, json):
		self.imageID        = json.get('imageId',        None)
		self.imageIndex     = json.get('imageIndex',     None)
		self.imageExtension = json.get('imageExtension', None)
		self.sourceURL      = json.get('unescapedUrl',   None)
		self.thumbURL       = json.get('tbUrl',          None)
		self.width          = json.get('width',          None)
		self.height         = json.get('height',         None)
		self.tWidth         = json.get('tbWidth',        None)
		self.tHeight        = json.get('tbHeight',       None)
		self.localPath      = json.get('localPath',      None)
		self.localThumbPath = json.get('localThumbPath', None)
		# Get file extension from URL
		import re
		m = re.search('.*\\.([jpegJPEGpngPNGgifGIF]{3,4}).*', json.get('unescapedUrl'))
		if m != None:
			self.imageExtension = m.group(1).lower()
		else:
			raise Exception('no extension found for ' + json['unescapedUrl'])
		
	def toJSON(self):
		result = self.toDict()
		if self.localPath != None:
			result['localPath'] = self.localPath
		if self.localThumbPath != None:
			result['localThumbPath'] = self.localThumbPath

		from json import dumps
		return dumps(result, indent=2)

	def toDict(self):
		result = {
			'imageId'       : self.imageID,
			'imageIndex'    : self.imageIndex,
			'imageExtesion' : self.imageExtension,
			'unescapedUrl'  : self.sourceURL,
			'tbUrl'         : self.thumbURL,
			'width'         : self.width,
			'height'        : self.height,
			'tbWidth'       : self.tWidth,
			'tbHeight'      : self.tHeight,
			'localPath'     : self.localPath,
			'localThumbPath': self.localThumbPath
		}
		return result