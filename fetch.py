import pycurl
from cStringIO import StringIO

class Fetcher(object):
  """ Basic pycurl-based fetcher """

  __COOKIEFILE__ = '/tmp/pycurl-cookies'
  rawheaders = None
  _handle = None

  def __init__(self, url):
    self.url = url
    self.fetched = False

  def get_cookie_file(self):
    return self.__COOKIEFILE__

  def __enter__(self):
    return self

  def __exit__(self, type, value, traceback):
    self._cleanup_curl()

  def __del__(self):
    self._cleanup_curl()

  def _init_curl(self):
    self._handle = pycurl.Curl()
    self._response_io = StringIO()
    self._headers_io = StringIO()
    self._handle.setopt(pycurl.COOKIEFILE, self.get_cookie_file())
    self._handle.setopt(pycurl.COOKIEJAR, self.get_cookie_file())
    self._handle.setopt(pycurl.URL, self.url)
    self._handle.setopt(pycurl.WRITEFUNCTION, self._response_io.write)
    self._handle.setopt(pycurl.HEADERFUNCTION, self._headers_io.write)

  def _perform_curl(self):
    self._handle.perform()
    self._cleanup_curl()

  def _cleanup_curl(self):
    if self._handle:
      self._handle.close()
      self._handle = None

  def _postfetch(self):
    self._headers_io.seek(0)
    self.rawheaders = self._headers_io.read()
    self._response_io.seek(0)
    self.fetched = True

  def fetch(self):
    if not self.fetched:
      self._init_curl()
      self._perform_curl()
      self._postfetch()

    return self._response_io

import urllib 
import os.path

class CachedFetcher(Fetcher):
  __CACHE_DIR__ = '/tmp/fetchcache'
  def _check_dir(self):
    """ makes the __CACHE_DIR__ for this instance if it doesn't exist """
    try:
      os.mkdir(self.__CACHE_DIR__)
    except OSError:
      pass

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

import time
from collections import defaultdict

class FetchEngine():
  """ Helper class for queueing uris and such for fetch """
  def __init__(self):
    self.last_fetched = defaultdict(int)

    # omg use a fucking queue!  to_fetch.pop(0) has O(N)
    self.to_fetch = []
    self.queued = set()
    self.has_fetched = set()

  def empty(self):
    return len(self.to_fetch) <= 0

  def add(self, uri):
    """ Enqueue `uri` to the fetch engine """
    if uri in self.queued:
      return False

    self.to_fetch.append(uri)
    self.queued.add(uri)
    return True

  def next(self, keepout = 0):
    """ Return the next uri outside of `keepout`.  Returns None if
        there's nothing outside the keepout """
    last_check = None
    while len(self.to_fetch):
      uri = self.to_fetch.pop(0)

      # Break if we can't check any of these... shit!
      if last_check and last_check == uri:
        self.to_fetch.append(uri)
        break

      # Check if we're still behind the keepout
      if time.time() < self.last_fetched[uri] + keepout:
        # Re-enqueue this guy
        self.to_fetch.append(uri)
        last_check = uri
        continue

      self.queued.remove(uri)
      self.mark_fetched(uri)
      return uri

    raise Exception('Empty')

  def has_fetched(self, uri):
    return uri in self.last_fetched

  def mark_fetched(self, uri):
    self.last_fetched[uri] = time.time()
