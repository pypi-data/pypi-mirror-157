"""
oldmethods: Map old API method calls (i.e., their arguments) to config keys of
the new PDFreactor client API,
and provide a conversion function.

As far as "symbols" are involved (like CLEANUP_CYBERNEKO and the like), we
have a mapping of the old names to the new values already in ./oldsymbols.py.
This is not used yet, though.

Here is what we have already.
We'll use a little test helper function:

    >>> from pdfreactor.parsecfg.convert import parse_configuration
    >>> def om(cfgtext):
    ...     config = parse_configuration(cfgtext, convert=convert_api_method)
    ...     return sorted(config.items())

    >>> om('enableDebugMode();setAddLinks(yes)')
    ... # doctest: +NORMALIZE_WHITESPACE
    [('debugSettings', {'appendLogs': True}),
     ('disableLinks',    False)]

NOTE:
    There has been a change in the symbols which have been provided for such
    calls; the CLEANUP_NONE symbol, to take one, was "renamed" to Cleanup.NONE
    (there is an 'Cleanup' attribute now to the PDFreactor class, which is a
    mini class itself and provides some names).
    The values have changed as well; while they used to be numeric, they are
    now strings, usually containing a trailing part of the name.

    There is no transformation of such values yet!
"""

# Python compatibility:
from __future__ import absolute_import, print_function

from pdfreactor.parsecfg.convert import resolve_value

def negate(val):
    # negate the given value
    return not val

def unsupported(val):
    raise ValueError('The use of this method can\'t be converted '
                     'to some config key in the new PDFreactor API!')


map2 = {
    'setOutputFormat': [{
        'key': 'outputType',
        'subkey': 'type',
        }, {
        'key': 'outputType',
        'subkey': 'width',
        }, {
        'key': 'outputType',
        'subkey': 'height',
        }],
    'setCleanupTool': [{  # _new.Cleanup symbols
        'key': 'cleanupTool',
        }],
    'setEncoding': [{
        'key': 'encoding',
        }],
    'setJavaScriptMode': [{  # _new.JavaScriptMode symbols
        'key': 'javaScriptMode',
        }],
    'setAddBookmarks': [{
        'key': 'addBookmarks',
        }],
    'setAddLinks': [{
        'key': 'disableLinks',
        'convert': negate,
        }],
    'setAppendLog': [{
        'key': 'debugSettings',
        'subkey': 'appendLogs',
        }],
    'setDocumentType': [{
        'key': 'documentType',
        }],
    'setLicenseKey': [{  # not to be confused with the PDFreactor.apiKey attribute!
        'key': 'licenseKey',
        }],
    # https://www.pdfreactor.com/product/doc_html/#Logging
    'setLogLevel': [{  # _new.logLevel symbols
        'key': 'logLevel',
        }],
    }


def _specs(liz):
    if not liz:
        return
    elif not liz[1:]:
        yield 'val'
        return
    res = []
    for dic in liz:
        yield dic['subkey']


def convert_api_method(statement, config, control):  #  [[
    """
    Convert API methods (which are not used in the Python client API anymore)
    in config key assigments.

    Since this function is used as a `convert` argument to the
    parse_configuration function, we need to have a config and control dict,
    and we'll return a boolean value.

    >>> from pdfreactor.parsecfg.parse import generate_statements
    >>> def first_stmt(txt):
    ...     return list(generate_statements(txt))[0]
    >>> config = {}
    >>> ctrl = {}
    >>> stmt = first_stmt('the_answer=41')
    >>> convert_api_method(stmt, config, ctrl)
    False

    Well, this function doesn't convert assignments;
    so it returns False to allow you to try something else.

    For our further tests, we'll use a little test helper:
    >>> def cvt(txt, which='config'):
    ...     config = {}
    ...     control = {}
    ...     for stmt in generate_statements(txt):
    ...         res = convert_api_method(stmt, config, control)
    ...         print(res)
    ...     if which in ('config', 'both'):
    ...         print(sorted(config.items()))
    ...     if which in ('control', 'both'):
    ...         print(sorted(control.items()))

    >>> cvt('setAddLinks(yes)')
    True
    [('disableLinks', False)]

    >>> cvt('enableDebugMode()')
    True
    [('debugSettings', {'appendLogs': True})]

    """
    if not statement.is_method_call:
        return False

    grp0 = statement[0]
    the_name = grp0.dotted_name

    # TODO: create something generic, based on the map2 data!
    if the_name == 'setAddLinks':
        args = statement.method_args
        if args[1:]:
            tail = args[1]
            raise ValueError('Superfluous argument(s) in %(statement)r: '
                    '%(tail)r(...)' % locals())
        elif not args:
            val = True
        else:
            val = resolve_value(args[0])
            if not isinstance(val, int):
                raise ValueError('%(the_name)s(val) is expected to be a boolean '
                        '(or int); found %r' % (type(val),))
        control['add_links'] = val  # add_links_value
        config['disableLinks'] = not val
        return True
    elif the_name == 'enableDebugMode':
        args = statement.method_args
        if args:
            tail = args[0]
            raise ValueError('The %(the_name)s method doesn\'t expect arguments;'
                    'found %(tail)r' % locals())
        dic = config.setdefault('debugSettings', {})
        dic['appendLogs'] = True
        return True
    else:
        return False

if __name__ == '__main__':
  if 0:
    from six.moves import zip

    dictnames = set()
    nodicts = set()

    for name in sorted(map2.keys()):
        args = map2[name]
        specs = list(_specs(args))
        arglist = ', '.join(specs)
        print('%(name)s(%(arglist)s) -->' % locals())
        for spec, dic in zip(specs, args):
            try:
                key = dic['key']
            except KeyError:
                print('    (UNSUPPORTED)')
            else:
                if dic.get('convert'):
                    spec = '(converted) ' + spec
                if 'subkey' in dic:
                    subkey = dic['subkey']
                    assert key not in nodicts
                    dictnames.add(key)
                    print('    config[%(key)r][%(subkey)r] = %(spec)s' % locals())
                else:
                    assert key not in dictnames
                    nodicts.add(key)
                    print('    config[%(key)r] = %(spec)s' % locals())
  else:
    # Standard library:
    import doctest
    doctest.testmod()
