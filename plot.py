from basic import *
from legend import *
from augments import *
from draw import *

def doPlot(fn, opts_raw, plots, **kwargs):
	opts = mergeOpts(opts_raw, kwargs)
	(fig, ax) = setupPlot(opts)
	drawInfoText(opts, ax)

	base_ax = ax

	plots = map(dict, plots) # convert PlotEntries to dictionaries
	base_ax2 = None
	for p in plots:
		if not p.get('data'):
			continue
		axis = p.pop('axis', 1)
		if axis == 1:
			drawPlot(ax, p, opts.get('plots', {}), opts.get('xy_switch', False))
		elif axis == 2:
			if not base_ax2:
				xprefix = 'x'
				yprefix = 'y'
				if 'x2range' in opts:
					xprefix = 'x2'
					base_ax2 = base_ax.twiny()
				if 'y2range' in opts:
					yprefix = 'y2'
					base_ax2 = base_ax.twinx()
				setupAxis(base_ax2, opts, xprefix = xprefix, yprefix = yprefix)
			drawPlot(base_ax, p, opts.get('plots2', opts.get('plots', {})), opts.get('xy_switch', False))

	drawLegend(base_ax, plots, opts)
	if 'notesize' in opts:
		drawAnnotation(base_ax, opts.get('notes', []), {'fontsize': opts.get('notesize')})
	else:
		drawAnnotation(base_ax, opts.get('notes', []))
	if 'area' in opts:
		for entry in opts['area']:
			drawArea(base_ax, **entry)

	drawLines(base_ax, kwargs.get('lines', []), **opts_raw.get('lines', {}))
	if kwargs.get('fun'):
		kwargs.get('fun')(base_ax)
	savePlot(fig, fn, opts_raw.get('formats', ['png', 'pdf']))


def get2DXYZ(opts, src):
	def getAxisArray(prefix):
		vsrc = opts.get('%ssrc' % prefix, prefix)
		esrc = vsrc + 'e'
		if opts.get('raw_data'):
			return numpy.array(src[vsrc])
		else:
			return numpy.array(list(src[vsrc] - src[esrc]) + [list(src[vsrc])[-1] + src[esrc][-1]])
	x = getAxisArray('x')
	y = getAxisArray('y')
	z = src[opts.get('zsrc', 'z')]
	if 'zrange' in opts:
		zr = opts.get('zrange')
		if zr[0] != None:
			z = numpy.ma.masked_less(z, zr[0])
		if zr[1] != None:
			z = numpy.ma.masked_greater(z, zr[1])
	return (x, y, z)


def do2DPlot(fn, opts, src):
	(fig, ax) = setupPlot(opts)
	setupAxis(ax, opts)
	drawInfoText(opts, ax)

	zcolor = opts.get('zcolor', 'bwr')
	if isinstance(zcolor, str):
		cmap = matplotlib.pyplot.get_cmap(zcolor)
	else:
		cmap = zcolor
	(x, y, z) = get2DXYZ(opts, src)

	zscale = opts.get('zscale', 'linear')
	level_style = None
	if zscale == 'norm':
		zrange = opts.get('zrange', (-1, 1))
		norm = matplotlib.colors.Normalize(zrange[0], zrange[1])
		level_style = ['-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-']
		level_pos = [-1. , -0.8, -0.6, -0.4, -0.2,  0. ,  0.2,  0.4,  0.6,  0.8,  1. ]
		level_color = ['k', 'k', 'k', 'k', 'k', 'k', 'w', 'w', 'w', 'w', 'w']
	elif zscale == 'log':
		zrange = opts.get('zrange', (z.min(), z.max()))
		norm = matplotlib.colors.LogNorm(zrange[0], zrange[1])
		level_pos = opts.get('zlevel', None)
		level_color = opts.get('zlevel_color', None)
	else:
		zrange = opts.get('zrange', (z.min(), z.max()))
		norm = matplotlib.colors.Normalize(zrange[0], zrange[1])
		level_pos = opts.get('zlevel', None)
		level_color = opts.get('zlevel_color', None)

	mode = map(str.strip, opts.get('mode', 'pcolor,bar').split(','))
	if 'pcolormesh' in mode:
		mesh = ax.pcolormesh(x, y, z, alpha = 1, norm = norm, cmap = cmap, edgecolors='face')
	elif 'pcolor' in mode:
		mesh = ax.pcolor(x, y, z, alpha = 1, norm = norm, cmap = cmap, edgecolors='face')

	if 'text' in mode:
		for i, r in enumerate(z):
			for j, v in enumerate(r):
				try:
					if v.mask:
						continue
				except:
					pass
				if opts.get('zscale', 'log'):
					if x[j] == 0:
						p_x = numpy.exp((numpy.log(ax.get_xlim()[0]) + numpy.log(x[j + 1])) / 2.)
					else:
						p_x = numpy.exp((numpy.log(x[j]) + numpy.log(x[j + 1])) / 2.)
					if y[i] == 0:
						p_y = numpy.exp((numpy.log(ax.get_ylim()[0]) + numpy.log(y[i + 1])) / 2.)
					else:
						p_y = numpy.exp((numpy.log(y[i]) + numpy.log(y[i + 1])) / 2.)
				else:
					p_x = (x[j] + x[j + 1]) / 2.
					p_y = (y[i] + y[i + 1]) / 2.
				if (p_x < ax.get_xlim()[0]) or (p_y < ax.get_ylim()[0]) or (p_x > ax.get_xlim()[1]) or (p_y > ax.get_ylim()[1]):
					continue
				ax.text(p_x, p_y, '%.1f' % v, ha = 'center', va = 'center', fontsize = 6)
