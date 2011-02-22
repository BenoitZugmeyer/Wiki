#!/usr/bin/python2
# ReSt Wiki in 100 lines
# http://www.asynchronous.org/rstiki/index.cgi

# Python http://pypi.python.org/pypi/GitPython/0.3.1-beta2

import pprint
import os
import os.path
import sys
import urllib
import urlparse
import mimetypes
import re
import traceback
import docutils.core

import pygmentsrst

import breve
import breve.tags.html

root_path = os.path.abspath(os.path.dirname(__file__))
repository_path = os.path.abspath(os.path.join(root_path, '..'))
templates_path = os.path.join(root_path, 'templates')
static_path = os.path.join(root_path, 'static')
index_name = 'Index'


def droptags(str):
    return re.sub("< */? *\w+ */?\ *>", "", str)

breve.register_global('urlescape', urllib.quote)
breve.register_global('droptags', droptags)


html_escape_table = {
    "&": "&amp;",
    '"': "&quot;",
    "'": "&apos;",
    ">": "&gt;",
    "<": "&lt;",
    }


def html_escape(text):
    return "".join(html_escape_table.get(c, c) for c in text)


def render_template(name, vars={}):
    template = breve.Template(breve.tags.html.tags,
        tidy=True,
        debug=True,
        root=templates_path,
        doctype='<!DOCTYPE html>')
    return template.render(name, vars).encode('UTF-8')


def render_rst(content):
    # http://docutils.sourceforge.net/docs/howto/security.html
    heightened_security_settings = {'file_insertion_enabled': 0,
                                    'raw_enabled': 0}
    # http://docutils.sourceforge.net/docs/api/publisher.html
    parts = docutils.core.publish_parts(source=content, writer_name='html',
        settings_overrides=heightened_security_settings)

    return {
        'file_title': parts['title'],
        'file_subtitle': parts['subtitle'],
        'file_content': parts['fragment']}


def parse_post(environment):
    if environment['REQUEST_METHOD'] != 'POST':
        return {}
    raw = environment['wsgi.input'].read() \
        .split('&')
    return dict([urllib.unquote_plus(p) for p in s.partition('=')[::2]]
        for s in raw)


def application(environment, response):
    file_path, command_name = environment['PATH_INFO'].partition('.')[::2]
    method = environment['REQUEST_METHOD']

    file_path = file_path.rstrip('/')
    localfile_path = os.path.join(repository_path,
        file_path.lstrip('/').replace('/', os.sep))

    if os.path.isdir(localfile_path):
        file_path = '/'.join((file_path, index_name))
        localfile_path = os.path.join(localfile_path, index_name)

    command_kwargs = parse_post(environment)

    if not command_name:
        command_name = 'view'
        command_args = []
    else:
        command_args = command_name.split('/')
        command_name = command_args.pop(0)

    header = {
        'status': '200 OK',
        'Content-Type': 'text/html'}

    body = run(
        command_name,
        header=header,
        file_path=file_path,
        localfile_path=localfile_path,
        file_name=os.path.basename(localfile_path),
        method=method,
        *command_args,
        **command_kwargs)

    response(header.pop('status'), header.items())
    return body


def run(name, *args, **kwargs):
    command = globals().get('command_' + name)
    if command:
        try:
            result = command(*args, **kwargs)
        except TypeError, e:
            return run('error', message='Arguments error')

        if result is None or isinstance(result, dict):
            if result:
                kwargs.update(result)
            result = render_template(name, kwargs)
    else:
        result = run('error',
            message='Command "{0}" not found'.format(html_escape(name)))
    return result


def command_error(message, exception=None, **kwargs):
    return {'exception': sys.exc_info()[0] and traceback.format_exc()}


def read_file(file_path):
    result = None
    if os.path.isfile(file_path):
        with open(file_path, 'rb') as fp:
            result = fp.read()
    return result


def command_view(localfile_path, file_name, **kwargs):
    file_content = read_file(localfile_path)
    file_exists = file_content is not None
    rendered = render_rst(file_content) if file_exists else {}
    rendered.update({'file_exists': file_exists})
    return rendered


def command_edit(localfile_path, header, file_path, content=None, **kwargs):
    if content is not None:
        with open(localfile_path, 'wb') as fp:
            fp.write(content)
        header['status'] = '302 Found'
        header['Location'] = file_path

    file_content = read_file(localfile_path)
    file_exists = file_content is not None
    return {
        'file_exists': file_exists,
        'file_content': file_content or ''}


def command_static(*file_path, **kwargs):
    header = kwargs['header']
    if not file_path or '..' in file_path:
        header['status'] = '403 Forbidden'
        return run('error', 'Forbidden')

    content = read_file(os.path.join(static_path, *file_path))
    if content is None:
        header['status'] = '404 Not found'
        return run('error',
            message='File "{0}" not found'.format('/'.join(file_path)),
            **kwargs)

    header['Content-Type'] = mimetypes.guess_type(file_path[-1])[0]
    return content


import bjoern
try:
    bjoern.run(application, '0.0.0.0', 8080)
except:
    pass
