
import breve
import breve.tags.html
import re
import urllib

import datetime

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
    action = '&'.join([
        '='.join([urllib.quote(str(p))
            for p in (part if isinstance(part, tuple) else (part, ))
        ])
        for part in action])
    return '?'.join((file, action))


@breve_global
def static(file):
    return url(action=['static', file])


@breve_global
def format_date(d):
    if isinstance(d, int) or isinstance(d, float):
        d = datetime.datetime.fromtimestamp(d)
    now = datetime.datetime.today()
    absolute = d.strftime(
        '%m-%d-%y %H:%M' if now.year != d.year else
        '%m-%d %H:%M' if now.month != d.month or now.day != d.day else
        '%H:%M')

    diff = now - d
    days = diff.days
    months = days / 30
    years = days / 365
    seconds = diff.seconds
    minutes = seconds / 60
    hours = seconds / 3600
    value, name = (
        (years, 'year') if years else
        (months, 'month') if months else
        (days, 'day') if days else
        (hours, 'hour') if hours else
        (minutes, 'minute') if minutes else
        (seconds, 'second'))
    relative = '{0} {1}{2} ago'.format(value, name, 's' if value > 1 else '')

    return breve.tags.html.tags.span(class_='date', title=relative)[absolute]


_size_units = ['', 'K', 'M', 'G', 'T', 'P']


@breve_global
def format_size(size):
    idx = 0
    rest = 0
    while True:
        nextsize, nextrest = divmod(size, 1024)
        if not nextsize:
            break
        idx += 1
        size, rest = nextsize, nextrest
    if rest > 5:
        format = '{:.3} {}byte{}'
        size += rest / 1024.
    else:
        format = '{} {}byte{}'
    return format.format(size, _size_units[idx], 's' if size > 1 else '')
    # Note: in french, units are taking a 's' if it is >= 2


breve.register_global('urlescape', urllib.quote)


def render_template(name, vars={}):
    template = breve.Template(breve.tags.html.tags,
        tidy=True,
        debug=True,
        root=conf.templates_path,
        doctype='<!DOCTYPE html>')
    return template.render(name, vars).encode('UTF-8')
