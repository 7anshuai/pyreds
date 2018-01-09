#!/usr/bin/env python

import re

from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords
from pyreds.phonetics import metaphone
import redis

stemmer = PorterStemmer()
stop_words = set(stopwords.words('english'))

types = {
    'intersect': 'zinterstore',
    'union': 'zunionstore',
    'and': 'zinterstore',
    'or': 'zunionstore'
}

_ASCII_STR_RE = re.compile(r'[a-zA-Z0-9_]+')

_redis_client = None

def set_client(in_client):
    global _redis_client
    _redis_client = in_client

def create_client():
    global _redis_client
    if not _redis_client:
        _redis_client = redis.StrictRedis()
    return _redis_client

def create_search(key):
    if not key:
        raise ValueError('create_search() requires a redis key for namespacing.')

    return Search(key)

# Return the words in `str`.
def _words(s):
    return _ASCII_STR_RE.findall(str(s))

# Stem the given `words`.
def _stem(words):
    ret = []

    if not words:
        return ret

    for word in words:
        ret.append(stemmer.stem(word))

    return ret

# Strip stop words in `words`.
def _strip_stopwords(words):
    ret = []

    if not words:
        return ret

    for word in words:
        if word in stop_words:
            continue
        ret.append(word)

    return ret

# Return an object mapping each word in a list
# to the number of times it occurs in the list.
def _count_words(words):
    mapper = {}

    if not words:
        return mapper

    for word in words:
        if word not in mapper:
            mapper[word] = 1
        else:
            mapper[word] += 1

    return mapper

# Return the given `words` mapper to the metaphone constant.
#
# Examples:
#
#   metaphone_map([`tobi`, 'wants', '4', 'dollars'])
#   => {'4': '4', 'tobi': 'TB', 'wants': 'WNTS', 'dollars': 'TLRS'}
#
def _metaphone_map(words):
    mapper = {}

    if not words:
        return mapper

    for word in words:
        mapper[word] = metaphone(word)

    return mapper

# Return an list of metaphone constants in `words`.
#
# Examples:
#
#   metaphone_list(['tobi', 'wants', '4', 'dollars'])
#   => ['4', 'TB', 'WNTS', 'TLRS']
#
def _metaphone_list(words):
    ret = []

    if not words:
        return ret

    for word in words:
        constant = metaphone(word)
        if constant not in ret:
            ret.append(constant)

    return ret

# Return a map of metaphone constant redis keys for `words`
# and the given `key`.
def _metaphone_keys(key, words):
    return list(map(lambda c: key + ':word:' + c, _metaphone_list(words)))

# Initialize a new `Query` with the given `str`
# and `search` instance.
class Query:

    def __init__(self, txt, type, search):
        self.txt = txt
        self.type(type if type else 'and')
        self.between(0, -1)
        self.search = search

    # Set `type` to "union" or "intersect", aliased as
    # "or" and "and".

    def type(self, type):
        self._type = types[type] if type and type in types else types['and']
        return self

    # Limit search to the specified range of elements.
    def between(self, start, stop):
        self._start = start
        self._stop = stop
        return self

    # Perform the query
    def end(self):
        key = self.search.key
        db = self.search.client
        query = self.txt
        words = _stem(_strip_stopwords(_words(query)))
        keys = _metaphone_keys(key, words)
        type = self._type
        start = self._start
        stop = self._stop

        if not len(keys):
            return []

        tkey = key + 'tmpkey'
        pipe = db.pipeline()
        getattr(pipe, type)(tkey, keys)
        for cmd in [
            ['zrevrange', tkey, start, stop],
            ['zremrangebyrank', tkey, start, stop]
        ]:
            getattr(pipe, cmd[0])(*cmd[1:])

        ids = pipe.execute()
        return ids[1]

# Initialize a new `Search` with the given `key`.
class Search:

    def __init__(self, key):
        self.key = key
        self.client = create_client()

    # Index the given `str` mapped to `id`
    def index(self, txt, id):
        key = self.key
        db = self.client
        words = _stem(_strip_stopwords(_words(txt)))
        counts = _count_words(words)
        metaphone_map = _metaphone_map(words)
        keys = list(metaphone_map.keys())

        cmds = []
        for k in keys:
            cmds.append(['zadd', key + ':word:' + metaphone_map[k], counts[k], id])
            cmds.append(['zadd', key + ':object:' + str(id), counts[k], metaphone_map[k]])

        pipe = db.pipeline()
        for cmd in cmds:
            getattr(pipe, cmd[0])(*cmd[1:])

        return pipe.execute()

    # to remove index
    def remove(self, id):
        key = self.key
        db = self.client

        constants =  db.zrevrangebyscore(key + ':object:' + str(id), '+inf', 0)

        pipe = db.pipeline()
        pipe.delete(key + ':object:' + str(id))

        for c in constants:
            pipe.zrem(key + ':word:' + c.decode('utf-8'), id)

        return pipe.execute()

    # Perform a search on the given `query` returning
    # a `Query` instance.
    def query(self, txt, type = None):
        return Query(txt, type, self)
