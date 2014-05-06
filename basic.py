import os, numpy
import matplotlib
import matplotlib.pyplot
from mathtools import format_unc, format_exp
from legend import getPlotLabel

class PlotEntry:
	def __init__(self, data, style = 'errorbar', **kwargs):
		self.info = kwargs
		self.info['data'] = data
		self.info['style'] = style
	def __iter__(self): # this class is converted into a dictionary (its the only interface!)
		for key in self.info:
			yield (key, self.info[key])
P = PlotEntry


def mergeOpts(dict1, dict2):
	opts = dict(dict1)
	opts.update(dict2)
	return opts


def getFigure(opts):
	w = opts.get('width', 4.2)
	if opts.get('square', False):
		fig = matplotlib.pyplot.figure(figsize=(w, w))
	else:
		fig = matplotlib.pyplot.figure(figsize=(numpy.sqrt(2)*w, w))
	fig.subplots_adjust(
		left=opts.get('left', 0.15),
		right=1-opts.get('right', 0.05),
		top=1-opts.get('top', 0.08),
		bottom=opts.get('bottom', 0.15))
	return fig


def setupAxis(ax, opts, xprefix = 'x', yprefix = 'y'):
	def setupAxis_single(ax_int, prefix, ):
		if opts.get(prefix + 'labelsize', None):
			ax_int.label.set_size(opts.get(prefix + 'labelsize'))
		ax_int.label.set_color(opts.get(prefix + 'color', 'black'))

		scale = opts.get(prefix + 'scale', 'linear')
		axlim = opts.get(prefix + 'range')
		if prefix.startswith('x'):
			if axlim:
				ax.set_xlim(*axlim)
			ax.set_xscale(scale)
		elif prefix.startswith('y'):
			if axlim:
				ax.set_ylim(*axlim)
			ax.set_yscale(scale)

		tmp = opts.get(prefix + 'ticks_manual', None)
		if tmp:
			ax_int.set_ticks(tmp['ticks'])
			ax_int.set_ticklabels(tmp['labels'],
				rotation = tmp.get('rotation', 0),
				fontsize = tmp.get('size', None),
				color = opts.get(prefix + 'color', 'black'))

		elif scale == 'log':
			ax_int.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, y: format_exp(x)))
			major = opts.get(prefix + 'ticks', [1,2,5])
			minor = filter(lambda x: x not in major, range(1, 10))
			ax_int.set_major_locator(matplotlib.ticker.LogLocator(10, major))
			ax_int.set_minor_locator(matplotlib.ticker.LogLocator(10, minor))

		elif opts.get(prefix + 'scaletex', True):
			prec = str(opts.get(prefix + 'prec', 1))
			ax_int.set_major_formatter(matplotlib.ticker.FormatStrFormatter(r'$%.' + prec + 'f$'))
			for x in ax_int.get_ticklabels():
				x.set_color(opts.get(prefix + 'color', 'black'))

	ax.set_xlabel(opts.get(xprefix + 'label', 'x'), ha = 'right', va = 'top', x = 1,
		labelpad = opts.get(xprefix + 'pad', 14))
	setupAxis_single(ax.xaxis, xprefix)

	ax.set_ylabel(opts.get(yprefix + 'label', 'y'), ha = 'right', va = 'top', y = 1,
		labelpad = opts.get(yprefix + 'pad', 24))
	setupAxis_single(ax.yaxis, yprefix)

	ax.grid(opts.get('grid', False))
	return ax


def getAxis(opts, fig, pos = 111, xshare = None, yshare = None):
	args = {}
	if xshare:
		args['sharex'] = xshare
	if yshare:
		args['sharey'] = yshare

	if isinstance(pos, tuple):
		ax = fig.add_subplot(*pos, **args)
	else:
		ax = fig.add_subplot(pos, **args)
	return setupAxis(ax, opts)


def setupPlot(opts, **kwargs):
	opts = mergeOpts(opts, kwargs)
	fig = getFigure(opts)
	ax = getAxis(opts, fig, 111)
	return (fig, ax)


def savePlot(fig, fn, output = ['png', 'pdf'], **kwargs):
	dest = os.path.join(os.getcwd(), fn)
	print 'saving plot', dest, output
	if not os.path.exists(os.path.dirname(dest)):
		os.makedirs(os.path.dirname(dest))
	for ext in output:
		fig.savefig('%s.%s' % (dest, ext), **kwargs)
	fig.clear()
	matplotlib.pyplot.close()


