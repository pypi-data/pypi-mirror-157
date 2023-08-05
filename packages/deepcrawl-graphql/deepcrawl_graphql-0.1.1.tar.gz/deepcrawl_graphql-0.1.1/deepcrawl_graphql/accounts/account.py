"""
AccountQuery
============
"""

from deepcrawl_graphql.api import DeepCrawlConnection
from deepcrawl_graphql.projects.fields import ProjectFields
from deepcrawl_graphql.query import Query

from .fields import AccountFields


class AccountQuery(AccountFields, Query):
    """AccountQuery class

    Creates an accout query instance.
    The instance will be passed to the run_query method in order to execute the query.

    >>> from deepcrawl_graphql.accounts.account import AccountQuery

    >>> account_query = AccountQuery(conn, "id")
    >>> account_query.select_account()
    >>> account_query.select_settings()
    >>> account_query.select_callback_headers()
    >>> account_query.select_feature_flags()
    >>> account_query.select_locations()
    >>> account_query.select_package()
    >>> account_query.select_subscription()
    >>> account_query.select_projects()
    >>> account_query.select_project("project_id")
    >>> account = conn.run_query(account_query)

    :param conn: Connection.
    :type conn: DeepCrawlConnection
    :param account_id: account id.
    :type account_id: int or str
    """

    def __init__(self, conn: DeepCrawlConnection, account_id) -> None:
        super().__init__(conn)
        self.query = self.query.getAccount.args(id=account_id)

    """
    Account
    """

    def select_account(self):
        """Selects account fields."""
        self.query.select(*self.fields(self.ds))
        return self

    def select_settings(self):
        """Selects account accountSettings."""
        self.query.select(self.ds.Account.accountSettings.select(*self.settings_fields(self.ds)))
        return self

    def select_callback_headers(self):
        """Selects account apiCallbackHeaders."""
        self.query.select(
            self.ds.Account.apiCallbackHeaders.select(self.ds.APICallbackHeader.key, self.ds.APICallbackHeader.value)
        )
        return self

    def select_feature_flags(self):
        """Selects account featureFlags."""
        self.query.select(self.ds.Account.featureFlags.select(self.ds.FeatureFlag.name, self.ds.FeatureFlag.enabled))
        return self

    def select_locations(self):
        """Selects account locations."""
        self.query.select(self.ds.Account.locations.select(*self.locations_fields(self.ds)))
        return self

    def select_package(self):
        """Selects account primaryAccountPackage."""
        self.query.select(
            self.ds.Account.primaryAccountPackage.select(
                self.ds.AccountPackage.credits, self.ds.AccountPackage.packageType
            )
        )
        return self

    def select_subscription(self, include_addons=False, integration_type=None):
        """Selects account subscription.

        :param include_addons: If true includes the addons available.
        :type include_addons: bool
        :param integration_type: Selects an addon by integration type
        :type integration_type: str
        """
        self.query.select(self.ds.Account.subscription.select(*self.subscription_fields(self.ds)))
        if include_addons:
            self.query.select(
                self.ds.Account.subscription.select(
                    self.ds.AccountSubscription.addons.select(*self.subscription_addons_fields(self.ds))
                )
            )
        if integration_type:
            self.query.select(
                self.ds.Account.subscription.select(
                    self.ds.AccountSubscription.addonByIntegrationType.args(integrationType=integration_type).select(
                        *self.subscription_addons_fields(self.ds)
                    )
                )
            )
        return self

    """
    Project
    """

    def select_projects(self):
        """Selects account projects."""
        projects_nodes = self.ds.ProjectConnection.nodes.select(*ProjectFields.fields(self.ds))
        self.query.select(self.ds.Account.projects.select(projects_nodes))
        return self

    def select_project(self, project_id):
        """Selects account project by id.

        :param project_id: Project id.
        :type project_id: bool
        """
        self.query.select(self.ds.Account.project.args(id=project_id).select(*ProjectFields.fields(self.ds)))
        return self
