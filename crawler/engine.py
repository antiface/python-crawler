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
