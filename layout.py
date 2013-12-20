from basic import *
from legend import *
from augments import *

def doPlot(fn, opts_raw, plots, **kwargs):
	opts = mergeOpts(opts_raw, kwargs)
	(fig, ax) = setupPlot(opts)

	title_plot = opts.get('title', '')
	if title_plot:
		ax.text(0, 1.02, title_plot, transform=ax.transAxes, ha='left', va='bottom')
	title_info = opts.get('infostr', '')
	if title_info:
		ax.text(1, 1.02, title_info, transform=ax.transAxes, ha='right', va='bottom')

	base_ax = ax

	plots = map(dict, plots) # convert PlotEntries to dictionaries
	plots_ax1 = filter(lambda p: p.get('data') and (p.get('axis', 1) == 1), plots)
	drawPlots(ax, plots_ax1, opts.get('plots', {}), opts.get('xy_switch', False))

	plots_ax2 = filter(lambda p: p.get('data') and (p.get('axis', 1) == 2), plots)
	if plots_ax2:
		xprefix = 'x'
		yprefix = 'y'
		if 'x2range' in opts:
			xprefix = 'x2'
			base_ax = base_ax.twiny()
		if 'y2range' in opts:
			yprefix = 'y2'
			base_ax = base_ax.twinx()
		setupAxis(base_ax, opts, xprefix = xprefix, yprefix = yprefix)
		drawPlots(base_ax, plots_ax2, opts.get('plots2', opts.get('plots', {})), opts.get('xy_switch', False))

	drawLegend(base_ax, plots, opts)
	if 'notesize' in opts:
		drawAnnotation(base_ax, opts.get('notes', []), {'fontsize': opts.get('notesize')})
	else:
		drawAnnotation(base_ax, opts.get('notes', []))
	if 'area' in opts:
		drawArea(base_ax, xlim = opts['area'].get('xlim'), ylim = opts['area'].get('ylim'))

	lines = kwargs.get('lines', ([], []))
	drawLines(base_ax, lines[0], lines[1], **opts_raw.get('lines', {}))
	if kwargs.get('fun'):
		kwargs.get('fun')(base_ax)
	savePlot(fig, fn)
