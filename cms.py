from plot import doPlot, do2DPlot

def setCMSsettings(opts):
	cms_style = opts.get('cms-style', 'default')

	opts.setdefault('title', r'\textbf{CMS} \textit{preliminary}')
	infostr = []
	lumi = opts.get('lumi')
	if lumi:
		lumi_str = '%.1f\,\mathsf{pb}^{-1}' % lumi
		if lumi >= 1000:
			lumi_str = '%.1f\,\mathsf{fb}^{-1}' % (lumi / 1000.)
		infostr.append({
			'default': r'$\mathcal{L} = %s$' % lumi_str,
			'pub': r'$%s$' % lumi_str,
		}[cms_style])
	if opts.get('cme'):
		infostr.append({
			'default': r'$\sqrt{s} = %s\,\mathsf{TeV}$' % opts.get('cme'),
			'pub': r'$(%s\,\mathsf{TeV})$' % opts.get('cme'),
		}[cms_style])
	if infostr:
		opts.setdefault('infostr', str.join(' ', infostr))


def doCMSPlot(fn, opts, plots, **kwargs):
	opts = dict(opts)
	setCMSsettings(opts)
	doPlot(fn, opts, plots, **kwargs)


def doCMS2DPlot(fn, opts, src):
	opts = dict(opts)
	setCMSsettings(opts)
	do2DPlot(fn, opts, src)
