from .cookies import CookieFile

class BaseFetcher(object):
    cookies = CookieFile()

    def __init__(self, url):
        self.url = url
        self.fetched = False

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass
