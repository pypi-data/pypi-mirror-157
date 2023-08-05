"""
ProjectQuery
============
"""

from deepcrawl_graphql.accounts.fields import AccountFields
from deepcrawl_graphql.api import DeepCrawlConnection
from deepcrawl_graphql.crawls.fields import CrawlFields
from deepcrawl_graphql.query import Query

from .fields import ProjectFields


class ProjectQuery(ProjectFields, Query):
    """ProjectQuery class

    Creates a project query instance.
    The instance will be passed to the run_query method in order to execute the query.

    >>> from deepcrawl_graphql.projects.project import ProjectQuery

    >>> project_query = ProjectQuery(conn, "project_id")
    >>> project_query.select_project()
    >>> project_query.select_sitemaps()
    >>> project_query.select_advanced_crawl_rate()
    >>> project_query.select_majestic_configuration()
    >>> project_query.select_location()
    >>> project_query.select_google_search_configuration()
    >>> project_query.select_custom_extraction_settings()
    >>> project_query.select_account()
    >>> project_query.select_crawls()
    >>> project = conn.run_query(project_query)

    :param conn: Connection.
    :type conn: DeepCrawlConnection
    :param project_id: project id.
    :type project_id: int or str
    """

    def __init__(self, conn: DeepCrawlConnection, project_id) -> None:
        super().__init__(conn)
        self.query = self.query.getProject.args(id=project_id)

    """
    Project
    """

    def select_project(self):
        """Selects project fields."""
        self.query.select(*self.fields(self.ds))
        return self

    def select_sitemaps(self):
        """Selects project sitemaps."""
        self.query.select(self.ds.Project.sitemaps.select(*self.sitemaps_fields(self.ds)))
        return self

    def select_advanced_crawl_rate(self):
        """Selects project maximumCrawlRateAdvanced."""
        self.query.select(self.ds.Project.maximumCrawlRateAdvanced.select(*self.advanced_crawl_rate_fields(self.ds)))
        return self

    def select_majestic_configuration(self):
        """Selects project majesticConfiguration."""
        self.query.select(self.ds.Project.majesticConfiguration.select(*self.majestic_configuration_fields(self.ds)))
        return self

    def select_location(self):
        """Selects project location."""
        self.query.select(self.ds.Project.location.select(*self.location_fields(self.ds)))
        return self

    def select_last_finished_crawl(self):
        """Selects project lastFinishedCrawl.

        Not implemented yet.
        """
        raise NotImplementedError()

    def select_google_search_configuration(self):
        """Selects project googleSearchConsoleConfiguration."""
        self.query.select(
            self.ds.Project.googleSearchConsoleConfiguration.select(*self.google_search_configuration_fields(self.ds))
        )
        return self

    def select_google_analytics_project_view(self):
        """Selects project googleAnalyticsProjectView.

        Not implemented yet.
        """
        raise NotImplementedError()

    def select_custom_extraction_settings(self):
        """Selects project customExtractions."""
        self.query.select(self.ds.Project.customExtractions.select(*self.custom_extraction_setting_fields(self.ds)))
        return self

    """
    Account
    """

    def select_account(self):
        """Selects project account."""
        self.query.select(self.ds.Project.account.select(*AccountFields.fields(self.ds)))
        return self

    """
    Crawl
    """

    def select_crawls(self):
        """Selects project crawls."""
        crawl_nodes = self.ds.CrawlConnection.nodes.select(*CrawlFields.fields(self.ds))
        self.query.select(self.ds.Project.crawls.select(crawl_nodes))
        return self
