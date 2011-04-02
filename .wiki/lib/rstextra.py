
import docutils.core
import sys
import re


def render_content(content):
    if content is None:
        return {'file_title': None, 'file_subtitle': None,
            'file_content': None, 'error_count': 0}

    # http://docutils.sourceforge.net/docs/howto/security.html
    heightened_security_settings = {'file_insertion_enabled': 0,
                                    'raw_enabled': 0}

    stderr = sys.stderr
    sys.stderr = None
    parts = docutils.core.publish_parts(source=content, writer_name='html',
        settings_overrides=heightened_security_settings)
    sys.stderr = stderr

    # replaces errors
    content, error_count = \
        re.subn(r'(<div class="system-message"(?: id="id\d*?")?>)\n' \
            r'.*?\(.*?((?: line \d+)?)\)((?:; <em>.*?</em>)?)</p>\n' \
            r'(.*?)(</div>)',
            r'\1Error\2\3: \4\5', parts['fragment'], 0, re.S)

    return {
        'file_title': parts['title'],
        'file_subtitle': parts['subtitle'],
        'file_content': content,
        'error_count': error_count}


"""
    The Pygments reStructuredText directive
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This fragment is a Docutils_ 0.5 directive that renders source code
    (to HTML only, currently) via Pygments.

    To use it, adjust the options below and copy the code into a module
    that you import on initialization.  The code then automatically
    registers a ``sourcecode`` directive that you can use instead of
    normal code blocks like this::

        .. sourcecode:: python

            My code goes here.

    If you want to have different code styles, e.g. one with line numbers
    and one without, add formatters with their names in the VARIANTS dict
    below.  You can invoke them instead of the DEFAULT one by using a
    directive option::

        .. sourcecode:: python
            :linenos:

            My code goes here.

    Look at the `directive documentation`_ to get all the gory details.

    .. _Docutils: http://docutils.sf.net/
    .. _directive documentation:
       http://docutils.sourceforge.net/docs/howto/rst-directives.html

    :copyright: Copyright 2006-2010 by the Pygments team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

# Options
# ~~~~~~~

# Set to True if you want inline CSS styles instead of classes
INLINESTYLES = True

from pygments.formatters import HtmlFormatter

from pygments.styles import STYLE_MAP

# The default formatter
DEFAULT = HtmlFormatter(noclasses=INLINESTYLES)

# Add name -> formatter pairs for every variant you want to use
VARIANTS = {
    'linenos': HtmlFormatter(noclasses=INLINESTYLES, linenos=True),
}

for style in STYLE_MAP.keys():
    VARIANTS[style] = HtmlFormatter(noclasses=INLINESTYLES, style=style)

from docutils import nodes
from docutils.parsers.rst import directives, Directive

from pygments import highlight
from pygments.lexers import get_lexer_by_name, TextLexer


class Pygments(Directive):
    """ Source code syntax hightlighting.
    """
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = dict([(key, directives.flag) for key in VARIANTS])
    has_content = True

    def run(self):
        self.assert_has_content()
        try:
            lexer = get_lexer_by_name(self.arguments[0])
        except ValueError:
            # no lexer found - use the text one instead of an exception
            lexer = TextLexer()
        # take an arbitrary option if more than one is given
        formatter = self.options and \
            VARIANTS[self.options.keys()[0]] or DEFAULT
        parsed = highlight(u'\n'.join(self.content), lexer, formatter)
        return [nodes.raw('', parsed, format='html')]

directives.register_directive('sourcecode', Pygments)
