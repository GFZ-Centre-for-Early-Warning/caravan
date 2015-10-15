import codecs, datetime, sys
import xml.sax.handler

import datetime

#define some filters
def lat(value, prec = '.2f'):
	prec = '%' + prec
	v = float(value)
	if v < 0:
		return prec % abs(v) + '&deg; S'
	else:
		return prec % v + '&deg; N'


def lon(value, prec = '.2f'):
	prec = '%' + prec
	v = float(value)
	if v < 0:
		return prec % abs(v) + '&deg; W'
	else:
		return prec % v + '&deg; E'


def qmldate(value):
	return datetime.datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%fZ')

def dbdate(value):
	try:
		return datetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%S.%f')
	except:
		return datetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%S')


def deg2km(value):
	return float(value) * 111.1329149013519096


def date(value, format = '%Y-%m-%d %H:%M:%S'):
	return datetime.datetime.strftime(value, format)



class Reader():
	def xml2obj(self, src):
		"""
		A simple function to converts XML data into native Python object.
		"""

		class DataNode(object):
			def __init__(self):
				self._attrs = {}    # XML attributes and child elements
				self.data = None    # child text data

			def __len__(self):
				# treat single element as a list of 1
				return 1

			def __getitem__(self, key):
				if isinstance(key, basestring):
					return self._attrs.get(key,None)
				else:
					return [self][key]

			def __contains__(self, name):
				return self._attrs.has_key(name)

			def __nonzero__(self):
				return bool(self._attrs or self.data)

			def __getattr__(self, name):
				if name.startswith('__'):
					# need to do this for Python special methods???
					raise AttributeError(name)
				return self._attrs.get(name,None)

			def _add_xml_attr(self, name, value):
				if name in self._attrs:
						# multiple attribute of the same name are represented by a list
						children = self._attrs[name]
						if not isinstance(children, list):
							children = [children]
							self._attrs[name] = children
						children.append(value)
				else:
					self._attrs[name] = value

			def __str__(self):
				return self.data or ''

			def __repr__(self):
				items = sorted(self._attrs.items())
				if self.data:
					items.append(('data', self.data))
				return u'{%s}' % ', '.join([u'%s:%s' % (k,repr(v)) for k,v in items])

		class TreeBuilder(xml.sax.handler.ContentHandler):
			def __init__(self):
				self.stack = []
				self.root = DataNode()
				self.current = self.root
				self.text_parts = []
				self.publicObjects = {}

			def startElement(self, name, attrs):
				self.stack.append((self.current, self.text_parts))
				self.current = DataNode()
				self.text_parts = []
				# xml attributes --> python attributes
				for k, v in attrs.items():
					# Register PublicObject in lookup map
					if k == "publicID":
						self.publicObjects[v] = self.current
					self.current._add_xml_attr(k, v)

			def endElement(self, name):
				text = ''.join(self.text_parts).strip()
				if text:
					self.current.data = text
				if self.current._attrs:
					obj = self.current
				else:
					# a text only node is simply represented by the string
					obj = text or ''
					# try to store the object as float if possible
					try: obj = float(obj)
					except: pass
				self.current, self.text_parts = self.stack.pop()
				self.current._add_xml_attr(name, obj)

			def characters(self, content):
				self.text_parts.append(content)

		builder = TreeBuilder()
		if isinstance(src,basestring):
			xml.sax.parseString(src, builder)
		else:
			xml.sax.parse(src, builder)
		return builder


	def createContext(self, src):
		sys.stderr.write("Parsing XML ... ")
		sys.stderr.flush()
		obj = self.xml2obj(src)
		sys.stderr.write("done\n")

		if not obj:
			raise Exception('No content')

		sc = obj.root.seiscomp
		if not sc:
			raise Exception("Invalid root tag, expected 'seiscomp'")

		ep = sc.EventParameters
		if not ep:
			raise Exception("No EventParameters found")

		if len(ep.event) == 0:
			raise Exception("No event found")

		if len(ep.event) > 1:
			raise Exception("Multiple events found, not supported")

		evt = ep.event[0]
		if not evt.publicID:
			raise Exception("No eventID set")

		org = obj.publicObjects.get(evt.preferredOriginID)
		if not org:
			raise Exception("Preferred origin not found")

		if evt.preferredMagnitudeID:
			mag = obj.publicObjects.get(evt.preferredMagnitudeID)
			if not mag:
				seiscomp3.Logging.warning("Preferred magnitude not found")
		else:
			mag = None

		if evt.preferredFocalMechanismID:
			fm = obj.publicObjects.get(evt.preferredFocalMechanismID)
		else:
			fm = None

		if evt.description:
			for d in evt.description:
				if d.type == "region name":
					evt.region = d.text
					break

		ctx = {}

		ctx['EventLocationName'] = evt.region
		ctx['Time'] = date(qmldate(org.time.value))
		ctx['Latitude'] = org.latitude.value
		ctx['Longitude'] = org.longitude.value
 		ctx['Depth'] = "%.0f" % float(org.depth.value)
		ctx['Magnitude'] = "%.1f" % float(mag.magnitude.value)
		ctx['EventId'] = evt.publicID

		return ctx
