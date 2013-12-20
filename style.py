import numpy, matplotlib

def hsv2rgb(h, s = 1, v = 1):
	return tuple(matplotlib.colors.hsv_to_rgb(numpy.array([[(h, s, v)]]))[0][0])
