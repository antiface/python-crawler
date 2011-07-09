import os


def makedirs(path, mode=0777):
    if os.path.exists:
        if os.path.isdir(path):
            return
    os.makedirs(path, mode)
