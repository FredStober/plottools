#!/usr/bin/env python

import numpy, math

class DataHolder:
	def __init__(self, metadata = {}):
		self.x = []
		self.xe = []
		self.xea = []
		self.y = []
		self.ye = []
		self.yea = []
		self.meta = dict(metadata)

	def append(self, x, y, ye = 0, xe = 0):
		def do_append(array_e, array_ea, e):
			tmp = numpy.array(e)
			if tmp.ndim == 0:
				array_e.append(tmp)
				array_ea.append([tmp, tmp])
			elif tmp.ndim == 1:
				assert(len(tmp) == 2)
				array_e.append((tmp[0] + tmp[1]) / 2.0)
				array_ea.append(tmp)

		self.x.append(x)
		do_append(self.xe, self.xea, xe)
		self.y.append(y)
		do_append(self.ye, self.yea, ye)

	def get(self, var = None):
		def unpack_err(arr):
			(high, low) = ([], [])
			for e_high, e_low in arr:
				high.append(e_high)
				low.append(e_low)
			return numpy.array([high, low])
		if var == 'x':
			return numpy.array(self.x)
		elif var == 'xe':
			return numpy.array(self.xe)
		elif var == 'xea':
			return unpack_err(self.xea)
		elif var == 'xea_packed':
			return numpy.array(self.xea)
		elif var == 'y':
			return numpy.array(self.y)
		elif var == 'ye':
			return numpy.array(self.ye)
		elif var == 'yea':
			return unpack_err(self.yea)
		elif var == 'yea_packed':
			return numpy.array(self.yea)
		else:
			result = dict(self.meta)
			result.update({'x': self.get('x'), 'xe': self.get('xe'), 'xea': self.get('xea'),
				'y': self.get('y'), 'ye': self.get('ye'), 'yea': self.get('yea')})
			return result