def drawPlots(ax, plots, opts = {}, xy_switch = False):
	for plot_raw in plots:
		plot = dict(opts)
		plot.update(plot_raw)
		if 'preset' in plot:
			plot.update(plot_presets[plot['preset']])
		plot['label'] = getPlotLabel(plot)
		if 'fmt' in plot:
			if plot['fmt'].startswith('#'):
				plot['markerfacecolor'] = 'w'
				plot['fmt'] = plot['fmt'][1:]

		# Retrieve data
		plot_data = {'x': plot['data']['x'], 'xe': plot['data']['xe']}
		plot_data['y'] = plot['data'][plot.get('ysrc', 'y')]
		plot_data['ye'] = plot['data'][plot.get('esrc', 'ye')]
		if xy_switch:
			plot_data = {'x': plot_data['y'], 'xe': plot_data['ye'], 'y': plot_data['x'], 'ye': plot_data['xe']}

		# Expand asymmetric error bars
		if plot_data['ye'].ndim == 2:
			(ye_high, ye_low) = (plot_data['ye'][0], plot_data['ye'][1])
		else:
			(ye_high, ye_low) = (plot_data['ye'], plot_data['ye'])
		if ax.get_yscale() == 'log': # handle zero/subzero lower limits
			ye_low = numpy.where(ye_low > plot_data['y'], plot_data['y'] - ax.get_ylim()[0], ye_low)
		plot_data['ye'] = numpy.array([ye_low, ye_high])

		plotstyle = plot.get('style', 'errorbar')
		if plotstyle == 'steps':
			plot.setdefault('fmt', '')
			plot.setdefault('drawstyle', 'steps-mid')
			plotstyle = 'lines'

		if plotstyle == 'errorbar':
			plot_raw['vis'] = ax.errorbar(plot_data['x'], plot_data['y'], plot_data['ye'], xerr = plot_data['xe'],
				color = plot.get('color', 'k'), alpha = plot.get('alpha'), label = plot.get('label'),
				linewidth = plot.get('linewidth', 1),
				markersize = plot.get('markersize', 1), markevery = plot.get('markevery'),
				markerfacecolor = plot.get('markerfacecolor', plot.get('color')),
				fmt = plot.get('fmt', 'o'), capsize = plot.get('capsize', 0),
			)

		elif plotstyle == 'bars':
			islog = (opts.get('yscale', 'linear') == 'log')
			plot_raw['vis'] = ax.bar(plot_data['x'] - plot_data['xe'], plot_data['y'], 2 * plot_data['xe'],
				color = plot.get('color'), alpha = plot.get('alpha'), label = plot.get('label'),
				log = True, linewidth = plot.get('linewidth', 0),
			)

		elif plotstyle == 'lines':
			plot_raw['vis'] = ax.plot(plot_data['x'], plot_data['y'], plot.get('fmt', 'o-'),
				color = plot.get('color'), alpha = plot.get('alpha'), label = plot.get('label'),
				linewidth=plot.get('linewidth', 1),
				markersize = plot.get('markersize', 1), markevery = plot.get('markevery'),
				markerfacecolor = plot.get('markerfacecolor', plot.get('color')),
				drawstyle = plot.get('drawstyle'),
			)

		elif (plotstyle == 'band') or (plotstyle == 'bandx') or (plotstyle == 'outline') or (plotstyle == 'bandline'):
			if plot.get('steps', False):
				y_low = plot_data['y'] - plot_data['ye'][0]
				y_high = plot_data['y'] + plot_data['ye'][1]
				y_low = numpy.ma.masked_invalid(y_low)
				y_high = numpy.ma.masked_invalid(y_high)
				xlims = (plot_data['x'] - plot_data['xe'], plot_data['x'] + plot_data['xe'])
				plot_data['x'] = numpy.dstack(xlims).flatten()
				y_low = numpy.repeat(y_low, 2)
				y_high = numpy.repeat(y_high, 2)
			else:
				y_low = plot_data['y'] - plot_data['ye'][0]
				y_high = plot_data['y'] + plot_data['ye'][1]

			if plotstyle == 'band':
				plot_raw['vis'] = ax.fill_between(plot_data['x'], y_low, y_high,
					color = plot.get('color'), alpha = plot.get('alpha'), label = plot.get('label'),
					linewidth = plot.get('linewidth', 0)
				)
			if plotstyle == 'bandx':
				if plot_data['xe'].ndim == 2:
					x_low = plot_data['x'] - plot_data['xe'][0]
					x_high = plot_data['x'] + plot_data['xe'][1]
				else:
					x_low = plot_data['x'] - plot_data['xe']
					x_high = plot_data['x'] + plot_data['xe']
				x_low = numpy.ma.masked_invalid(x_low)
				x_high = numpy.ma.masked_invalid(x_high)
				plot_raw['vis'] = ax.fill_betweenx(numpy.repeat(plot_data['y'], 2), x_low, x_high,
					color = plot.get('color'), alpha = plot.get('alpha'), label = plot.get('label'),
					linewidth=plot.get('linewidth', 0)
				)
			elif plotstyle == 'bandline':
				plot_raw['vis'] = ax.fill_between(plot_data['x'], y_low, y_high,
					color = plot.get('color'), alpha = plot.get('alpha'), label = plot.get('label'),
					linewidth=plot.get('linewidth', 0)
				)
			elif plotstyle == 'outline':
				ax.plot(plot_data['x'], y_low, plot.get('fmt', ''),
					color = plot.get('color'), alpha = plot.get('alpha'),
					markersize = plot.get('markersize', 1), markevery = plot.get('markevery'),
					markerfacecolor = plot.get('markerfacecolor', plot.get('color')),
					linewidth=plot.get('linewidth', 1), drawstyle = plot.get('drawstyle')
				)
				plot_raw['vis'] = ax.plot(plot_data['x'], y_high, plot.get('fmt', ''),
					color = plot.get('color'), alpha = plot.get('alpha'), label = plot.get('label'),
					markersize = plot.get('markersize', 1), markevery = plot.get('markevery'),
					markerfacecolor = plot.get('markerfacecolor', plot.get('color')),
					linewidth=plot.get('linewidth', 1), drawstyle = plot.get('drawstyle')
				)
		else:
			raise
