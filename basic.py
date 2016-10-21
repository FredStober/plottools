import os, numpy, sys, time
import matplotlib
import matplotlib.pyplot
from format import format_exp
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


def setupAxis_single_style(ax, ax_int, opts, prefix, scale):
	style = opts.get(prefix + 'style', scale)

	if style == 'none':
		ax_int.set_major_formatter(matplotlib.ticker.NullFormatter())
		ax_int.set_minor_formatter(matplotlib.ticker.NullFormatter())

	elif style == 'manual':
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
		ticks = opts.get(prefix + 'ticks', None)
		if ticks == None:
			ax_int.set_major_locator(matplotlib.ticker.AutoLocator())
		elif ticks == 'int':
			ax_int.set_major_locator(matplotlib.ticker.MultipleLocator())
		else:
			ax_int.set_major_locator(matplotlib.ticker.MaxNLocator(nbins = ticks))
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
		ax_int.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, y: format_exp(x, prec=opts.get(prefix + 'prec', 1))))
	if format == 'date':
		fmtstr = opts.get(prefix + 'datefmt', '%Y-%m-%d')
		ax_int.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, y: time.strftime(fmtstr, time.localtime(x))))
	elif format == 'f':
		prec = str(opts.get(prefix + 'prec', 1))
		ax_int.set_major_formatter(matplotlib.ticker.FormatStrFormatter(r'$%.' + prec + 'f$'))
	elif format == 'p':
		prec = str(opts.get(prefix + 'prec', 1))
		def format_phy(value, pos):
			tmp = (r'%.' + prec + 'f') % value
			tmp = tmp.rstrip('0')
			tmp = tmp.rstrip('.')
			return '$%s$' % tmp
		ax_int.set_major_formatter(matplotlib.ticker.FuncFormatter(format_phy))
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
		if opts.get(prefix + 'rotation', 0) != 0:
			x.set_ha('right')
			x.set_rotation(opts.get(prefix + 'rotation', 0))


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

	setupAxis_single_style(ax, ax_int, opts, prefix, scale)


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


class UncertaintyHolder(object):
	def __init__(self):
		self._data = []
		self._keys = set()

	def set(self, x, **values):
		for key in values:
			self._keys.add(key)
			try:
				self._data.append((tuple(x), key, values[key]))
			except:
				self._data.append(((x,), key, values[key]))

	def get_keys(self):
		return sorted(self._keys)

	def get(self):
		def removeEpsilon(src):
			result = {}
			while src:
				x = src.pop()
				result[x] = x
				for y in filter(lambda y: abs(x-y) / x < 1e-10, src):
					src.remove(y)
					result[y] = x
			return result
		xlist = []
		for x in self._data:
			xlist.extend(x[0])
		xmap = removeEpsilon(sorted(xlist))
		result = {}
		for (x, key, value) in self._data:
			x_new = tuple(map(lambda y: xmap[y], x))
			result.setdefault(x_new, {}).setdefault(key, {}).update(value)
		return result


