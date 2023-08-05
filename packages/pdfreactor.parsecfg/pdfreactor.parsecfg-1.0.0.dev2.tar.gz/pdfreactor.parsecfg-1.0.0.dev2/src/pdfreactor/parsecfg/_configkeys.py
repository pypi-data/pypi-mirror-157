# -*- coding: utf-8
"""
pdfreactor.parsecfg._configkeys: info about PDFreactor config keys

vim:
%s;^\(\s\+\)\('[^',]\+'\):;\1(\2,):;
"""

def Resource(*args):
    """
    This is needed e.g. for userStyleSheets and integrationStyleSheets; see:
    https://www.pdfreactor.com/product/doc/webservice/python.html#Resource

    >>> Resource('++resource++pdfreactor.plone/export.css')
    {'uri': '++resource++pdfreactor.plone/export.css'}

    For now, we only support a single argument which will be interpreted as the URI.

    >>> Resource('++resource++pdfreactor.plone/export.css', 'more-styles.css')
    Traceback (most recent call last):
      ...
    ValueError: Too many arguments; for now, we only support a single URI!

    """
    if args[1:]:
        raise ValueError('Too many arguments;'
                ' for now, we only support a single URI!')
    return {'uri': args[0]}


_factories = {
        ('disableLinks',): bool,
        ('outputFormat',): dict,
        ('outputFormat', 'type'): str,
        ('outputFormat', 'width'): int,
        ('outputFormat', 'height'): int,
        ('integrationStyleSheets',): list,
        ('integrationStyleSheets', None): Resource,
        ('userStyleSheets',): list,
        ('userStyleSheets', None): Resource,
        }


if __name__ == '__main__':
    # Standard library:
    import doctest
    doctest.testmod()
