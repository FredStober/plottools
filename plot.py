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
#	if showErrors:
#		fig = matplotlib.pyplot.figure(figsize=(6, 6))
#		ax = fig.add_axes((0.15, 0.3, 0.72, 0.65), xlim = opts.get('xrange'), ylim = opts.get('yrange')) # l,b,w,h
#	else:
	(fig, ax) = setupPlot(opts)
#	fig = getFigure(opts)
#	ax = fig.add_axes((0.15, 0.1, 0.72, 0.85), xlim = opts.get('xrange'), ylim = opts.get('yrange')) # l,b,w,h
#	opts['yscale'] = opts.get('y1scale', 'linear')
#	opts['ylabel'] = opts.get('y1label', 'y1')
	setupAxis(ax, opts)
#	ax.xaxis.set_major_formatter(matplotlib.ticker.NullFormatter())
#	ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
	drawInfoText(opts, ax)

	cmap = matplotlib.pyplot.get_cmap(opts.get('zcolor', 'bwr'))
	if opts.get('zcolor_user'):
		cmap = opts.get('zcolor_user')
	(x, y, z) = get2DXYZ(opts, src)

	zscale = opts.get('zscale', 'linear')
	if zscale == 'norm':
		norm = matplotlib.colors.Normalize(-1, 1)
	elif zscale == 'log':
		norm = matplotlib.colors.LogNorm(z.min(), z.max())
	else:
		norm = matplotlib.colors.Normalize(z.min(), z.max())

#	mesh = ax.pcolormesh(x, y, z, alpha = 1, norm = norm, cmap = cmap, edgecolors='face')
	mesh = ax.pcolor(x, y, z, alpha = 1, norm = norm, cmap = cmap, edgecolors='face')
	if False:
		mesh = ax.contour(x, y, z, alpha = 1, norm = norm,
			linestyles = ['-', '-', '-', '-', '-', '-', '-', '-', '-', '-', '-'],
#			linestyles = ['--', '-', '--', '-', '--', '-', '--', '-', '--', '-', '--'],
			levels = [-1. , -0.8, -0.6, -0.4, -0.2,  0. ,  0.2,  0.4,  0.6,  0.8,  1. ],
			colors = ['k', 'k', 'k', 'k', 'k', 'k', 'w', 'w', 'w', 'w', 'w'])
		ax.clabel(mesh, inline=True, fontsize=10, fmt = '%.1f',
			colors = ['k', 'k', 'k', 'k', 'k', 'k', 'w', 'w', 'w', 'w', 'w'])
	else:
		cb = fig.colorbar(mesh, ax=ax, aspect=30, fraction = 0.15, pad = 0.01, format='$%.1f$')
		cb.solids.set_edgecolor("face")
#		setupAxis_single(cb, cb, opts, 'z')
		cb.set_label(opts.get('zlabel', 'z'), ha = 'right', va = 'top', y = 1, size = 11.5,
			labelpad = opts.get('zpad', None))
	if 'notesize' in opts and 'notecolor' in opts :
		drawAnnotation(ax, opts.get('notes', []), {'fontsize': opts.get('notesize'), 'color': opts.get('notecolor')})
	elif 'notesize' in opts:
		drawAnnotation(ax, opts.get('notes', []), {'fontsize': opts.get('notesize')})
	else:
		drawAnnotation(ax, opts.get('notes', []))
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