def saveHEPDATA(fn, opts, plots):
	from augments import parseAnnotation
	from draw import parsePlotData

	hepdata_info = opts.get('hepdata', {})
	fp = open(fn + '.hepdata', 'w')
	style = hepdata_info.pop('style', None)
	if not style:
		return

	def writeHeader(xheader = '', yheader = ''):
		def writeEntry(key):
			if hepdata_info.get(key):
				fp.write('*%s: %s\n' % (key, str(hepdata_info[key]).strip()))
		fp.write('*dataset:\n')
		writeEntry('location')
		writeEntry('dscomment')
		writeEntry('reackey')
		writeEntry('obskey')
		for entry in hepdata_info.get('qual', []):
			fp.write('*qual:%s\n' % entry.strip())
		for note in opts.get('notes', []):
			fp.write('*qual:%s\n' % note.split(',')[-1].strip())
		fp.write('*xheader: %s\n' % xheader)
		fp.write('*yheader: %s\n' % yheader)

	def writeData(header, entries):
		fp.write('*data: %s\n' % header)
		for entry in entries:
			fp.write(entry + '\n')
		fp.write('*dataend:\n')

	def writeUHData(xheader, yheader, uh, yerr_list_order = None):
		x_fmt = '%.' + '%d%s' % (opts.get('xprec', 6), opts.get('xformat', 'g'))
		y_fmt = '%.' + '%d%s' % (opts.get('yprec', 3), opts.get('yformat', 'f'))

		output = []
		for (x, y) in sorted(uh.get().items()):
			y_str = []
			for idx in uh.get_keys():
				y_info = y.get(idx, {})
				if y_info:
					tmp = y_fmt % y_info.pop('y')
					def fmt_error(err):
						ep_str = y_fmt % err[0]
						em_str = y_fmt % err[1]
						if ep_str == em_str:
							return ep_str
						return '+%s,-%s' % (ep_str, em_str)
					if 'ye' in y_info:
						tmp += ' ' + fmt_error(y_info.pop('ye'))
					y_err_list = sorted(y_info.keys())
					if yerr_list_order:
						y_err_list = map(lambda x: x.split('_')[-1], yerr_list_order)
					sys_tmp = map(lambda key: 'DSYS=%s:%s' % (fmt_error(y_info[key]), key), y_err_list)
					if sys_tmp:
						tmp += ' +- (' + str.join(',', sys_tmp) + ')'
				else:
					tmp = ''
				y_str.append(tmp)
			output.append('%s TO %s ; %s' % (x_fmt % x[0], x_fmt % x[1], str.join(' ; ', y_str)))
		writeData(str.join(' : ', 'x'*len(xheader) + 'y'*len(yheader)), output)

	if style == 1:
		xheader = [hepdata_info.get('xheader')]
		yheader = []
		for plot in plots:
			yheader.append('%s(%s)' % (hepdata_info.get('yheader'), plot.get('label', '')))
		writeHeader(str.join(' : ', xheader), str.join(' : ', yheader))

		uh = UncertaintyHolder()
		output_data = {}
		for i, plot in enumerate(plots):
			plot_param = dict(plot)
			plot_param.update(opts.get('plots', {}))
			plot_data = parsePlotData(plot_param)
			for (xl, xh, y, yel, yeh) in zip(plot_data['x_low'], plot_data['x_high'], plot_data['y'], plot_data['ye'][0], plot_data['ye'][1]):
				xr = opts.get('xrange')
				if xr:
					if xl < xr[1]:
						uh.set((xl, xh), **{str(i): {'y': y, 'ye': (yeh, yel)}})
				else:
					uh.set((xl, xh), **{str(i): {'y': y, 'ye': (yeh, yel)}})
		writeUHData(xheader, yheader, uh)

	elif style == 2:
		y_err_list = hepdata_info.get('yerr')
		xheader = [hepdata_info.get('xheader')]
		yheader = []
		for plot in plots:
			yheader.append('%s(%s)' % (hepdata_info.get('yheader'), plot.get('label', '')))
		writeHeader(str.join(' : ', xheader), str.join(' : ', yheader))

		uh = UncertaintyHolder()
		output_data = {}
		for i, plot in enumerate(plots):
			plot_param = dict(plot)
			plot_param.update(opts.get('plots', {}))
			for y_err in y_err_list:
				plot_param['esrc'] = y_err
				plot_data = parsePlotData(plot_param)
				for (xl, xh, y, yel, yeh) in zip(plot_data['x_low'], plot_data['x_high'], plot_data['y'], plot_data['ye'][0], plot_data['ye'][1]):
					y_err = y_err.split('_')[-1]
					xr = opts.get('xrange')
					if xr:
						if xl < xr[1]:
							uh.set((xl, xh), **{str(i): {'y': y, y_err: (yeh, yel)}})
					else:
						uh.set((xl, xh), **{str(i): {'y': y, y_err: (yeh, yel)}})
		print uh.get()
		writeUHData(xheader, yheader, uh, y_err_list)


def savePlotEx(fig, fn, opts, plots = None):
	if fn.endswith('.png'):
		opts['formats'] = ['png']
		fn = fn[:-4]
	if fn.endswith('.pdf'):
		opts['formats'] = ['pdf']
		fn = fn[:-4]
	if fn.endswith('.hepdata'):
		opts['formats'] = ['hepdata']
		fn = fn[:-8]
	formats = opts.get('formats', ['png', 'pdf', 'hepdata'])
#	formats = ['png']
	kwargs = opts.get('output_opts', {})
	if 'hepdata' in formats:
		formats.remove('hepdata')
		saveHEPDATA(fn, opts, plots)
	savePlot(fig, fn, formats, **kwargs)
