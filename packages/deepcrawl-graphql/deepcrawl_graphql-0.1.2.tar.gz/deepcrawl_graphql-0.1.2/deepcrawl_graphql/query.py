"""
Query
=====
"""

from deepcrawl_graphql.api import DeepCrawlConnection


class Query:
    """Query class"""

    def __init__(self, conn: DeepCrawlConnection) -> None:
        self.ds = conn.ds
        self.query = self.ds.Query
