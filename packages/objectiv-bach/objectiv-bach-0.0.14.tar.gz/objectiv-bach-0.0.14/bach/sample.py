"""
Copyright 2021 Objectiv B.V.
"""
from typing import cast, TYPE_CHECKING

from bach import DataFrame
from bach.dataframe import escape_parameter_characters
from bach.sql_model import SampleSqlModel
from sql_models.graph_operations import find_node, replace_node_in_graph
from sql_models.sql_generator import to_sql
from sql_models.util import quote_identifier

if TYPE_CHECKING:
    from bach import SeriesBoolean


def get_sample(df: DataFrame,
               table_name: str,
               filter: 'SeriesBoolean' = None,
               sample_percentage: int = None,
               overwrite: bool = False,
               seed: int = None) -> 'DataFrame':
    """
    See :py:meth:`bach.DataFrame.get_sample` for more information.
    """
    if sample_percentage is None and filter is None:
        raise ValueError('Either sample_percentage or filter must be set')

    dialect = df.engine.dialect
    original_node = df.base_node
    if filter is not None:
        sample_percentage = None
        from bach.series import SeriesBoolean
        if not isinstance(filter, SeriesBoolean):
            raise TypeError('Filter parameter needs to be a SeriesBoolean instance.')
        # Boolean argument implies return type of self[filter], help mypy a bit
        df = cast('DataFrame', df[filter])

    with df.engine.connect() as conn:
        if overwrite:
            sql = f'DROP TABLE IF EXISTS {quote_identifier(dialect, table_name)}'
            sql = escape_parameter_characters(conn, sql)
            conn.execute(sql)

        if sample_percentage:
            repeatable = f'repeatable ({seed})' if seed else ''

            sql = f'''
                create temporary table tmp_table_name on commit drop as
                ({to_sql(dialect, df.base_node)});
                create temporary table {quote_identifier(dialect, table_name)} as
                (select * from tmp_table_name
                tablesample bernoulli({sample_percentage}) {repeatable})
            '''
        else:
            sql = f'create temporary table {quote_identifier(dialect, table_name)} as ({df.view_sql()})'
        sql = escape_parameter_characters(conn, sql)
        conn.execute(sql)

    # Use SampleSqlModel, that way we can keep track of the current_node and undo this sampling
    # in get_unsampled() by switching this new node for the old node again.
    new_base_node = SampleSqlModel.get_instance(
        dialect=dialect,
        table_name=table_name,
        previous=original_node,
        column_expressions=original_node.column_expressions,
    )
    return df.copy_override_base_node(base_node=new_base_node)


def get_unsampled(df: DataFrame) -> 'DataFrame':
    """
    See :py:meth:`bach.DataFrame.get_unsampled` for more information.
    """
    # The returned DataFrame has a modified base_node graph, in which the node that introduced the
    # sampling is removed.
    sampled_node_tuple = find_node(
        start_node=df.base_node,
        function=lambda node: isinstance(node, SampleSqlModel)
    )
    if sampled_node_tuple is None:
        raise ValueError('No sampled node found. Cannot un-sample data that has not been sampled.')

    # help mypy: sampled_node_tuple.model is guaranteed to be a SampleSqlModel, as that is what the
    # filter function for find_node() above filtered on
    assert isinstance(sampled_node_tuple.model, SampleSqlModel)

    updated_graph = replace_node_in_graph(
        start_node=df.base_node,
        reference_path=sampled_node_tuple.reference_path,
        replacement_model=sampled_node_tuple.model.previous
    )
    return df.copy_override_base_node(base_node=updated_graph)
