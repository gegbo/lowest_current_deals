"""Generated message classes for fusiontables version v1.

API for working with Fusion Tables data.
"""
# NOTE: This file is autogenerated and should not be edited by hand.

from protorpc import messages


package = 'fusiontables'


class Column(messages.Message):

    """Specifies the id, name and type of a column in a table.

    Messages:
      BaseColumnValue: Optional identifier of the base column. If present, this
        column is derived from the specified base column.

    Fields:
      baseColumn: Optional identifier of the base column. If present, this
        column is derived from the specified base column.
      columnId: Identifier for the column.
      description: Optional column description.
      graph_predicate: Optional column predicate. Used to map table to
        graph data model (subject,predicate,object) See
        http://www.w3.org/TR/2014/REC-
        rdf11-concepts-20140225/#data-model
      kind: Type name: a template for an individual column.
      name: Required name of the column.
      type: Required type of the column.

    """

    class BaseColumnValue(messages.Message):

        """Optional identifier of the base column. If present, this column is
        derived from the specified base column.

        Fields:
          columnId: The id of the column in the base table from which
            this column is derived.
          tableIndex: Offset to the entry in the list of base tables
            in the table definition.

        """

        columnId = messages.IntegerField(1, variant=messages.Variant.INT32)
        tableIndex = messages.IntegerField(2, variant=messages.Variant.INT32)

    baseColumn = messages.MessageField('BaseColumnValue', 1)
    columnId = messages.IntegerField(2, variant=messages.Variant.INT32)
    description = messages.StringField(3)
    graph_predicate = messages.StringField(4)
    kind = messages.StringField(5, default=u'fusiontables#column')
    name = messages.StringField(6)
    type = messages.StringField(7)


class ColumnList(messages.Message):

    """Represents a list of columns in a table.

    Fields:
      items: List of all requested columns.
      kind: Type name: a list of all columns.
      nextPageToken: Token used to access the next page of this
        result. No token is displayed if there are no more pages left.
      totalItems: Total number of columns for the table.

    """

    items = messages.MessageField('Column', 1, repeated=True)
    kind = messages.StringField(2, default=u'fusiontables#columnList')
    nextPageToken = messages.StringField(3)
    totalItems = messages.IntegerField(4, variant=messages.Variant.INT32)


class FusiontablesColumnListRequest(messages.Message):

    """A FusiontablesColumnListRequest object.

    Fields:
      maxResults: Maximum number of columns to return. Optional. Default is 5.
      pageToken: Continuation token specifying which result page to return.
        Optional.
      tableId: Table whose columns are being listed.
    """

    maxResults = messages.IntegerField(1, variant=messages.Variant.UINT32)
    pageToken = messages.StringField(2)
    tableId = messages.StringField(3, required=True)


class FusiontablesColumnListAlternateRequest(messages.Message):

    """A FusiontablesColumnListRequest object.

    Fields:
      pageSize: Maximum number of columns to return. Optional. Default is 5.
      pageToken: Continuation token specifying which result page to return.
        Optional.
      tableId: Table whose columns are being listed.
    """

    pageSize = messages.IntegerField(1, variant=messages.Variant.UINT32)
    pageToken = messages.StringField(2)
    tableId = messages.StringField(3, required=True)


class ColumnListAlternate(messages.Message):

    """Represents a list of columns in a table.

    Fields:
      items: List of all requested columns.
      kind: Type name: a list of all columns.
      nextPageToken: Token used to access the next page of this
        result. No token is displayed if there are no more pages left.
      totalItems: Total number of columns for the table.

    """

    columns = messages.MessageField('Column', 1, repeated=True)
    kind = messages.StringField(2, default=u'fusiontables#columnList')
    nextPageToken = messages.StringField(3)
    totalItems = messages.IntegerField(4, variant=messages.Variant.INT32)
