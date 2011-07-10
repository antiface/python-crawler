import os


def makedirs(path, mode=0777):
    if os.path.exists:
        if os.path.isdir(path):
            return
    os.makedirs(path, mode)


def strip_unicode(s):
    return ''.join([c for c in s if ord(c) < 128])
