# TODO: precision parameters

def format_exp(x, mode = 'latex', prec = 1):
	if x == 0:
		return '$0$'
	result = ('%' + str(prec) + '.2e') % x
	if mode == 'latex':
		tmp = tuple(map(float, result.split('e')))
#		if abs(tmp[0] - 1.0) < 10**(-prec-1):
#			return '$10^{%d}$' % tmp[1]
#		else:
		return ('$%.' + str(prec) + 'f\cdot 10^{%d}$') % tmp
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
