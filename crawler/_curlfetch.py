import pycurl
from ._fetchbase import BaseFetcher
from cStringIO import StringIO


class CurlFetcher(BaseFetcher):
  """ Basic pycurl-based fetcher """
  rawheaders = None
  _handle = None

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

    # If no cookie file is set, don't use it
    cookiefile = self.cookies.get_cookie_file()
    if cookiefile:
      self._handle.setopt(pycurl.COOKIEFILE, cookiefile)
      self._handle.setopt(pycurl.COOKIEJAR, cookiefile)

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


