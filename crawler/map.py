from routes import Mapper
from urlparse import urlsplit

class URLMapper():
  """ Unlike the normal routes.Mapper, URLMapper works on urls with scheme, etc...
      Except, right now it doesn't really; eventually, make this match stuff """
  def __init__(self):
    self.mapper = Mapper()
    self._add_routes()

  def _add_routes(self):
    """ override this in the subclass to add routes at create-time """
    pass

  def make_path_with_query(self, parsed):
    if parsed.query:
      return parsed.path + '/' + parsed.query
    return parsed.path

  def match(self, uri):
    parsed = urlsplit(uri, 'http')
    path = self.make_path_with_query(parsed)

    if not path:
      return None

    return self.mapper.match(path)

  def connect(self, *args, **kwargs):
    #domain = kwargs.get('domain', '_default')
    return self.mapper.connect(*args, **kwargs)

