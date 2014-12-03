import os, numpy, sys
import matplotlib
import matplotlib.pyplot
from mathtools import format_unc, format_exp
from legend import getPlotLabel, MultiLineContainer
from fractions import Fraction

class PlotEntry:
	def __init__(self, data = None, style = 'errorbar', **kwargs):
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
	if opts.get('square', False):
		s = opts.get('height', opts.get('width', 4.2))
		if ('height' in opts) and ('width' in opts):
			assert(opts.get('height') == opts.get('width'))
		fig = matplotlib.pyplot.figure(figsize=(s, s))
	else:
		if 'height' in opts:
			h = opts.get('height', 4.2)
			w = opts.get('width', h * numpy.sqrt(2))
		else:
			w = opts.get('width', 5.9)
			h = opts.get('height', w / numpy.sqrt(2))
		fig = matplotlib.pyplot.figure(figsize=(w, h))
	fig.subplots_adjust(
		wspace = opts.get('wspace'), hspace = opts.get('hspace'),
		left = opts.get('left', opts.get('bl', 0.15)),
		bottom = opts.get('bottom', opts.get('bl', 0.15)),
		right = 1 - opts.get('right', opts.get('tr', 0.05)),
		top = 1 - opts.get('top', opts.get('tr', 0.05)))
	return fig


def setupAxis_single(ax, ax_int, opts, prefix):
	if opts.get(prefix + 'labelsize', None):
		ax_int.label.set_size(opts.get(prefix + 'labelsize'))
	ax_int.label.set_color(opts.get(prefix + 'color', 'black'))

	scale = opts.get(prefix + 'scale', 'linear')
	axlim = opts.get(prefix + 'range')
	if prefix.startswith('x'):
		if axlim:
			ax.set_xlim(*axlim)
		if scale != 'linear':
			ax.set_xscale(scale)
	elif prefix.startswith('y'):
		if axlim:
			ax.set_ylim(*axlim)
		if scale != 'linear':
			ax.set_yscale(scale)

	style = opts.get(prefix + 'style', scale)

	if style == 'manual':
		tmp = opts.get(prefix + 'ticks_manual')
		ax_int.set_ticks(tmp['ticks'])
		ax_int.set_ticklabels(tmp['labels'],
			rotation = tmp.get('rotation', 0),
			fontsize = tmp.get('size', None),
			color = opts.get(prefix + 'color', 'black'))
		return

	elif style == 'log':
		opts.setdefault(prefix + 'format', 'e')
		major = opts.get(prefix + 'ticks', [1,2,5])
		minor = filter(lambda x: x not in major, range(1, 10))
		ax_int.set_major_locator(matplotlib.ticker.LogLocator(10, major))
		ax_int.set_minor_locator(matplotlib.ticker.LogLocator(10, minor))

	elif style == 'linear':
		opts.setdefault(prefix + 'format', 'f')
		ax_int.set_major_locator(matplotlib.ticker.AutoLocator())
		ax_int.set_minor_locator(matplotlib.ticker.AutoMinorLocator(n = opts.get(prefix + 'minor')))

	elif style.startswith('pi'):
		opts.setdefault(prefix + 'format', style)
		major = opts.get(prefix + 'sub', 4)
		ax_int.set_major_locator(matplotlib.ticker.MultipleLocator(numpy.pi / major))
		ax_int.set_minor_locator(matplotlib.ticker.AutoMinorLocator(n = opts.get(prefix + 'minor')))

	format = opts.get(prefix + 'format')
	def format_pi_special(value): # format -pi, 0 and +pi in a special way
		if abs(value) < 1e-10:
			return '$0$'
		if abs(abs(value / numpy.pi) - 1) < 1e-10:
			if value < 0:
				return '$-\pi$'
			return '$\pi$'
	if format == 'e':
		ax_int.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, y: format_exp(x)))
	elif format == 'f':
		prec = str(opts.get(prefix + 'prec', 1))
		ax_int.set_major_formatter(matplotlib.ticker.FormatStrFormatter(r'$%.' + prec + 'f$'))
	elif format == 'deg':
		prec = str(opts.get(prefix + 'prec', 1))
		def format_deg(value, pos):
			return (r'$%.' + prec + 'f^{\circ}$') % (value / numpy.pi * 180)
		ax_int.set_major_formatter(matplotlib.ticker.FuncFormatter(format_deg))
	elif format == 'pi':
		prec = str(opts.get(prefix + 'prec', 1))
		def format_pi(value, pos):
			result = format_pi_special(value)
			if result != None:
				return result
			return (r'$%.' + prec + 'f \pi$') % (value / numpy.pi)
		ax_int.set_major_formatter(matplotlib.ticker.FuncFormatter(format_pi))
	elif format == 'pifrac':
		def format_pifrac(value, pos):
			result = format_pi_special(value)
			if result != None:
				return result
			x = Fraction(value / numpy.pi).limit_denominator()
#			if abs(x.numerator) == 1:
#				if value < 0:
#					return r'$\frac{-\pi}{%d}$' % (x.denominator)
#				return r'$\frac{\pi}{%d}$' % (x.denominator)
			if value < 0:
				return r'$-\frac{%d}{%d}\pi$' % (-x.numerator, x.denominator)
			return r'$\frac{%d}{%d}\pi$' % (x.numerator, x.denominator)
		ax_int.set_major_formatter(matplotlib.ticker.FuncFormatter(format_pifrac))

	# Apply color
	for x in ax_int.get_ticklabels():
		x.set_color(opts.get(prefix + 'color', 'black'))


def setupAxis(ax, opts, xprefix = 'x', yprefix = 'y'):
	ax.set_xlabel(opts.get(xprefix + 'label', 'x'), ha = 'right', va = 'top', x = 1,
		labelpad = opts.get(xprefix + 'pad', 14))
	setupAxis_single(ax, ax.xaxis, opts, xprefix)

	ax.set_ylabel(opts.get(yprefix + 'label', 'y'), ha = 'right', va = 'top', y = 1,
		labelpad = opts.get(yprefix + 'pad', 24))
	setupAxis_single(ax, ax.yaxis, opts, yprefix)

	ax.grid(opts.get('grid', False))
	return ax


def getAxis(opts, fig, pos = 111, xshare = None, yshare = None):
	args = {}
	if xshare:
		args['sharex'] = xshare
	if yshare:
		args['sharey'] = yshare
	args['polar'] = opts.get('polar', False)

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
	sys.stdout.write('saving plot %s %s ' % (dest, output,))
	sys.stdout.flush()
	if not os.path.exists(os.path.dirname(dest)):
		os.makedirs(os.path.dirname(dest))
	for ext in output:
		if ext == 'png':
			kwargs.setdefault('dpi', 300)
		fig.savefig('%s.%s' % (dest, ext), **kwargs)
		sys.stdout.write('%s ' % ext)
		sys.stdout.flush()
	sys.stdout.write('\n')
	sys.stdout.flush()
	fig.clear()
	matplotlib.pyplot.close()
