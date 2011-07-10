import html5lib
from cStringIO import StringIO
from .model import ModelNode

class HtmlParser():
  __REPR_METADATA__ = []

  def __init__(self, stream):
    self._stream = stream
    self._parse()

  def _parse(self):
    self.document = html5lib.parse(self._stream, treebuilder="lxml")

  def xpath(self, query, node = None):
    return ModelNode(node or self.document).xpath(query)

  @classmethod
  def from_string(cls, s):
    f = StringIO(s)
    f.seek(0)
    return cls(f)

  def get_links(self):
    return self.xpath('descendant::x:a/@href')

  def get_text(self, node):
    if node.text:
      return node.text

    s = ''
    for node in node.iterchildren():
      s += self.get_text(node)

    return s

  def __repr__(self):
    s = '<' + self.__class__.__name__
    for attr in self.__REPR_METADATA__:
      s += " " + attr + "=" + str(getattr(self, attr))
    s += '>'
    return s


