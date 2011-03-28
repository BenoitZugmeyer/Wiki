
import breve
import breve.tags.html
import re
import urllib

import conf


def breve_global(fct):
    breve.register_global(fct.__name__, fct)
    return fct


@breve_global
def droptags(str):
    return re.sub("< */? *\w+ */?\ *>", "", str)


@breve_global
def url(file='', action=None):
    file = urllib.quote(file)
    if action is None:
        return file
    if isinstance(action, str):
        action = (action,)
    action = '&'.join([urllib.quote(part) for part in action])
    return '?'.join((file, action))


@breve_global
def static(file):
    return url(action=['static', file])


breve.register_global('urlescape', urllib.quote)


def render_template(name, vars={}):
    template = breve.Template(breve.tags.html.tags,
        tidy=True,
        debug=True,
        root=conf.templates_path,
        doctype='<!DOCTYPE html>')
    return template.render(name, vars).encode('UTF-8')
