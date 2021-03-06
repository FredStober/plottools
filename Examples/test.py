#!/usr/bin/env python
import math, numpy, sys, os, random
sys.path.append(os.path.normpath(os.path.join(os.path.dirname(os.path.join(os.getcwd(), __file__)), '../..')))
random.seed(123)

import matplotlib
matplotlib.rc('text', usetex = True)
matplotlib.use('agg')
from plottools import P, doPlot, doCMSPlot

def getData():
	x = numpy.array(range(-20, 20, 1))
	xe = numpy.ones(x.shape)*0.5
	p = numpy.array(map(lambda x: random.random(), range(10)))
	pr = numpy.ones(p.shape)
	pr[0:4] = numpy.array([2, 0.05, 0.01, 1e-3])
	p = pr * p - pr / 2
	y = numpy.array(map(lambda x: p[0], x))
	y += numpy.array(map(lambda x: p[1]*x, x))
	y += numpy.array(map(lambda x: p[2]*x*x, x))
	y += numpy.array(map(lambda x: p[3]*x*x*x, x))
#	y = numpy.array(map(lambda x: p[0] * (x-p[1])*(x-p[2])*(x-p[3]), x))
	print y
#	y = (2-random.random()) / (1 + y*y)
#	print y
	pe = numpy.array(map(lambda x: random.random(), range(10)))
	ye_up = numpy.array(map(lambda x: 0.3/(0.01*(x-5)**2+1.)+0.05, x)) * y + 0.1
	ye_down = numpy.array(map(lambda x: 0.3/(0.01*(x+5)**2+1.)+0.05, x)) * y + 0.1
	ye = numpy.array([ye_up, ye_down]) # +/- error
	return {'x': x, 'xe': xe, 'y': y, 'ye': ye}


if False:
	doCMSPlot(os.path.basename(sys.argv[0]).split('.')[0], {'width': 5, 'square': True, 'xpad': 5, 'ypad': 10,
		'xrange': ( -20, 20), 'xlabel': '$Q$ [GeV]',
		'yrange': (-4, 2), 'ylabel': r'$\alpha_s(Q)$',
		'legend': {'cols': 2, 'loc': 2},
		'legend_test': {'cols': 1, 'loc': 8, 'size': 8, 'markerscale': 1.2},
	}, [
		P(data = getData(), style = 'errorbar', label = 'Errorbar1', legend = 'test'),
		P(data = getData(), style = 'errorbar', color = '#ff3451', fmt = '#s',
			markeredgewidth = 1, label = 'Errorbar2'),
		P(data = getData(), style = 'errorbar', color = '#1235ff', fmt = '#D',
			markersize = 3, markevery = 2, label = 'Errorbar3'),

		P(label = 'Pad Entry 1'),

		P(data = getData(), style = 'lines', color = 'r', fmt = '-.', legend = 'test',
			linewidth = 2, label = 'Lines1'),
		P(data = getData(), style = 'lines', color = '#23ff74', fmt = '--o', label = 'Lines2'),

		P(data = getData(), style = 'band', color = 'g', fmt = '', alpha = 0.4,
			linewidth = 2, label = 'Band1', hatch = 'xxxx'),
		P(data = getData(), style = 'band', color = 'b', alpha = 0.4, legend = 'test',
			linewidth = 2, label = 'Band2', hatch = 'o', steps = True),

		P(data = getData(), style = 'bar', color = 'y', alpha = 0.4, label = 'Bar1', hatch = 'o'),

		P(data = getData(), style = 'outline', color = 'r', fmt = ':',
			linewidth = 2, label = 'Outline1'),

		P(data = getData(), style = 'bandline', color = 'm', fmt = '-.', dashes = [2,5,7,2], alpha = 0.5,
			linewidth = 2, label = 'Bandline1', hatch = '////'),
		P(label = 'Pad Entry 2'),
	])

data_1 = {
	'x': numpy.array([1, 2, 4]), 'xe': numpy.array([[0.25, 0.5, 0.5], [0.5, 0.25, 0.5]]),
	'y': numpy.array([-2, 4, 6]), 'ye': numpy.array([[1, 2, 2], [0.5, 1, 3]]),
}
print data_1

doCMSPlot(os.path.basename(sys.argv[0]).split('.')[0] + '_1', {'width': 5, 'square': True, 'xpad': 5, 'ypad': 10,
		'xrange': (-1, 5), 'xlabel': '$Q$ [GeV]',
		'yrange': (-5, 10), 'ylabel': r'$\alpha_s(Q)$',
		'legend': {'cols': 1, 'loc': 7}, 'grid': True, 'notesize': 8,
		'notes': ['0,0.2,%r' % list(data_1['x']), '0,0.15,%r' % list(data_1['xe']), '0,0.1,%r' % data_1['y'], '0,0.05,%r' % list(data_1['ye'])],
	}, [
		P(data = data_1, style = 'errorband', label = 'Errorband1', color = 'r', alpha = 0.4, steps = True),
		P(data = data_1, style = 'errorband', label = 'Errorband2', color = 'b', alpha = 0.4, steps = True, band_connected = False),
	]
)

data_1 = {
	'x': numpy.array([0, 2, 3, 4, 5]), 'xe': numpy.array([[1, 0.5, 0.5, 1, 0.25], [0.5, 1, 0.5, 0, 0.25]]),
	'y': numpy.array([5, 0, -1, 3, 2]), 'ye': numpy.array([[1, 2, 1, 3, 1], [2, 2, 2, 2, 1]]),
}
print data_1

doCMSPlot(os.path.basename(sys.argv[0]).split('.')[0] + '_2', {'width': 5, 'square': True, 'xpad': 5, 'ypad': 10,
		'xrange': (-1, 6), 'xlabel': '$Q$ [GeV]',
		'yrange': (-5, 10), 'ylabel': r'$\alpha_s(Q)$',
		'legend': {'cols': 1, 'loc': 7}, 'grid': True, 'notesize': 8,
		'notes': ['0,0.2,%r' % list(data_1['x']), '0,0.15,%r' % list(data_1['xe']), '0,0.1,%r' % data_1['y'], '0,0.05,%r' % list(data_1['ye'])],
	}, [
#		P(data = data_1, style = 'errorbar', label = 'Errorbar', color = 'r', linewidth = 4, fmt='-'),
#		P(data = data_1, style = 'lines', label = 'Lines', color = 'b', linewidth = 2),
		P(data = data_1, style = 'lines', label = 'None', color = 'y', steps = True, fmt = '-^', markersize=4, connected = None),
		P(data = data_1, style = 'lines', label = 'True', color = 'r', steps = True, fmt = '--s', markersize=4, connected = True),
		P(data = data_1, style = 'lines', label = 'False', color = 'b', steps = True, fmt = '-.o', markersize=4, connected = False),
	]
)

doCMSPlot(os.path.basename(sys.argv[0]).split('.')[0] + '_3', {'width': 5, 'square': True, 'xpad': 5, 'ypad': 10,
		'xrange': (-1, 6), 'xlabel': '$Q$ [GeV]',
		'yrange': (-5, 10), 'ylabel': r'$\alpha_s(Q)$',
		'legend': {'cols': 1, 'loc': 7}, 'grid': True, 'notesize': 8,
		'notes': ['0,0.2,%r' % list(data_1['x']), '0,0.15,%r' % list(data_1['xe']), '0,0.1,%r' % data_1['y'], '0,0.05,%r' % list(data_1['ye'])],
	}, [
		P(data = data_1, steps = True, style = 'errorband', fmt = 'o', color = 'k',
			band_color = '#555555', band_alpha = 0.5, band_fmt = '-'),
	]
)
