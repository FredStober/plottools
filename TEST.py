#!/usr/bin/env python
import math, numpy, sys, os, random
sys.path.append(os.path.normpath(os.path.join(os.path.dirname(os.path.join(os.getcwd(), __file__)), '..')))
random.seed(123)

from plottools import P, doPlot

def getData():
	x = numpy.array(range(-20, 20, 1))
	xe = numpy.ones(x.shape)*0.5
	p = numpy.array(map(lambda x: random.random(), range(10)))
	pr = numpy.ones(p.shape)
	pr[0:4] = numpy.array([0.05, 40, 40, 40])
	p = pr * p - pr / 2
	y = numpy.array(map(lambda x: p[0]*(x-p[1])*(x-p[2])*(x-p[3]), x))
	pe = numpy.array(map(lambda x: random.random(), range(10)))
	ye_up = numpy.array(map(lambda x: 0.3/(0.01*(x-5)**2+1.)+0.1, x)) * y
	ye_down = numpy.array(map(lambda x: 0.3/(0.01*(x+5)**2+1.)+0.1, x)) * y
	ye = numpy.array([ye_up, ye_down]) # +/- error
	return {'x': x, 'xe': xe, 'y': y, 'ye': ye}


doPlot(os.path.basename(sys.argv[0]).split('.')[0], {
		'xrange': ( -20, 20), 'xlabel': '$Q$ [GeV]',
		'yrange': (-200, 50), 'ylabel': r'$\alpha_s(Q)$',
		'legend': {'cols': 2, 'loc': 2},
		'legend_test': {'cols': 1, 'loc': 8},
	}, [
		P(data = getData(), style = 'errorbar', label = 'Errorbar1', legend = 'test'),
		P(data = getData(), style = 'errorbar', color = '#ff3451', fmt = '#s', label = 'Errorbar2'),
		P(data = getData(), style = 'errorbar', color = '#1235ff', fmt = '#D',
			markersize = 3, markevery = 2, label = 'Errorbar3'),

		P(label = 'Padding Entry 1'),

		P(data = getData(), style = 'lines', color = 'r', fmt = '-.', legend = 'test',
			linewidth = 2, label = 'Lines1'),
		P(data = getData(), style = 'lines', color = '#23ff74', fmt = '--o', label = 'Lines2'),

		P(data = getData(), style = 'band', color = 'g', fmt = '', alpha = 0.4,
			linewidth = 2, label = 'Band1', hatch = '+'),
		P(data = getData(), style = 'band', color = 'b', alpha = 0.4, legend = 'test',
			linewidth = 2, label = 'Band2', hatch = 'o', steps = True),

		P(data = getData(), style = 'bar', color = 'y', alpha = 0.4, label = 'Bar1', hatch = 'o'),

		P(data = getData(), style = 'outline', color = 'r', fmt = ':',
			linewidth = 2, label = 'Outline1'),

		P(data = getData(), style = 'bandline', color = 'm', fmt = '-.', dashes = [2,5,7,2], alpha = 0.5,
			linewidth = 2, label = 'Bandline1', hatch = '////'),
		P(label = 'Padding Entry 2'),
	]
)
