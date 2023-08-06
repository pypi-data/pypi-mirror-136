#
#  Copyright (c) 2016-2021 Deephaven Data Labs and Patent Pending
#
from typing import List

from pydeephaven import Table
from pydeephaven._query_ops import *
from pydeephaven.constants import SortDirection
from pydeephaven.dherror import DHError


class Query:
    """ A Query object is used to define and exec a sequence of Deephaven table operations on the server.

    When the query is executed, the table operations specified for the Query object are batched together and sent to the
    server in a single request,  thus avoiding multiple round trips between the client and the server. The result of
    executing the query is a new Deephaven table.

    Note, an application should always use the factory method on the Session object to create a Query instance as the
    constructor is subject to future changes to support more advanced features already planned.
    """

    def __init__(self, session, table):
        self.session = session
        if not self.session or not table:
            raise DHError("invalid session or table value.")
        self._ops = self._last_op = NoneOp(table=table)

    def exec(self) -> Table:
        """ execute the query on the server and returns the result table.

        Args:

        Returns:
            a Table object

        Raises:
            DHError

        """
        return self.session.table_service.batch(self._ops)

    def drop_columns(self, columns: List[str]):
        """ chain a drop-columns operation into the query.

        Args:
            columns (List[str]: a list of column names

        Returns:
            self

        Raises:

        """
        self._last_op = DropColumnsOp(parent=self._last_op, column_names=columns)
        return self

    def update(self, column_specs: List[str]):
        """ chain a update operation into the query.

        Args:
            column_specs (List[str]): a list of column spec strings in the form of either a single name or a simple
        assignment between two names

        Returns:
            self

        Raises:

        """
        self._last_op = UpdateOp(parent=self._last_op, column_specs=column_specs)
        return self

    def lazy_update(self, column_specs):
        """ chain a lazy update operation into the query.

        Args:
            column_specs (List[str]): a list of column spec strings in the form of either a single name or a simple
        assignment between two names

        Returns:
            self

        Raises:

        """
        self._last_op = LazyUpdateOp(parent=self._last_op, column_specs=column_specs)
        return self

    def view(self, column_specs):
        """ chain a view operation into the query.

        Args:
            column_specs (List[str]): a list of column spec strings in the form of either a single name or a simple
        assignment between two names

        Returns:
            self

        Raises:

        """
        self._last_op = ViewOp(parent=self._last_op, column_specs=column_specs)
        return self

    def update_view(self, column_specs):
        """ chain a update-view operation into the query.

        Args:
            column_specs (List[str]): a list of column spec strings in the form of either a single name or a simple
        assignment between two names

        Returns:
            self

        Raises:

        """
        self._last_op = UpdateViewOp(parent=self._last_op, column_specs=column_specs)
        return self

    def select(self, column_specs):
        """ chain a select operation into the query.

        Args:
            column_specs (List[str]): a list of column spec strings in the form of either a single name or a simple
        assignment between two names

        Returns:
            self

        Raises:

        """
        self._last_op = SelectOp(parent=self._last_op, column_specs=column_specs)
        return self

    def tail(self, num_rows: int):
        """ chain a tail operation into the query

        Args:
            num_rows (int): the number of rows to return

        Returns:
            self

        Raises:

        """
        self._last_op = TailOp(parent=self._last_op, num_rows=num_rows)
        return self

    def head(self, num_rows):
        """ chain a head operation into the query

        Args:
            num_rows (int): the number of rows to return

        Returns:
            self

        Raises:

        """
        self._last_op = HeadOp(parent=self._last_op, num_rows=num_rows)
        return self

    def sort(self, column_name, direction=SortDirection.UNKNOWN):
        self._last_op = SortOp(parent=self._last_op, column_name=column_name, direction=direction)
        return self
