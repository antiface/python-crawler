
class ModelNode(object):
    NS = {'x': 'http://www.w3.org/1999/xhtml'}

    def __init__(self, node):
        self.node = node

    def xpath(self, query):
        return self.node.xpath(query, namespaces=ModelNode.NS)

    def __getattr__(self, name):
        return getattr(self.node, name)


class Table(ModelNode):
    @property
    def rows(self):
        for n in self.iterchildren(tag='{http://www.w3.org/1999/xhtml}tbody'):
            for row in Table(n).rows:
                yield row

        for n in self.iterchildren(tag='{http://www.w3.org/1999/xhtml}tr'):
            yield TableRow(n)

    def __iter__(self):
        return self.rows

class TableRow(ModelNode):
    @property
    def cells(self):
        for n in self.headers:
            yield n
        for n in self.data:
            yield n

    @property
    def headers(self):
        for n in self.iterchildren(tag='{http://www.w3.org/1999/xhtml}th'):
            yield ModelNode(n)

    @property
    def data(self):
        for n in self.iterchildren(tag='{http://www.w3.org/1999/xhtml}td'):
            yield ModelNode(n)

    def __iter__(self):
        return self.data
