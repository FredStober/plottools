# TODO: precision parameters

def format_exp(x, mode = 'latex'):
	result = '%1.2e' % x
	if mode == 'latex':
		tmp = tuple(map(float, result.split('e')))
		if tmp[0] == 1.0:
			return '$10^{%d}$' % tmp[1]
		else:
			return '$%d\cdot 10^{%d}$' % tmp
	return result

def format_unc(x, high, low, mode = 'latex'):
	if mode == 'latex':
		if high == low:
			return r'$%g \pm %g$' % (x, high)
		else:
			return r'$%g^{%g}_{%g}$' % (x, high, low)
	if high == low:
		return '%g +/- %g' % (x, high)
	else:
		return '%g +%g-%g' % (x, high, low)
