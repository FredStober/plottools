import os, numpy, sys
import matplotlib
import matplotlib.pyplot
from legend import getPlotLabel, MultiLineContainer


def drawErrorbars(ax, plot, plot_data):
	return ax.errorbar(plot_data['x'], plot_data['y'], plot_data['ye'], xerr = plot_data['xe'],
		color = plot.get('color', 'k'), alpha = plot.get('alpha'), label = plot.get('label'),
		linewidth = plot.get('linewidth', 1),
		markeredgewidth = plot.get('markeredgewidth'),
		markersize = plot.get('markersize', 3), markevery = plot.get('markevery'),
		markerfacecolor = plot.get('markerfacecolor', plot.get('color')),
		fmt = plot.get('fmt', 'o'), capsize = plot.get('capsize', 0),
	)


def drawLine(ax, plot, plot_data, y_key):
	connected = plot.pop('connected', True)
	# Draw unconnected lines (eg. each step separatly)
	if connected == None:
		result = []
		for (x, y, x_low, x_high) in zip(plot_data['x'], plot_data[y_key], plot_data['x_low'], plot_data['x_high']):
			result = drawLine(ax, plot, {'x': [x], y_key: [y], 'x_low': [x_low], 'x_high': [x_high]}, y_key)
		return result
	# Draw connected lines only when they border each other
	elif connected == False:
		segments = []
		tmp = []
		for (x, y, x_low, x_high) in zip(plot_data['x'], plot_data[y_key], plot_data['x_low'], plot_data['x_high']):
			if tmp and (tmp[-1][3] != x_low):
				segments.append(tmp)
				tmp = []
			tmp.append((x, y, x_low, x_high))
		if tmp:
			segments.append(tmp)
		result = []
		for segment in segments:
			result = drawLine(ax, plot, {'x': map(lambda e: e[0], segment), y_key: map(lambda e: e[1], segment),
				'x_low': map(lambda e: e[2], segment), 'x_high': map(lambda e: e[3], segment)}, y_key)
		return result
	# Default is to draw everything connected (connected == True)

	data_x = plot_data['x']
	data_y = plot_data[y_key]
	if plot.get('steps', False):
		data_x = numpy.dstack((plot_data['x_low'], plot_data['x_high'])).flatten()
		data_y = numpy.dstack((plot_data[y_key], plot_data[y_key])).flatten()

	result = ax.plot(data_x, data_y, plot.get('fmt', 'o-'),
		color = plot.get('color', 'k'), alpha = plot.get('alpha'), label = plot.get('label'),
		linewidth = plot.get('linewidth', 1),
		markersize = plot.get('markersize', 3), markevery = plot.get('markevery'),
		markerfacecolor = plot.get('markerfacecolor', plot.get('color')),
		drawstyle = plot.get('drawstyle'),
	)
	if plot.get('dashes'):
		result[0].set_dashes(plot.get('dashes'))
	return result


def drawBand(ax, plot, plot_data):
	linestyle = plot.get('band_fmt', plot.get('fmt', '-'))
	linewidth = plot.get('band_linewidth', plot.get('linewidth', 0)),
	if (linestyle.strip() == '') or (linewidth == 0):
		linestyle = '-'
		linewidth = 0

	data_x = plot_data['x']
	data_y_low = plot_data['y_low']
	data_y_high = plot_data['y_high']
	if plot.get('steps', False):
		if plot.get('band_connected', True):
			data_x = numpy.dstack((plot_data['x_low'], plot_data['x_high'])).flatten()
			data_y_high = numpy.dstack((plot_data['y_high'], plot_data['y_high'])).flatten()
			data_y_low = numpy.dstack((plot_data['y_low'], plot_data['y_low'])).flatten()
		else:
			data_nan = numpy.NAN * numpy.ones(plot_data['x'].shape)
			data_x = numpy.dstack((plot_data['x_low'], plot_data['x_high'], data_nan)).flatten()
			data_y_high = numpy.dstack((plot_data['y_high'], plot_data['y_high'], data_nan)).flatten()
			data_y_low = numpy.dstack((plot_data['y_low'], plot_data['y_low'], data_nan)).flatten()

	band_color = plot.get('band_color', plot.get('color'))
	result = ax.fill_between(data_x, data_y_low, data_y_high,
		facecolor = band_color, edgecolor = plot.get('bandedge_color', band_color),
		alpha = plot.get('band_alpha', plot.get('alpha')),
		hatch = plot.get('hatch'),
		linewidth = linewidth, linestyle = linestyle, label = plot.get('label'),
	)
	return result