#				print i, j, v, p_x, p_y
#		print x.shape, x
#		print y.shape, y
#		print z.shape, z

	if 'contourf' in mode:
		opts.setdefault('raw_data', True)
		(x, y, z) = get2DXYZ(opts, src)
		cmesh = ax.contourf(x, y, z, alpha = 1, norm = norm,
			linestyles = level_style, levels = level_pos, colors = level_color)
	elif 'contour' in mode:
		opts.setdefault('raw_data', True)
		(x, y, z) = get2DXYZ(opts, src)
		cmesh = ax.contour(x, y, z, alpha = 1, norm = norm,
			linestyles = level_style, levels = level_pos, colors = level_color)
	if 'clabel' in mode:
		zcprec = '$%.' + str(opts.get('zcprec', 1)) + 'f$'
		ax.clabel(cmesh, inline=True, fontsize=10, fmt = zcprec, colors = level_color)

	cb = None
	zprec = '$%.' + str(opts.get('zprec', 1)) + 'f$'
	if 'bar' in mode:
		cb = fig.colorbar(mesh, ax=ax, aspect=30, fraction = 0.15, pad = 0.01, format=zprec)
	if 'cbar' in mode:
		cb = fig.colorbar(cmesh, ax=ax, aspect=30, fraction = 0.15, pad = 0.01, format=zprec)
	if cb:
		try:
			cb.solids.set_edgecolor("face")
		except:
			pass
		cb.set_label(opts.get('zlabel', 'z'), ha = 'right', va = 'top', y = 1, size = 11.5,
			labelpad = opts.get('zpad', None))
		cb.set_minor_locator = lambda *args: None
		cb.set_major_locator = lambda x: setattr(cb, 'locator', x)
		cb.set_major_formatter = lambda x: setattr(cb, 'formatter', x)
		cb.get_ticklabels = lambda *args: []
		setupAxis_single_style(cb, cb, opts, 'z', zscale)
		cb.update_ticks()

	if 'notesize' in opts and 'notecolor' in opts :
		drawAnnotation(ax, opts.get('notes', []), {'fontsize': opts.get('notesize'), 'color': opts.get('notecolor')})
	elif 'notesize' in opts:
		drawAnnotation(ax, opts.get('notes', []), {'fontsize': opts.get('notesize')})
	else:
		drawAnnotation(ax, opts.get('notes', []))
	drawLines(ax, opts.get('lines', {}))
	savePlot(fig, fn, opts.get('formats', ['png', 'pdf']), **opts.get('output_opts', {}))

#	if showErrors:
#		ax2 = fig.add_axes((0.15, 0.1, 0.72*(1-0.05-0.02), 0.2), xlim = opts.get('xrange'), ylim = opts.get('y2range'))
#		opts['yscale'] = opts.get('y2scale', 'linear')
#		setupAxis(ax2, opts)
#		ax2.yaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter('$%.1f$'))
#		ax2.set_ylabel(opts.get('y2label', 'y'), va = 'center', y = 0.5)
#		tmp = dict(src)
#		tmp['ye'] = ye_err
#		plots = [P(data = scaleData(makeRelative(tmp, yoffset=0), 100), label = 'Error', style = 'band', alpha = 0.5, color = 'k')]
#		drawPlot(ax2, map(dict, plots), xy_switch = opts.get('xy_switch', False))
#		drawLines(ax2, [0])
