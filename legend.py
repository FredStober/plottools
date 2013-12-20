import matplotlib

def drawLegend(ax, plots, opts):
	legends = set()
	for plot in plots:
		legends.add(plot.get('legend', None))
	leg_vis = None
	for leg in legends:
		if leg_vis != None:
			ax.add_artist(leg_vis)
		name = 'legend'
		if leg != None:
			name = 'legend_%s' % leg
		leg_plots = filter(lambda p: p.get('legend', None) == leg, plots)
		leg_vis = drawLegend_int(ax, leg_plots, **opts.get(name, {}))
		if opts.get(name, {}).get('width', 0):
			box = ax.get_position()
			ax.set_position([box.xmin, box.ymin, box.width*(1-opts.get(name, {}).get('width', 0)), box.height])


def getPlotLabel(plot):
	if ('label' in plot) and ('meta' in plot['data']):
		return plot['label'] % plot['data']['meta']
	return plot.get('label')


def drawLegend_int(ax, plots, size = 12, loc = 0, cols = 1, bbox_to_anchor = None, **other):
	plots = filter(lambda p: p.get('label'), plots)
	proxy = map(lambda p: getLabelProxy(p['vis'], p), plots)
	labels = map(getPlotLabel, plots)
	locMap = {1: 3, 2: 8, 3: 4, 4: 6, 5: 10, 6: 7, 7: 2, 8: 9, 9: 1, 0: 0}
	loc = int(loc)
	loc = locMap[loc]
	if len(filter(lambda l: l != None, labels)) > 0:
		if bbox_to_anchor:
			return ax.legend(proxy, labels, prop=matplotlib.font_manager.FontProperties(size=size),
				handlelength=2.5, loc=loc, bbox_to_anchor=bbox_to_anchor, ncol=cols, numpoints=1)
		else:
			return ax.legend(proxy, labels, prop=matplotlib.font_manager.FontProperties(size=size),
				handlelength=2.5, loc=loc, ncol=cols, numpoints=1)


def getLabelProxy(p, pinfo):
	if type(p) is matplotlib.collections.PolyCollection:
		try:
			return matplotlib.patches.Rectangle((0, 0), 1, 1,
				lw = p.get_linewidth()[0], fc = p.get_facecolor()[0],
				ec = p.get_edgecolor()[0], alpha = p.get_alpha())
		except:
			return None
	else:
		try:
			marker = p[0].get_marker()
			linestyle = p[0].get_linestyle()
			if str(linestyle) == 'None':
				linestyle = '-'
			return matplotlib.lines.Line2D([0,1], [1,1], color=p[0].get_color(),
				linewidth=p[0].get_linewidth(), linestyle=linestyle,
				marker=marker, markersize=p[0].get_markersize() + 3,
				markeredgewidth=0.5, markerfacecolor=p[0].get_markerfacecolor(),
				markeredgecolor='k')
		except:
			return matplotlib.patches.Rectangle((0, 0), 1, 1,
				fc = p[0].get_facecolor(), ec = p[0].get_facecolor())
