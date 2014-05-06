def drawAnnotation(ax, notelist, opts = {}):
	for note in notelist:
		if isinstance(note, str):
			xp, yp, text = note.split(',', 2)
			note = {'x': xp, 'y': float(yp), 'label': text}
			if xp.startswith('r'):
				note.setdefault('ha', 'right')
				note['x'] = float(xp[1:])
			else:
				note['x'] = float(xp)
			note.setdefault('transform', 'axis')

		tf = ax.transAxes
		if note.get('transform') == 'data':
			tf = ax.transData
		ax.text(note.get('x', 0), note.get('y', 0), note['label'],
			ha=note.get('ha', 'left'), va=note.get('va', 'center'), transform = tf, **opts)


def drawArea(ax, xlim = None, ylim = None, color = 'gray', alpha = 0.2):
	def getLimits(usr, axis):
		if not usr:
			return axis
		(low, high) = usr
		if not low:
			low = axis[0]
		if not high:
			high = axis[1]
		return (low, high)
	xr = getLimits(xlim, ax.get_xlim())
	yr = getLimits(ylim, ax.get_ylim())
	ax.add_patch(matplotlib.patches.Rectangle((xr[0], yr[0]), xr[1] - xr[0], yr[1] - yr[0],
		color=color, linewidth=0, alpha=alpha))


def drawLines(ax, hlines = [], vlines = [], **kwargs):
	for hline in hlines:
		ax.hlines(hline, ax.get_xlim()[0], ax.get_xlim()[1], **kwargs)
	for vline in vlines:
		ax.vlines(vline, ax.get_ylim()[0], ax.get_ylim()[1], **kwargs)


def drawInfoText(opts, ax):
	title_plot = opts.get('title', '')
	if title_plot:
		ax.text(0, 1.02, title_plot, transform=ax.transAxes, ha='left', va='bottom')
	title_info = opts.get('infostr', '')
	if title_info:
		ax.text(1, 1.02, title_info, transform=ax.transAxes, ha='right', va='bottom')
