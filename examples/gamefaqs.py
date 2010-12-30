from crawler.fetch import Fetcher, CachedFetcher
from crawler.engine import FetchEngine
from crawler.parse import HtmlParser
from crawler.map import URLMapper
from urlparse import urlsplit
import os.path

class SystemsPageParser(HtmlParser):
  __REPR_METADATA__ = ['systems']
  """ Parse the systems base uris and their names from the systems list page """
  DEFAULT_URI = 'http://www.gamefaqs.com/systems.html'

  def _parse(self):
    HtmlParser._parse(self)
    results = {}
    for n0 in self.xpath('descendant::x:div[@class="pod"]'):
      for n1 in self.xpath('descendant::x:a', n0):
        if n1.text:
          results[n1.text] = System(n1.text, n1.attrib['href']) 
    self.systems = results.values()

class System:
  """ Object wrapper for a System parsed by the Systems page parser """
  def __init__(self, name, uri):
    self.name = name
    self.uri = uri

  def __repr__(self):
    return "<System '%s'>" % self.name

class FaqPageParser(HtmlParser):
  """ Parse the FAQ body from a faq page """
  def _parse(self):
    HtmlParser._parse(self)
    self.faq = self.xpath('//x:div[@id="body"]/x:pre')[0].text

class GameDataPageParser(HtmlParser):
  __REPR_METADATA__ = ['metadata']
  """ Parse a game's info from its Data Page """
  def _parse(self):
    HtmlParser._parse(self)
    metadata = {}
    title_data = {}
    ul_title_data = self.xpath('//x:ul[@class="details title_data"]')[0]
    for li in ul_title_data:
      for span in li:
        if span.attrib['class'] == 'label':
          key = span.text
        if span.attrib['class'] == 'data':
          value = self.get_text(span)

      title_data[key] = value
    metadata['title_data'] = title_data
    self.metadata = metadata

class GFMapper(URLMapper):
  def _add_routes(self):
    base_game_path = r'/{console:[^/]+}/{game_id:\d+}-' \
                     r'{game_name:[^/]+}'
    self.connect('faq', base_game_path + '/faqs/{faq_id:\d+}',
                   parser=FaqPageParser)
    self.connect('game_data', base_game_path + '/data',
                   parser=GameDataPageParser)
    self.connect('credit', '/features/credit/{credit_id:\d+}.html')
    self.connect('company', '/features/company/{company_id:\d+}.html')
    self.connect('games_list_alpha', r'/{console:[^/]+}/list-{list_alpha:[a-z0]}')
    self.connect('games_list', r'/{console:[^/]+}/list-{list_id:\d+}')
    self.connect('game_overview', base_game_path)


if __name__ == '__main__':
  fe = FetchEngine()

  # Seed the fetch engine with 
  fe.add('http://www.gamefaqs.com/psp/943347-kingdom-hearts-birth-by-sleep/data')

  mapper = GFMapper()
  while not fe.empty():
    uri = fe.next()
    metadata = mapper.match(uri) or {}

    ParserClass = metadata.get('parser', HtmlParser)

    print "Fetching '%s'..." % (uri)
    parsed = ParserClass(CachedFetcher(uri).fetch())
    print ' >> ', parsed

    for link in parsed.get_links():
      # Some people do messed up stuff... like put garbage whitespace in hrefs
      link = link.strip()

      # Let's not walk absolute links
      if link.startswith('http'):
        continue

      if link.startswith('javascript:'):
        continue

      if not link.startswith('/'):
        link = os.path.join(os.path.dirname(urlsplit(uri).path), link)

      # Maybe we want to include weights in the routes or prevent cross domain traversal
      # in the router instead of hardcoding the logic above
      fe.add('http://www.gamefaqs.com' + link)

