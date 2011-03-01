
import docutils.core
import pygmentsrst
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
