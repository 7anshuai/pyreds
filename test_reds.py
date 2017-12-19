#!/usr/bin/env python

import unittest

import redis
from reds import reds

db = redis.StrictRedis(db=1)
reds.set_client(db)

class SearchTestCase(unittest.TestCase):
    def setUp(self):
        self.search = reds.create_search('reds')
        self.search.index('Tobi wants 4 dollars', 0)
        self.search.index('Loki is a ferret', 2)
        self.search.index('Tobi is also a ferret', 3)
        self.search.index('Jane is a bitchy ferret', 4)
        self.search.index('Tobi is employed by LearbBoost', 5)
        self.search.index('stuff compute', 6)
        self.search.index('simple words do not mean simple ideas', 7)
        self.search.index('The dog spoke the words, much to our unbelief', 8)
        self.search.index('puppy dog eagle puppy frog puppy dog simple', 9)

    def tearDown(self):
        db.flushdb()

    def test_words(self):
        assert reds._words('foo bar baz ') == ['foo', 'bar', 'baz']
        assert reds._words(' Punctuation and whitespace; should be, handled.') == [
                'Punctuation',
                'and',
                'whitespace',
                'should',
                'be',
                'handled'
            ]
        assert reds._words('Tobi wants 4 dollars') == ['Tobi', 'wants', '4', 'dollars']

    def test_strip_stopwords(self):
        assert reds._strip_stopwords(['this', 'is', 'just', 'a', 'test']) == ['test']

    def test_count_words(self):
        assert reds._count_words(['foo', 'bar', 'baz', 'foo', 'jaz', 'foo', 'baz']) == {
                'foo': 3,
                'bar': 1,
                'baz': 2,
                'jaz': 1
            }

    def test_metaphone_map(self):
        assert reds._metaphone_map(['foo', 'bar', 'baz']) == {'foo': 'F', 'bar': 'BR', 'baz': 'BS'}

    def test_metaphone_list(self):
        assert reds._metaphone_list(['foo', 'bar', 'baz']) == ['F', 'BR', 'BS']

    def test_metaphone_keys(self):
        assert reds._metaphone_keys('reds', ['foo', 'bar', 'baz']) == ['reds:word:F', 'reds:word:BR', 'reds:word:BS']
        assert reds._metaphone_keys('foobar', ['foo', 'bar', 'baz']) == ['foobar:word:F', 'foobar:word:BR', 'foobar:word:BS']

    def test_query(self):
        ids = self.search.query('stuff compute').end()
        assert ids == ['6']

        ids = self.search.query('Tobi').end()
        assert len(ids) == 3
        assert '0' in ids
        assert '3' in ids
        assert '5' in ids

        ids = self.search.query('tobi').end()
        assert len(ids) == 3
        assert '0' in ids
        assert '3' in ids
        assert '5' in ids

        ids = self.search.query('bitchy').end()
        assert ids == ['4']

        ids = self.search.query('bitchy jane').end()
        assert ids == ['4']

        ids = self.search.query('loki and jane').type('or').end()
        assert len(ids) == 2
        assert '2' in ids
        assert '4' in ids

        ids = self.search.query('loki and jane').end()
        assert ids == []

        ids = self.search.query('jane ferret').end()
        assert ids == ['4']

        ids = self.search.query('is a').end()
        assert ids == []

        ids = self.search.query('simple').end()
        assert len(ids) == 2
        assert '7' in ids
        assert '9' in ids
        assert ids[0] == '7'
        assert ids[1] == '9'

    def test_search(self):
        self.search.index('keyboard cat', 6)
        ids = self.search.query('keyboard').end()
        assert ids == ['6']

        ids = self.search.query('cat').end()
        assert ids == ['6']

        self.search.remove(6)
        ids = self.search.query('keyboard').end()
        assert ids == []

        ids = self.search.query('cat').end()
        assert ids == []


if __name__ == '__main__':
    unittest.main()
