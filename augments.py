import matplotlib

def drawAnnotation(ax, notelist, opts = {}):
	for note_entry in notelist:
		note = dict(opts)
		if isinstance(note_entry, str):
			xp, yp, text = note_entry.split(',', 2)
			note.update({'x': xp, 'y': float(yp), 'label': text})
			if xp.startswith('r'):
				note.setdefault('ha', 'right')
				note['x'] = float(xp[1:])
			else:
				note['x'] = float(xp)
			note.setdefault('transform', 'axis')
		else:
			note.update(note_entry)

		tf = ax.transAxes
		if note.pop('transform', 'axis') == 'data':
			tf = ax.transData
		n_x = note.pop('x', 0)
		n_y = note.pop('y', 0)
		n_l = note.pop('label')
		n_xa = note.pop('ha', 'left')
		n_ya = note.pop('va', 'center')
		ax.text(n_x, n_y, n_l, ha = n_xa, va = n_ya, transform = tf, **note)


def drawArea(ax, xlim = None, ylim = None, **kwargs):
	opts = {'color': 'gray', 'alpha': 0.2, 'linewidth': 0}
	opts.update(kwargs)
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
	ax.add_patch(matplotlib.patches.Rectangle((xr[0], yr[0]), xr[1] - xr[0], yr[1] - yr[0], **opts))


def drawLines(ax, lines = [], **kwargs):
	def drawLine(drawfun, maxrange, vkey, rkey, draw_dict):
		value = draw_dict.pop(vkey)
		drawrange = draw_dict.pop(rkey, maxrange)
		drawfun(value, drawrange[0], drawrange[1], **draw_dict)

	if isinstance(lines, tuple): # ([hlines], [vlines])
		(hlines, vlines) = lines
		lines = []
		for hline in hlines:
			lines.append({'y': hline})
		for vline in vlines:
			lines.append({'x': vline})

	for line_dict in lines:
		if 'x' in line_dict:
			drawLine(ax.vlines, (ax.get_ylim()[0], ax.get_ylim()[1]), 'x', 'yrange', line_dict)
		else:
			drawLine(ax.hlines, (ax.get_xlim()[0], ax.get_xlim()[1]), 'y', 'xrange', line_dict)


def drawInfoText(opts, ax):
	title_plot = opts.get('title', '')
	if title_plot:
		ax.text(0, 1.01, title_plot, transform=ax.transAxes, ha='left', va='bottom', fontsize=opts.get('titlesize', 14))
	title_info = opts.get('infostr', '')
	if title_info:
		ax.text(1, 1.01, title_info, transform=ax.transAxes, ha='right', va='bottom', fontsize=opts.get('infostrsize', 11))
