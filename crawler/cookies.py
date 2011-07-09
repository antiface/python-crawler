from .util import makedirs
import os.path


class CookiesBase(object):
    pass


class NoCookies(CookiesBase):
    def get_cookie_file(self):
        return None


class CookieFile(CookiesBase):
    __COOKIEFILE__ = '/tmp/pycurl-cookies'

    def get_cookie_file(self):
        return self.__COOKIEFILE__


class CookieFilePool(CookiesBase):
    __COOKIEFILEPATH__ = '/tmp/pycurl-cookie-pool'
    __NUMJARS__ = 10
    _current_index = None

    def __init__(self):
        makedirs(self.__COOKIEFILEPATH__)
        self._current_index = 0

    def get_cookie_file(self):
        p = os.path.join(self.__COOKIEFILEPATH__,
                         "_cf_%d" % (self._current_index))
        self._current_index = (self._current_index + 1) % \
                              self.__NUMJARS__
        return p



