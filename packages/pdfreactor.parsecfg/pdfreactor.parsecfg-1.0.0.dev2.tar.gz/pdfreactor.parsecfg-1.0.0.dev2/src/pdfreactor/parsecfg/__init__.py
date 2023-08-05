"""
pdfreactor.parsecfg: Configuration parser for PDFreactor client integrations
"""

# Python compatibility:
from __future__ import absolute_import, print_function

# from ._parse import make_parser, ControlStatement, ApiCall

if __name__ == '__main__':
  if 0:
      txt = '''
      strict on
      # don't forget that '.' OP:
      config.outputFormat = {
          type: OutputType.JPEG,
          width: 640,
      }
      '''
      # Standard library:
      from pprint import pprint

      # Logging / Debugging:
      from pdb import set_trace
      print(list(gen_restricted_lines(txt)))


      bogustxt = '''
      strict on
      # don't forget that '.' OP:
      config outputFormat = {
          type: OutputType.JPEG,
          width: 640,
      }
      '''
      print(list(gen_restricted_lines(bogustxt)))

      txt = '''
      strict on
      config.outputFormat = {
          type: OutputType.JPEG,
          width: 640,
      }
      '''
      set_trace() # b 104
      for tokens in gen_restricted_lines(txt):
          pprint(tokens)
          # pprint(resolve_tokens(tokens))

  else:
    # Standard library:
    import doctest
    doctest.testmod()
