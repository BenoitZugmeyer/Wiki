#!/usr/bin/python2
# ReSt Wiki in 100 lines
# http://www.asynchronous.org/rstiki/index.cgi

# Python http://pypi.python.org/pypi/GitPython/0.3.1-beta2

import pprint
import os
import sys
import urllib
import urlparse
import mimetypes
import re
import traceback


import lib

import conf


def parse_kwargs(environment):
    if environment['REQUEST_METHOD'] == 'POST':
        raw = environment['wsgi.input'].read()
    else:
        #raw = environment.get('QUERY_STRING', '')
        raw = ''
    return dict([urllib.unquote_plus(p) for p in s.partition('=')[::2]]
        for s in raw.split('&'))


def application(environment, response):
    file_path = environment['PATH_INFO']
    method = environment['REQUEST_METHOD']
    command = environment.get('QUERY_STRING', '')

    file_path = file_path.rstrip('/')
    localfile_path = os.path.join(conf.repository_path,
        file_path.lstrip('/').replace('/', os.sep))

    if os.path.isdir(localfile_path):
        file_path = '/'.join((file_path, conf.index_name))
        localfile_path = os.path.join(localfile_path, conf.index_name)

    command_kwargs = parse_kwargs(environment)

    if not command:
        command_name = 'view'
        command_args = []
    else:
        command_args = command.split('&')
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
    command = get_command(name)
    if command:
        try:
            result = command(*args, **kwargs)
        except TypeError, e:
            return run('error', message='Arguments error', **kwargs)

        if result is None or isinstance(result, dict):
            if result:
                kwargs.update(result)
            result = lib.render_template(name, kwargs)
    else:
        result = run('error',
            message='Command "{0}" not found'.format(lib.html_escape(name)),
            **kwargs)
    return result


def read_file(file_path):
    result = None
    if os.path.isfile(file_path):
        with open(file_path, 'rb') as fp:
            result = fp.read()
    return result


_commands = {}


def command(fct):
    _commands[fct.__name__] = fct
    return fct


def get_command(name):
    return _commands.get(name)


@command
def error(message, exception=None, **_):
    return {'exception': sys.exc_info()[0] and traceback.format_exc()}


@command
def view(localfile_path, **_):
    return lib.render_content(read_file(localfile_path))


@command
def edit(localfile_path, header, file_path, method,
    content=None, preview=False, **_):

    rendered = lib.render_content(content)
    if content is not None and method == 'POST':
        if not rendered['error_count'] and not preview:
            with open(localfile_path, 'wb') as fp:
                fp.write(content)
            header['status'] = '302 Found'
            header['Location'] = file_path
            return ''
    else:
        content = read_file(localfile_path)
    rendered['content'] = content

    return rendered


@command
def static(*file_path, **kwargs):
    header = kwargs['header']
    if not file_path or '..' in file_path:
        header['status'] = '403 Forbidden'
        return run('error', message='Forbidden', **kwargs)

    content = read_file(os.path.join(conf.static_path, *file_path))
    if content is None:
        header['status'] = '404 Not found'
        return run('error',
            message='File "{0}" not found'.format('/'.join(file_path)),
            **kwargs)

    header['Content-Type'] = mimetypes.guess_type(file_path[-1])[0]
    return content


def launch(address, port):
    import bjoern
    bjoern.run(application, address, port)


if __name__ == '__main__':
    try:
        print "Start..."
        launch('0.0.0.0', 8080)
    except Exception, e:
        print e