def drawPlot(ax, plot_raw, opts = {}, xy_switch = False):
	plot = dict(opts)
	plot.update(plot_raw)

	def ensureArray(arr):
		if isinstance(arr, list):
			return numpy.array(arr)
		return arr

	# Retrieve data
	plot_data = {}
	plot_data['x'] = ensureArray(plot['data'][plot.get('xsrc', 'x')])
	plot_data['y'] = ensureArray(plot['data'][plot.get('ysrc', 'y')])
	if isinstance(plot_data['y'], list):
		plot_data['x'] = numpy.array(plot_data['x'])

	plot_zero = numpy.zeros(plot_data['x'].shape)
	if plot.get('xesrc', 'xe') in plot['data']:
		plot_data['xe'] = ensureArray(plot['data'][plot.get('xesrc', 'xe')])
	else:
		plot_data['xe'] = plot_zero

	if plot.get('esrc', 'ye') in plot['data']:
		plot_data['ye'] = ensureArray(plot['data'][plot.get('esrc', 'ye')])
	else:
		plot_data['ye'] = plot_zero

	if xy_switch:
		plot_data = {'x': plot_data['y'], 'xe': plot_data['ye'], 'y': plot_data['x'], 'ye': plot_data['xe']}

	# Expand data (eg. asymmetric error bars)
	def expandData(key, scale, lower_limit):
		if plot_data[key + 'e'].ndim == 2:
			(e_high, e_low) = (plot_data[key + 'e'][0], plot_data[key + 'e'][1])
		else:
			(e_high, e_low) = (plot_data[key + 'e'], plot_data[key + 'e'])
		if scale == 'log': # handle zero/subzero lower limits => only go to edge of axis
			e_low = numpy.where(e_low > plot_data[key], plot_data[key] - lower_limit, e_low)
		# ATTENTION: for plotting we need (-/+) but user input is (+/-)
		plot_data[key + 'e'] = numpy.array([e_low, e_high])
		plot_data[key + '_high'] = numpy.ma.masked_invalid(plot_data[key] + e_high)
		plot_data[key + '_low']  = numpy.ma.masked_invalid(plot_data[key] - e_low)
	expandData('x', ax.get_xscale(), ax.get_xlim()[0])
	expandData('y', ax.get_yscale(), ax.get_ylim()[0])

	# "Steppize" data
	if 'preset' in plot:
		plot.update(plot_presets[plot['preset']])
	plot['label'] = getPlotLabel(plot)

	# Special treatment of #<marker> => unfilled marker
	if 'fmt' in plot:
		if plot['fmt'].startswith('#'):
			plot['markerfacecolor'] = 'w'
			plot['fmt'] = plot['fmt'][1:]
	plotstyle = plot.get('style', 'errorbar')
	if 'band' in plotstyle:
		plot.setdefault('band_fmt', '-')
		plot.setdefault('band_linewidth', 0)

	plot_raw['vis'] = []

	if plotstyle.startswith('errorbar'):
		plot_raw['vis'] = drawErrorbars(ax, plot, plot_data)

	if plotstyle.startswith('errorband'):
		plot_raw['vis'] = [drawBand(ax, plot, plot_data), drawErrorbars(ax, plot, plot_data)]

	if plotstyle.startswith('step'):
		plot['steps'] = True
		plotstyle = 'line'

	if plotstyle.startswith('line'):
		if plot.get('steps', False):
			markersize = plot.pop('markersize', 3)
			plot['markersize'] = 0
			line = drawLine(ax, plot, plot_data, y_key = 'y')
			plot_raw['vis'] = [line]
			if line[0].get_marker() not in ['', ' ', 'None', None]:
				plot['steps'] = False
				plot['fmt'] = line[0].get_marker()
				plot['markersize'] = markersize
				plot_raw['vis'].append(drawLine(ax, plot, plot_data, y_key = 'y'))
		else:
			plot_raw['vis'] = drawLine(ax, plot, plot_data, y_key = 'y')

	if plotstyle == 'outline':
		plot_raw['vis'] = MultiLineContainer()
		plot.setdefault('fmt', '')
		plot_raw['vis'].extend(drawLine(ax, plot, plot_data, y_key = 'y_low'))
		plot_raw['vis'].extend(drawLine(ax, plot, plot_data, y_key = 'y_high'))

	if plotstyle == 'band':
		plot_raw['vis'] = drawBand(ax, plot, plot_data)

	if plotstyle == 'bandline':
		plot_raw['vis'] = [drawBand(ax, plot, plot_data), drawLine(ax, plot, plot_data, y_key = 'y')]

	if plotstyle.startswith('bar'):
		islog = (opts.get('yscale', 'linear') == 'log')
		plot_raw['vis'] = ax.bar(plot_data['x_low'], plot_data['y'], plot_data['xe'][0] + plot_data['xe'][1],
			color = plot.get('color'), alpha = plot.get('alpha'), label = plot.get('label'),
			log = islog, linewidth = plot.get('linewidth', 0),
		)

#	elif plotstyle == 'bandx':
#		plot_raw['vis'] = ax.fill_betweenx(plot_data['y'], plot_data['x_low'], plot_data['x_high'],
#			color = plot.get('color'), alpha = plot.get('alpha'), label = plot.get('label'),
#			linewidth=plot.get('linewidth', 0)
#		)

	if not plot_raw['vis']:
		raise Exception('Unknown plotstyle %s!' % plotstyle)
