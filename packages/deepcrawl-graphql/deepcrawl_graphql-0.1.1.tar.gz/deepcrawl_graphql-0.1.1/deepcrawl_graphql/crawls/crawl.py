"""
CrawlQuery
==========
"""

from deepcrawl_graphql.api import DeepCrawlConnection
from deepcrawl_graphql.query import Query

from .fields import CrawlFields


class CrawlQuery(CrawlFields, Query):
    """CrawlQuery class

    Creates a crawl query instance.
    The instance will be passed to the run_query method in order to execute the query.

    >>> from deepcrawl_graphql.crawls.crawl import CrawlQuery

    >>> crawl_query = CrawlQuery(conn, "crawl_id")
    >>> crawl_query.select_crawl()
    >>> crawl_query.select_parquet_files("datasource_name")
    >>> crawl_query.select_compared_to()
    >>> crawl = conn.run_query(crawl_query)

    :param conn: Connection.
    :type conn: DeepCrawlConnection
    :param crawl_id: crawl id.
    :type crawl_id: int or str
    """

    def __init__(self, conn: DeepCrawlConnection, crawl_id) -> None:
        super().__init__(conn)
        self.query = self.query.getCrawl.args(id=crawl_id)

    """
    Crawl
    """

    def select_crawl(self):
        """Selects crawl fields."""
        self.query.select(*self.fields(self.ds))
        return self

    def select_parquet_files(self, datasource_name):
        """Selects crawl parquetFiles.

        :param datasource_name: Datasource name.
        :type datasource_name: str
        """
        self.query.select(
            self.ds.Crawl.parquetFiles.args(datasourceName=datasource_name).select(*self.parquet_files_fields(self.ds))
        )
        return self

    def select_crawl_type_counts(self, crawl_types, segment_id=None):
        """Selects crawl fields.

        Not implemented yet.

        :param crawl_types: Crawl type.
        :type crawl_types: str
        :param segment_id: Segment id.
        :type segment_id: int or str
        """
        # Having issues with sending the crawlTypes input.
        raise NotImplementedError()
        args = {"input": {"crawlTypes": crawl_types}}
        if segment_id:
            args["input"]["segmentId"] = segment_id
        self.query.select(self.ds.Crawl.crawlTypeCounts.args(**args).select(*self.crawl_type_counts_fields(self.ds)))
        return self

    def select_crawl_settings(self):
        """Selects crawl crawlSetting."""
        # common fields with ProjectQuery
        raise NotImplementedError()

    def select_compared_to(self):
        """Selects crawl comparedTo."""
        self.query.select(self.ds.Crawl.comparedTo.select(*self.fields(self.ds)))
        return self
