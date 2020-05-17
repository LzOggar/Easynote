from django.template.library import Library

register = Library()

@register.filter
def xsplit(l, x):
	"""
		xsplit function. Split a string separate with blank space and return the x first members of the list.
		:param l: must be a string separate with blank space
		:param x: must be an integer
		:return: return the x first members of the list
		:rtype: <str>
	"""

	if x >= 0 and x < len(l):
		return "".join(l.split()[x])

	return ""