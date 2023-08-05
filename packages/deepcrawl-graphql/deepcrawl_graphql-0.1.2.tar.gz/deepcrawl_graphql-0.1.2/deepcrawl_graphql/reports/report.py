"""
ReportQuery
===========
"""

from deepcrawl_graphql.api import DeepCrawlConnection
from deepcrawl_graphql.query import Query

from .fields import ReportFields, ReportTypeFields


class ReportQuery(ReportFields, Query):
    """ReportQuery class

    Creates a report query instance.
    The instance will be passed to the run_query method in order to execute the query.

    >>> from deepcrawl_graphql.reports.report import ReportQuery

    >>> report_query = ReportQuery(conn, "crawl_id", "report_tamplate_code", "report_type_code")
    >>> report_query.select_report()
    >>> report_query.select_datasource()
    >>> report_query.select_type()
    >>> report_query.select_trend()
    >>> report_query.select_segment()
    >>> report_query.select_report_template()
    >>> conn.run_query(report_query)

    :param conn: Connection.
    :type conn: DeepCrawlConnection
    :param crawl_id: crawl id.
    :type crawl_id: int or str
    :param report_tamplate_code: report template code.
    :type report_tamplate_code: str
    :param report_type_code: report type code.
    :type report_type_code: str
    :param segment_id: segment id.
    :type segment_id: int or str
    """

    def __init__(
        self, conn: DeepCrawlConnection, crawl_id, report_tamplate_code, report_type_code, segment_id=None
    ) -> None:
        super().__init__(conn)
        args = {
            "input": {
                "crawlId": crawl_id,
                "reportTemplateCode": report_tamplate_code,
                "reportTypeCode": report_type_code,
            }
        }
        if segment_id:
            args["input"]["segmentId"] = segment_id
        self.query = self.query.getReport.args(**args)

    def select_report(self):
        """Selects report fields."""
        self.query.select(*self.fields(self.ds))
        return self

    def select_datasource(self):
        """Selects report datasources."""
        self.query.select(*self.datasource_fields(self.ds))
        return self

    def select_type(self):
        """Selects report type."""
        self.query.select(self.ds.Report.type.select(*ReportTypeFields.fields(self.ds)))
        return self

    def select_trend(self):
        """Selects report trend."""
        # Failes if datasourceCode and datasourceCodeEnum is included
        self.query.select(self.ds.Report.trend.select(*self.fields(self.ds)))
        return self

    def select_segment(self):
        """Selects report segment."""
        self.query.select(self.ds.Report.segment.select(*self.segment_fields(self.ds)))
        return self

    def select_report_template(self):
        """Selects report reportTemplate."""
        self.query.select(self.ds.Report.reportTemplate.select(*self.report_template_fields(self.ds)))
        return self
