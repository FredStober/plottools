import numpy, matplotlib

def hsv2rgb(h, s = 1, v = 1):
	return tuple(matplotlib.colors.hsv_to_rgb(numpy.array([[(h, s, v)]]))[0][0])

getRX = lambda data, apad = 0, rpad = 1: (rpad*min(data['x'])-apad, rpad*max(data['x'])+apad)
getRY = lambda data, apad = 0, rpad = 1: ((1-rpad)*min(data['y'])-apad, (1+rpad)*max(data['y'])+apad)
