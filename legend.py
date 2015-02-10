import matplotlib

class MultiLineContainer(list):
	pass

def getPlotLabel(plot):
	try:
		return plot['label'] % plot['data']['meta']
	except:
		return plot.get('label')


def getHandlerMap(leg_opts):
	def updateRectFromPatches(legend_handle, orig_handle):
		legend_handle.set_hatch(orig_handle.get_hatch())
		legend_handle.set_alpha(orig_handle.get_alpha())
		legend_handle.set_linewidth(orig_handle.get_linewidth()[0])
		if orig_handle.get_facecolor().size:
			legend_handle.set_facecolor(orig_handle.get_facecolor()[0])
		if orig_handle.get_edgecolor().size:
			legend_handle.set_edgecolor(orig_handle.get_edgecolor()[0])

	def createRectangle(legend, orig_handle, xdescent, ydescent, width, height, fontsize):
		height = fontsize
		ydescent += fontsize * 0.1
		return matplotlib.patches.Rectangle(xy = (-xdescent, -ydescent), width = width, height = height)

	class HandlerMultiLine(matplotlib.legend_handler.HandlerLine2D):
		def create_artists(self, legend, orig_handle, xdescent, ydescent, width, height, fontsize, trans):
			result = []
			for idx, handle in enumerate(orig_handle):
				ydescent = height * (1 - 2 * idx / float(len(orig_handle) - 1))
				result.extend(matplotlib.legend_handler.HandlerLine2D.create_artists(
					self, legend, handle, xdescent, ydescent, width, height, fontsize, trans))
			return result

	errorbar_xs = leg_opts.pop('errorbar_xs', 1.25)
	errorbar_ys = leg_opts.pop('errorbar_ys', 0.6)
	class DummyLegendHandler:
		def __init__(self, fun):
			self.fun = fun
		def legend_artist(self, *args):
			return self.fun(*args)
	class CompositorHandler:
		def legend_artist(self, legend, orig_handle, *args):
			lmap = legend.get_legend_handler_map()
			for handle in orig_handle:
				legend.get_legend_handler(lmap, handle).legend_artist(legend, handle, *args)
	return {
		matplotlib.container.ErrorbarContainer: matplotlib.legend_handler.HandlerErrorbar(
			xerr_size = errorbar_xs, yerr_size = errorbar_ys),
		matplotlib.collections.PolyCollection: matplotlib.legend_handler.HandlerPatch(
			patch_func = createRectangle, update_func = updateRectFromPatches),
		matplotlib.container.BarContainer: matplotlib.legend_handler.HandlerPatch(
			patch_func = createRectangle, update_func = matplotlib.legend_handler.update_from_first_child),
		matplotlib.lines.Line2D: matplotlib.legend_handler.HandlerLine2D(),
		MultiLineContainer: HandlerMultiLine(),
		list: CompositorHandler(),
		None: DummyLegendHandler(lambda *args: None),
	}


def drawLegend(ax, plots, opts):
	for leg in set(map(lambda p: p.get('legend', ''), plots)):
		# Set default / Rewrite legend options
		leg_opts = dict(opts.get(('legend_%s' % leg).rstrip('_'), {}))
		leg_opts.setdefault('handlelength', 2.5)
		leg_opts.setdefault('numpoints', 1)
		leg_opts.setdefault('markerscale', 2)
		leg_opts.setdefault('ncol', leg_opts.pop('col', leg_opts.pop('ncols', leg_opts.pop('cols', 1))))
		leg_opts.setdefault('prop', matplotlib.font_manager.FontProperties(size = leg_opts.pop('size', 12)))
		locMap = {1: 3, 2: 8, 3: 4, 4: 6, 5: 10, 6: 7, 7: 2, 8: 9, 9: 1, 0: 0}
		leg_opts['loc'] = locMap[int(leg_opts.pop('loc', leg_opts.pop('pos', 0)))]
		leg_width = leg_opts.pop('width', 0)

		leg_plots = filter(lambda p: (p.get('legend', '') == leg) and (p.get('label') != None), plots)
		if not leg_plots:
			continue

		handler_map = getHandlerMap(leg_opts)
		ax.add_artist(matplotlib.legend.Legend(ax, map(lambda p: p.get('vis'), leg_plots),
			map(getPlotLabel, leg_plots), handler_map = handler_map, **leg_opts))
		if leg_width:
			box = ax.get_position()
			ax.set_position([box.xmin, box.ymin, box.width*(1 - leg_width), box.height])
