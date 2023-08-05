"""
MeQuery
=======
"""

from deepcrawl_graphql.accounts.fields import AccountFields
from deepcrawl_graphql.api import DeepCrawlConnection
from deepcrawl_graphql.query import Query

from .fields import MeFields


class MeQuery(MeFields, Query):
    """MeQuery class

    Creates a me query instance. "Me" being the authenticated user.
    The instance will be passed to the run_query method in order to execute the query.

    >>> from deepcrawl_graphql.me.me import MeQuery

    >>> me_query = MeQuery(conn)
    >>> me_query.select_me()
    >>> me_query.select_accounts()
    >>> me = conn.run_query(me_query)

    :param conn: Connection.
    :type conn: DeepCrawlConnection
    """

    def __init__(self, conn: DeepCrawlConnection) -> None:
        super().__init__(conn)
        self.query = self.query.me

    def select_me(self):
        """Selects user fields."""
        self.query.select(*self.fields(self.ds))
        return self

    def select_accounts(self, account_query=None):
        """Selects users accounts."""
        account_connection_nodes = self.ds.AccountConnection.nodes.select(*AccountFields.fields(self.ds))
        self.query.select(self.ds.User.accounts.select(account_connection_nodes))
        return self
