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
import difflib

import lib

import conf


def parse_urlencoded(raw, args, kwargs):
    if not raw:
        return
    for cpl in raw.split('&'):
        name, sep, value = cpl.partition('=')
        name = urllib.unquote_plus(name)
        if sep:
            kwargs[name] = urllib.unquote_plus(value)
        else:
            args.append(name)


def parse_input(environment):
    args = []
    kwargs = {}
    parse_urlencoded(environment.get('QUERY_STRING', ''), args, kwargs)
    if environment['REQUEST_METHOD'] == 'POST':
        read = environment['wsgi.input'].read(int(environment.get('CONTENT_LENGTH', 0)))
        parse_urlencoded(read, args, kwargs)
    return args, kwargs


def application(environment, response):
    file_path = environment['PATH_INFO']
    method = environment['REQUEST_METHOD']

    file_path = file_path.rstrip('/')
    localfile_path = os.path.join(conf.repository_path,
        file_path.lstrip('/').replace('/', os.sep))

    if os.path.isdir(localfile_path):
        file_path = '/'.join((file_path, conf.index_name))
        localfile_path = os.path.join(localfile_path, conf.index_name)

    command_args, command_kwargs = parse_input(environment)

    header = {
        'status': '200 OK',
        'Content-Type': 'text/html'}

    body = run(
        command_args[0] if command_args else 'view',
        header=header,
        file_path=file_path,
        localfile_path=localfile_path,
        file_name=os.path.basename(localfile_path),
        file_exists=os.path.isfile(localfile_path),
        method=method,
        arguments=command_args,
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

def parseint(i, default=None):
    try:
        return int(i)
    except:
        return default

@command
def error(message, exception=None, **_):
    return {'exception': sys.exc_info()[0] and traceback.format_exc()}


@command
def view(localfile_path, **_):
    return lib.render_content(read_file(localfile_path))


@command
def edit(localfile_path, header, file_path, method, file_exists,
    content=None, preview=False, **_):

    rendered = lib.render_content(content)
    if content is not None and method == 'POST':
        if not rendered['error_count'] and not preview:
            file = lib.File(localfile_path)
            if file_exists:
                file.save()
            file.content = content
            header['status'] = '302 Found'
            header['Location'] = file_path
            return ''
    else:
        content = read_file(localfile_path)
    rendered['content'] = content

    return rendered


@command
def history(localfile_path, file_exists, new=None, old=None, see=None, **_):
    if not file_exists:
        return run('error', message='File not found', **_)

    see, new, old = parseint(see), parseint(new), parseint(old)
    file = lib.File(localfile_path)
    history = file.history()
    result = {'file': file, 'history': history, 'see': see, 'old': old, 'new': new}
    if see is not None:
        history_file = history[see] if see else file
        result.update(lib.render_content(history_file.content))
        result['history_file'] = history_file
    if new is not None and old is not None:
        old_content, new_content = [
            (history[i] if i else file).content.split('\n')
            for i in (old, new)]
        result['diff_content'] = ''.join([
            s if len(s) and s[-1] == '\n' else s + '\n'
            for s in difflib.unified_diff(old_content, new_content)])
    return result

@command
def static(header, arguments, **_):
    file_path = arguments[1]
    if not file_path or '..' in file_path:
        header['status'] = '403 Forbidden'
        return run('error', message='Forbidden', **kwargs)

    content = read_file(
        os.path.join(conf.static_path, file_path.replace('/', os.sep)))
    if content is None:
        header['status'] = '404 Not found'
        return run('error',
            message='File "{0}" not found'.format(file_path),
            **_)

    header['Content-Type'] = mimetypes.guess_type(file_path)[0]
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
