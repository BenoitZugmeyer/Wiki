#!/usr/bin/python2
# -*- coding: utf-8 -*-

import zlib
import os
import os.path
import datetime
import hashlib
import json
import time
import uuid

import tarfile
import StringIO

import conf


json_encode = json.JSONEncoder(separators=(',', ':')).encode
json_decode = json.JSONDecoder().raw_decode


class HistoryEntry(object):
    uname = None
    mtime = None
    size = None
    content = None


class _HistoryEntry(HistoryEntry):

    def __init__(self, tar, infos):
        self._infos = infos
        self._tar = tar
        self.uname = infos.uname
        self.mtime = infos.mtime
        self.size = infos.size

    @property
    def content(self):
        #return zlib.decompress(self._tar.extractfile(self._infos).read())
        return self._tar.extractfile(self._infos).read()


class History(object):

    def __init__(self, path):
        self._path = path
        if os.path.isfile(path):
            self._tar = tarfile.TarFile(path, 'r')
            self._files_iter = reversed(self._tar.getmembers())
        else:
            self._tar = False
            self._files_iter = iter([])

    def __del__(self):
        if self._tar:
            self._tar.close()

    def __iter__(self):
        return self

    def append(self, entry):
        content = entry.content
        infos = tarfile.TarInfo(hex(zlib.crc32(content)))
        #content = zlib.compress(content)
        infos.size = len(content)
        infos.uname = entry.uname or '-'
        infos.mtime = entry.mtime
        content = StringIO.StringIO(content)

        with tarfile.TarFile(self._path, 'a') as tar:
            tar.addfile(infos, content)

    def next(self):
        infos = self._files_iter.next()
        return _HistoryEntry(self._tar, infos)


class File(HistoryEntry):
    def __init__(self, name):
        self._name_hash = hashlib.sha1(name).hexdigest()
        self._name = name

    @property
    def content(self):
        with open(self.path, 'rb')as fp:
            result = fp.read()
        return result

    @content.setter
    def content(self, content):
        with open(self.path, 'wb') as f:
            f.write(content)

    def save(self):
        self.history().append(self)

    @property
    def path(self):
        return os.path.join(conf.repository_path, self._name)

    @property
    def hash_path(self):
        return os.path.join(conf.data_path, self._name_hash)

    @property
    def hash(self):
        return hashlib.sha1(self.content).digest()

    @property
    def mtime(self):
        return int(os.path.getmtime(self.path))

    @property
    def size(self):
        return os.path.getsize(self.path)

    def history(self):
        return History(self.hash_path)

    def delete():
        os.delete(self.path)
        os.delete(self.hash_path)

    def __repr__(self):
        return '<File {name} {hash}>'.format(**self.__dict__)


if __name__ == '__main__':
    import difflib

    def print_diff(a, b):
        for line in difflib.unified_diff(
            a.split('\n'),
            b.split('\n')):

            if line.endswith('\n'):
                print line,
            else:
                print line

    file = File('nyu')

    file.save()

    last_content = file.content

    i = 3
    for hi in file.history():
        i -= 1
        print 'Content from', hi.mtime
        content = hi.content
        print_diff(content, last_content)
        last_content = content
        if i == 0:
            break
