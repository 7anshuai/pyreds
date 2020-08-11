from pyreds.reds import (
    set_client,
    create_client,
    create_search,
    Query,
    Search
)

__version__ = '0.1.4'
VERSION = tuple(map(int, __version__.split('.')))

__all__ = [
    'set_client', 'create_client', 'create_search', 'Query', 'Search'
]
