from .util import makedirs

try:
    from ._curlfetch import CurlFetcher as Fetcher
except ImportError:
    raise ImportError('You need pycurl to run crawler')


import urllib 
import os.path


class CachedFetcher(Fetcher):
  __CACHE_DIR__ = '/tmp/fetchcache'
  def _check_dir(self):
    """ makes the __CACHE_DIR__ for this instance if it doesn't exist """
    makedirs(self.__CACHE_DIR__)

  def get_url_cache_file(self):
    """ Returns the response body cache filename for this url """
    return os.path.join(self.__CACHE_DIR__, urllib.quote(self.url, ''))

  def get_headers_cache_file(self):
    """ Returns the response headers cache filename for this url """
    return self.get_url_cache_file() + ".headers"

  def _fetch_from_cache(self):
    """ helper function; reassigns internal stream objects from the
        cached copies instead of the StreamIO's created by Fetcher """
    self._response_io = open(self.get_url_cache_file(), 'r')
    self._headers_io = open(self.get_headers_cache_file(), 'r')
    self._postfetch()

  def _perform_curl(self):
    Fetcher._perform_curl(self)

    # If we performed a curl, it wasn't in the cache.  Go ahead
    # and write the headers and response body out to a file.
    with open(self.get_url_cache_file(), 'w') as fbody:
      self._response_io.seek(0)
      fbody.write(self._response_io.read())
    self._response_io.seek(0)

    with open(self.get_headers_cache_file(), 'w') as fhead:
      self._headers_io.seek(0)
      fhead.write(self._headers_io.read())
    self._headers_io.seek(0)

  def fetch(self):
    """ Override fetch to check the cache first """
    if not self.fetched:
      self._check_dir()
      path = self.get_url_cache_file()
      if os.path.exists(path):
        self._fetch_from_cache()

    return Fetcher.fetch(self)

