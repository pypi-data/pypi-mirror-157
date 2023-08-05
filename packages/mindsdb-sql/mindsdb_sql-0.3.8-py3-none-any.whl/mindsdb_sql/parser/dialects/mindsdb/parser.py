import json

from sly import Parser
from mindsdb_sql.parser.ast import *
from mindsdb_sql.parser.ast.drop import DropDatabase, DropView
from mindsdb_sql.parser.dialects.mindsdb.drop_datasource import DropDatasource
from mindsdb_sql.parser.dialects.mindsdb.drop_predictor import DropPredictor
from mindsdb_sql.parser.dialects.mindsdb.drop_dataset import DropDataset
from mindsdb_sql.parser.dialects.mindsdb.create_predictor import CreatePredictor
from mindsdb_sql.parser.dialects.mindsdb.create_datasource import CreateDatasource
from mindsdb_sql.parser.dialects.mindsdb.create_view import CreateView
from mindsdb_sql.parser.dialects.mindsdb.latest import Latest
from mindsdb_sql.parser.dialects.mindsdb.create_file import CreateFile
from mindsdb_sql.exceptions import ParsingException
from mindsdb_sql.parser.dialects.mindsdb.lexer import MindsDBLexer
from mindsdb_sql.parser.dialects.mindsdb.retrain_predictor import RetrainPredictor
from mindsdb_sql.parser.logger import ParserLogger
from mindsdb_sql.parser.utils import ensure_select_keyword_order, JoinType, tokens_to_string

all_tokens_list = MindsDBLexer.tokens.copy()
all_tokens_list.remove('RPAREN')
all_tokens_list.remove('LPAREN')

"""
Unfortunately the rules are not iherited from base SQLParser, because it just doesn't work with Sly due to metaclass magic.
"""
class MindsDBParser(Parser):
    log = ParserLogger()
    tokens = MindsDBLexer.tokens

    precedence = (
        ('left', PLUS, MINUS, OR),
        ('left', STAR, DIVIDE, AND),
        ('right', UMINUS, UNOT),  # Unary minus operator, unary not
        ('nonassoc', LESS, LEQ, GREATER, GEQ, EQUALS, NEQUALS, IN, BETWEEN, IS, IS_NOT, LIKE),
    )

    # Top-level statements
    @_('show',
       'start_transaction',
       'commit_transaction',
       'rollback_transaction',
       'alter_table',
       'explain',
       'set',
       'use',
       'describe',
       'create_predictor',
       'datasource_engine',
       'create_integration',
       'create_view',
       'drop_predictor',
       'retrain_predictor',
       'drop_datasource',
       'drop_dataset',
       'union',
       'select',
       'insert',
       'delete',
       'drop_database',
       'drop_view',
       'drop_table',
       'create_table',
       )
    def query(self, p):
        return p[0]

    # Explain
    @_('EXPLAIN identifier')
    def explain(self, p):
        return Explain(target=p.identifier)

    # Alter table
    @_('ALTER TABLE identifier id id')
    def alter_table(self, p):
        return AlterTable(target=p.identifier,
                          arg=' '.join([p.id0, p.id1]))

    # DROP VEW
    @_('DROP VIEW identifier')
    @_('DROP VIEW IF_EXISTS identifier')
    def drop_view(self, p):
        if_exists = hasattr(p, 'IF_EXISTS')
        return DropView([p.identifier], if_exists=if_exists)

    @_('DROP VIEW enumeration')
    @_('DROP VIEW IF_EXISTS enumeration')
    def drop_view(self, p):
        if_exists = hasattr(p, 'IF_EXISTS')
        return DropView(p.enumeration, if_exists=if_exists)

    # DROP DATABASE
    @_('DROP DATABASE identifier')
    @_('DROP DATABASE IF_EXISTS identifier')
    @_('DROP SCHEMA identifier')
    @_('DROP SCHEMA IF_EXISTS identifier')
    def drop_database(self, p):
        if_exists = hasattr(p, 'IF_EXISTS')
        return DropDatabase(name=p.identifier, if_exists=if_exists)

    # Transactions

    @_('START TRANSACTION',
       'BEGIN')
    def start_transaction(self, p):
        # https://dev.mysql.com/doc/refman/8.0/en/commit.html
        return StartTransaction()

    @_('COMMIT')
    def commit_transaction(self, p):
        return CommitTransaction()

    @_('ROLLBACK')
    def rollback_transaction(self, p):
        return RollbackTransaction()

    # Set

    @_('SET id identifier')
    @_('SET id identifier COLLATE constant')
    @_('SET id identifier COLLATE DEFAULT')
    @_('SET id constant')
    @_('SET id constant COLLATE constant')
    @_('SET id constant COLLATE DEFAULT')
    def set(self, p):
        if not p.id.lower() == 'names':
            raise ParsingException(f'Expected "SET names", got "SET {p.id}"')
        if isinstance(p[2], Constant):
            arg = Identifier(p[2].value)
        else:
            # is identifier
            arg = p[2]

        params = {}
        if hasattr(p, 'COLLATE'):
            if isinstance(p[4], Constant):
                val = p[4]
            else:
                val = SpecialConstant('DEFAULT')
            params['COLLATE'] = val

        return Set(category=p.id.lower(), arg=arg, params=params)

    # set charset
    @_('SET charset constant')
    @_('SET charset DEFAULT')
    def set(self, p):
        if hasattr(p, 'DEFAULT'):
            arg = SpecialConstant('DEFAULT')
        else:
            arg = p.constant
        return Set(category='CHARSET', arg=arg)

    @_('CHARACTER SET',
       'CHARSET',
       )
    def charset(self, p):
        return p[0]

    # set transaction
    @_('SET transact_scope TRANSACTION transact_property_list')
    @_('SET TRANSACTION transact_property_list')
    def set(self, p):
        isolation_level = None
        access_mode = None
        transact_scope = getattr(p, 'transact_scope', None)
        for prop in p.transact_property_list:
            if prop['type'] == 'iso_level':
                isolation_level = prop['value']
            else:
                access_mode = prop['value']

        return SetTransaction(
            isolation_level=isolation_level,
            access_mode=access_mode,
            scope=transact_scope,
        )

    @_('GLOBAL',
       'SESSION')
    def transact_scope(self, p):
        return p[0]

    @_('transact_property_list COMMA transact_property')
    def transact_property_list(self, p):
        return p.transact_property_list + [p.transact_property]

    @_('transact_property')
    def transact_property_list(self, p):
        return [p[0]]

    @_('ISOLATION LEVEL transact_level',
       'transact_access_mode')
    def transact_property(self, p):
        if hasattr(p, 'transact_level'):
            return {'type': 'iso_level', 'value': p.transact_level}
        else:
            return {'type': 'access_mode', 'value': p.transact_access_mode}

    @_('REPEATABLE READ',
       'READ COMMITTED',
       'READ UNCOMMITTED',
       'SERIALIZABLE')
    def transact_level(self, p):
        return ' '.join([x for x in p])

    @_('READ WRITE',
       'READ ONLY')
    def transact_access_mode(self, p):
        return ' '.join([x for x in p])

    @_('SET expr_list')
    @_('SET set_modifier expr_list')
    def set(self, p):
        if len(p.expr_list) == 1:
            arg = p.expr_list[0]
        else:
            arg = Tuple(items=p.expr_list)

        if hasattr(p, 'set_modifier'):
            category = p.set_modifier
        else:
            category = None

        return Set(category=category, arg=arg)

    @_('GLOBAL',
       'PERSIST',
       'PERSIST_ONLY',
       'SESSION',
       )
    def set_modifier(self, p):
        return p[0]

    # Show
    @_('show WHERE expr')
    def show(self, p):
        command = p.show
        command.where = p.expr
        return command

    @_('show LIKE string')
    def show(self, p):
        command = p.show
        command.like = p.string
        return command

    @_('show FROM identifier')
    def show(self, p):
        command = p.show
        value0 = command.from_table
        value1 = p.identifier
        if value0 is not None:
            value1.parts = value1.parts + value0.parts

        command.from_table = value1
        return command

    @_('show IN identifier')
    def show(self, p):
        command = p.show
        value0 = command.in_table
        value1 = p.identifier
        if value0 is not None:
            value1.parts = value1.parts + value0.parts

        command.in_table = value1
        return command

    @_('SHOW show_category',
       'SHOW show_modifier_list show_category')
    def show(self, p):
        modes = getattr(p, 'show_modifier_list', None)
        return Show(
            category=p.show_category,
            modes=modes
        )

    @_('SCHEMAS',
       'DATABASES',
       'TABLES',
       'OPEN TABLES',
       'TRIGGERS',
       'COLUMNS',
       'FIELDS',
       'PLUGINS',
       'VARIABLES',
       'INDEXES',
       'KEYS',
       'SESSION VARIABLES',
       'GLOBAL VARIABLES',
       'GLOBAL STATUS',
       'SESSION STATUS',
       'PROCEDURE STATUS',
       'FUNCTION STATUS',
       'TABLE STATUS',
       'MASTER STATUS',
       'STATUS',
       'STORAGE ENGINES',
       'PROCESSLIST',
       'INDEX',
       'CREATE TABLE',
       'WARNINGS',
       'ENGINES',
       'CHARSET',
       'CHARACTER SET',
       'COLLATION',
       'BINARY LOGS',
       'MASTER LOGS',
       'PRIVILEGES',
       'PROFILES',
       'REPLICAS',
       'SLAVE HOSTS',
       # Mindsdb specific
       'VIEWS',
       'STREAMS',
       'PREDICTORS',
       'INTEGRATIONS',
       'DATASOURCES',
       'PUBLICATIONS',
       'DATASETS',
       'ALL')
    def show_category(self, p):
        return ' '.join([x for x in p])

    # custom show commands
    @_('SHOW ENGINE identifier STATUS',
       'SHOW ENGINE identifier MUTEX')
    def show(self, p):
        return Show(
            category=p[1],
            name=p.identifier.to_string(),
            modes=[p[3]]
        )

    @_('SHOW FUNCTION CODE identifier',
       'SHOW PROCEDURE CODE identifier')
    def show(self, p):
        category = p[1] + ' ' + p[2]
        return Show(
            category=category,
            name=p.identifier.to_string()
        )

    @_('SHOW REPLICA STATUS FOR CHANNEL id',
       'SHOW SLAVE STATUS FOR CHANNEL id',
       'SHOW REPLICA STATUS',
       'SHOW SLAVE STATUS',)
    def show(self, p):
        name = getattr(p, 'id', None)
        return Show(
            category='REPLICA STATUS', # slave = replica
            name=name
        )

    @_('show_modifier',
       'show_modifier_list show_modifier')
    def show_modifier_list(self, p):
        if hasattr(p, 'empty'):
            return None
        params = getattr(p, 'show_modifier_list', [])
        params.append(p.show_modifier)
        return params

    @_('EXTENDED',
       'FULL')
    def show_modifier(self, p):
        return p[0]

    # DELETE
    @_('DELETE FROM from_table WHERE expr')
    @_('DELETE FROM from_table')
    def delete(self, p):
        where = getattr(p, 'expr', None)

        if where is not None and not isinstance(where, Operation):
            raise ParsingException(
                f"WHERE must contain an operation that evaluates to a boolean, got: {str(where)}")

        return Delete(table=p.from_table, where=where)

    # INSERT
    @_('INSERT INTO from_table LPAREN result_columns RPAREN select')
    @_('INSERT INTO from_table select')
    def insert(self, p):
        columns = getattr(p, 'result_columns', None)
        return Insert(table=p.from_table, columns=columns, from_select=p.select)

    @_('INSERT INTO from_table LPAREN result_columns RPAREN VALUES expr_list_set')
    @_('INSERT INTO from_table VALUES expr_list_set')
    def insert(self, p):
        columns = getattr(p, 'result_columns', None)
        return Insert(table=p.from_table, columns=columns, values=p.expr_list_set)

    @_('expr_list_set COMMA expr_list_set')
    def expr_list_set(self, p):
        return p.expr_list_set0 + p.expr_list_set1

    @_('LPAREN expr_list RPAREN')
    def expr_list_set(self, p):
        return [p.expr_list]

    # DESCRIBE

    @_('DESCRIBE identifier')
    def describe(self, p):
        return Describe(value=p.identifier)

    # USE

    @_('USE identifier')
    def use(self, p):
        return Use(value=p.identifier)

    # CREATE VIEW
    @_('CREATE VIEW id create_view_from_table_or_nothing AS LPAREN raw_query RPAREN')
    @_('CREATE DATASET id create_view_from_table_or_nothing AS LPAREN raw_query RPAREN')
    @_('CREATE VIEW id create_view_from_table_or_nothing LPAREN raw_query RPAREN')
    @_('CREATE DATASET id create_view_from_table_or_nothing LPAREN raw_query RPAREN')
    def create_view(self, p):
        query_str = tokens_to_string(p.raw_query)

        return CreateView(name=p.id,
                          from_table=p.create_view_from_table_or_nothing,
                          query_str=query_str)

    @_('FROM identifier')
    def create_view_from_table_or_nothing(self, p):
        return p.identifier

    @_('empty')
    def create_view_from_table_or_nothing(self, p):
        pass

    # RETRAIN PREDICTOR
    @_('RETRAIN identifier')
    def retrain_predictor(self, p):
        return RetrainPredictor(p.identifier)

    # DROP PREDICTOR
    @_('DROP PREDICTOR identifier',
       'DROP PREDICTOR IF_EXISTS identifier')
    def drop_predictor(self, p):
        if_exists = hasattr(p, 'IF_EXISTS')
        return DropPredictor(p.identifier, if_exists=if_exists)

    # DROP DATASOURCE
    @_('DROP DATASOURCE identifier')
    def drop_datasource(self, p):
        return DropDatasource(p.identifier)

    # DROP DATASET
    @_('DROP DATASET identifier')
    def drop_dataset(self, p):
        return DropDataset(p.identifier)

    # DROP TABLE
    @_('DROP TABLE IF_EXISTS identifier')
    @_('DROP TABLE identifier')
    def drop_table(self, p):
        if_exists = hasattr(p, 'IF_EXISTS')
        return DropTables(tables=[p.identifier], if_exists=if_exists)

    # create table
    @_('CREATE TABLE identifier select')
    @_('CREATE TABLE identifier LPAREN select RPAREN')
    @_('CREATE OR REPLACE TABLE identifier select')
    @_('CREATE OR REPLACE TABLE identifier LPAREN select RPAREN')
    def create_table(self, p):
        # TODO create table with columns
        is_replace = False
        if hasattr(p, 'REPLACE'):
            is_replace = True
        return CreateTable(
            name=p.identifier,
            is_replace=is_replace,
            from_select=p.select
        )

    @_('CREATE TABLE identifier USING kw_parameter_list')
    def create_table(self, p):
        params = p.kw_parameter_list
        return CreateFile(name=p.identifier, **params)

    @_('create_predictor USING kw_parameter_list')
    def create_predictor(self, p):
        p.create_predictor.using = p.kw_parameter_list
        return p.create_predictor

    @_('create_predictor HORIZON integer')
    def create_predictor(self, p):
        p.create_predictor.horizon = p.integer
        return p.create_predictor

    @_('create_predictor WINDOW integer')
    def create_predictor(self, p):
        p.create_predictor.window = p.integer
        return p.create_predictor

    @_('create_predictor GROUP_BY expr_list')
    def create_predictor(self, p):
        group_by = p.expr_list
        if not isinstance(group_by, list):
            group_by = [group_by]

        p.create_predictor.group_by = group_by
        return p.create_predictor

    @_('create_predictor ORDER_BY ordering_terms')
    def create_predictor(self, p):
        p.create_predictor.order_by = p.ordering_terms
        return p.create_predictor

    @_('CREATE PREDICTOR identifier FROM identifier LPAREN raw_query RPAREN optional_data_source_name PREDICT result_columns')
    @_('CREATE TABLE identifier FROM identifier LPAREN raw_query RPAREN optional_data_source_name PREDICT result_columns')
    @_('CREATE PREDICTOR identifier PREDICT result_columns')
    @_('CREATE OR REPLACE PREDICTOR identifier FROM identifier LPAREN raw_query RPAREN optional_data_source_name PREDICT result_columns')
    @_('CREATE OR REPLACE TABLE identifier FROM identifier LPAREN raw_query RPAREN optional_data_source_name PREDICT result_columns')
    @_('CREATE OR REPLACE PREDICTOR identifier PREDICT result_columns')
    def create_predictor(self, p):
        is_replace = False
        if hasattr(p, 'REPLACE'):
            is_replace = True

        query_str = None
        if hasattr(p, 'raw_query'):
            query_str = tokens_to_string(p.raw_query)

        if hasattr(p, 'identifier'):
            # single identifier field
            name = p.identifier
        else:
            name = p.identifier0

        return CreatePredictor(
            name=name,
            integration_name=getattr(p, 'identifier1', None),
            query_str=query_str,
            datasource_name=getattr(p, 'optional_data_source_name', None),
            targets=p.result_columns,
            is_replace=is_replace
        )

    @_('AS identifier')
    def optional_data_source_name(self, p):
        return p.identifier

    @_('empty')
    def optional_data_source_name(self, p):
        pass

    # CREATE INTEGRATION
    @_('CREATE datasource_engine COMMA PARAMETERS EQUALS json',
       'CREATE datasource_engine COMMA PARAMETERS json',
       'CREATE datasource_engine PARAMETERS EQUALS json',
       'CREATE datasource_engine PARAMETERS json')
    @_('CREATE OR REPLACE datasource_engine COMMA PARAMETERS EQUALS json',
       'CREATE OR REPLACE datasource_engine COMMA PARAMETERS json',
       'CREATE OR REPLACE datasource_engine PARAMETERS EQUALS json',
       'CREATE OR REPLACE datasource_engine PARAMETERS json')
    def create_integration(self, p):
        is_replace = False
        if hasattr(p, 'REPLACE'):
            is_replace = True

        return CreateDatasource(name=p.datasource_engine['id'],
                                engine=p.datasource_engine['engine'],
                                is_replace=is_replace,
                                parameters=p.json)

    @_('DATASOURCE id WITH ENGINE EQUALS string',
       'DATASOURCE id WITH ENGINE string',
       'DATABASE id WITH ENGINE EQUALS string',
       'DATABASE id WITH ENGINE string',)
    def datasource_engine(self, p):
        return {'id': p.id, 'engine': p.string}

    # UNION / UNION ALL
    @_('select UNION select')
    def union(self, p):
        return Union(left=p.select0, right=p.select1, unique=True)

    @_('select UNION ALL select')
    def union(self, p):
        return Union(left=p.select0, right=p.select1, unique=False)

    # tableau
    @_('LPAREN select RPAREN')
    def select(self, p):
        return p.select

    # WITH
    @_('ctes select')
    def select(self, p):
        select = p.select
        select.cte = p.ctes
        return select

    @_('ctes COMMA identifier cte_columns_or_nothing AS LPAREN select RPAREN')
    def ctes(self, p):
        ctes = p.ctes
        ctes = ctes + [
            CommonTableExpression(
                name=p.identifier,
                columns=p.cte_columns_or_nothing,
                query=p.select)
        ]
        return ctes

    @_('WITH identifier cte_columns_or_nothing AS LPAREN select RPAREN')
    def ctes(self, p):
        return [
            CommonTableExpression(
                name=p.identifier,
                columns=p.cte_columns_or_nothing,
                query=p.select)
        ]

    @_('empty')
    def cte_columns_or_nothing(self, p):
        pass

    @_('LPAREN enumeration RPAREN')
    def cte_columns_or_nothing(self, p):
        return p.enumeration

    # SELECT
    @_('select FOR UPDATE')
    def select(self, p):
        select = p.select
        ensure_select_keyword_order(select, 'MODE')
        select.mode = 'FOR UPDATE'
        return select

    @_('select OFFSET constant')
    def select(self, p):
        select = p.select
        if select.offset is not None:
            raise ParsingException(f'OFFSET already specified for this query')
        ensure_select_keyword_order(select, 'OFFSET')
        if not isinstance(p.constant.value, int):
            raise ParsingException(f'OFFSET must be an integer value, got: {p.constant.value}')

        select.offset = p.constant
        return select

    @_('select LIMIT constant COMMA constant')
    def select(self, p):
        select = p.select
        ensure_select_keyword_order(select, 'LIMIT')
        if not isinstance(p.constant0.value, int) or not isinstance(p.constant1.value, int):
            raise ParsingException(f'LIMIT must have integer arguments, got: {p.constant0.value}, {p.constant1.value}')
        select.offset = p.constant0
        select.limit = p.constant1
        return select

    @_('select LIMIT constant')
    def select(self, p):
        select = p.select
        ensure_select_keyword_order(select, 'LIMIT')
        if not isinstance(p.constant.value, int):
            raise ParsingException(f'LIMIT must be an integer value, got: {p.constant.value}')
        select.limit = p.constant
        return select

    @_('select ORDER_BY ordering_terms')
    def select(self, p):
        select = p.select
        ensure_select_keyword_order(select, 'ORDER BY')
        select.order_by = p.ordering_terms
        return select

    @_('ordering_terms COMMA ordering_term')
    def ordering_terms(self, p):
        terms = p.ordering_terms
        terms.append(p.ordering_term)
        return terms

    @_('ordering_term')
    def ordering_terms(self, p):
        return [p.ordering_term]

    @_('ordering_term NULLS_FIRST')
    def ordering_term(self, p):
        p.ordering_term.nulls = p.NULLS_FIRST
        return p.ordering_term

    @_('ordering_term NULLS_LAST')
    def ordering_term(self, p):
        p.ordering_term.nulls = p.NULLS_LAST
        return p.ordering_term

    @_('identifier DESC')
    def ordering_term(self, p):
        return OrderBy(field=p.identifier, direction='DESC')

    @_('identifier ASC')
    def ordering_term(self, p):
        return OrderBy(field=p.identifier, direction='ASC')

    @_('identifier')
    def ordering_term(self, p):
        return OrderBy(field=p.identifier, direction='default')

    @_('select HAVING expr')
    def select(self, p):
        select = p.select
        ensure_select_keyword_order(select, 'HAVING')
        having = p.expr
        if not isinstance(having, Operation):
            raise ParsingException(
                f"HAVING must contain an operation that evaluates to a boolean, got: {str(having)}")
        select.having = having
        return select

    @_('select GROUP_BY expr_list')
    def select(self, p):
        select = p.select
        ensure_select_keyword_order(select, 'GROUP BY')
        group_by = p.expr_list
        if not isinstance(group_by, list):
            group_by = [group_by]

        select.group_by = group_by
        return select

    @_('select WHERE expr')
    def select(self, p):
        select = p.select
        ensure_select_keyword_order(select, 'WHERE')
        where_expr = p.expr
        if not isinstance(where_expr, Operation):
            raise ParsingException(
                f"WHERE must contain an operation that evaluates to a boolean, got: {str(where_expr)}")
        select.where = where_expr
        return select

    # Special cases for keyword-like identifiers
    @_('select FROM TABLES')
    def select(self, p):
        select = p.select
        ensure_select_keyword_order(select, 'FROM')
        select.from_table = Identifier(p.TABLES)
        return select

    @_('select FROM from_table_aliased')
    def select(self, p):
        select = p.select
        ensure_select_keyword_order(select, 'FROM')
        select.from_table = p.from_table_aliased
        return select

    @_('from_table_aliased join_clause from_table_aliased')
    def from_table_aliased(self, p):
        return Join(left=p.from_table_aliased0,
                    right=p.from_table_aliased1,
                    join_type=p.join_clause)

    @_('from_table_aliased COMMA from_table_aliased')
    def from_table_aliased(self, p):
        return Join(left=p.from_table_aliased0,
                    right=p.from_table_aliased1,
                    join_type=JoinType.INNER_JOIN,
                    implicit=True)

    @_('from_table_aliased join_clause from_table_aliased ON expr')
    def from_table_aliased(self, p):
        return Join(left=p.from_table_aliased0,
                    right=p.from_table_aliased1,
                    join_type=p.join_clause,
                    condition=p.expr)

    @_('from_table AS identifier',
       'from_table identifier',
       'from_table AS dquote_string',
       'from_table dquote_string',
       'from_table')
    def from_table_aliased(self, p):
        entity = p.from_table
        if hasattr(p, 'identifier'):
            entity.alias = p.identifier
        if hasattr(p, 'dquote_string'):
            entity.alias = Identifier(p.dquote_string)
        return entity

    @_('LPAREN query RPAREN')
    def from_table(self, p):
        query = p.query
        query.parentheses = True
        return query

    # keywords for table
    @_('PLUGINS')
    @_('ENGINES')
    def from_table(self, p):
        return Identifier.from_path_str(p[0])

    @_('identifier')
    def from_table(self, p):
        return p.identifier

    @_('parameter')
    def from_table(self, p):
        return p.parameter

    @_('JOIN',
       'LEFT JOIN',
       'RIGHT JOIN',
       'INNER JOIN',
       'FULL JOIN',
       'CROSS JOIN',
       'OUTER JOIN',
       )
    def join_clause(self, p):
        return ' '.join([x for x in p])

    @_('SELECT DISTINCT result_columns')
    def select(self, p):
        targets = p.result_columns
        return Select(targets=targets, distinct=True)

    @_('SELECT result_columns')
    def select(self, p):
        targets = p.result_columns
        return Select(targets=targets)

    @_('result_columns COMMA result_column')
    def result_columns(self, p):
        p.result_columns.append(p.result_column)
        return p.result_columns

    @_('result_column')
    def result_columns(self, p):
        return [p.result_column]

    @_('result_column AS identifier',
       'result_column identifier',
       'result_column AS dquote_string',
       'result_column dquote_string')
    def result_column(self, p):
        col = p.result_column
        if col.alias:
            raise ParsingException(f'Attempt to provide two aliases for {str(col)}')
        if hasattr(p, 'dquote_string'):
            alias = Identifier(p.dquote_string)
        else:
            alias = p.identifier
        col.alias = alias
        return col

    @_('LPAREN select RPAREN')
    def result_column(self, p):
        select = p.select
        select.parentheses = True
        return select

    @_('star')
    def result_column(self, p):
        return p.star


    @_('expr',
       'function',
       'window_function',
       'case')
    def result_column(self, p):
        return p[0]

    # case
    @_('CASE case_conditions ELSE expr END')
    def case(self, p):
        return Case(rules=p.case_conditions, default=p.expr)

    @_('case_condition',
       'case_conditions case_condition')
    def case_conditions(self, p):
        arr = getattr(p, 'case_conditions', [])
        arr.append(p.case_condition)
        return arr

    @_('WHEN expr THEN expr')
    def case_condition(self, p):
        return [p.expr0, p.expr1]

    # Window function
    @_('function OVER LPAREN window RPAREN')
    def window_function(self, p):

        return WindowFunction(
            function=p.function,
            order_by=p.window.get('order_by'),
            partition=p.window.get('partition'),
        )

    @_('window PARTITION_BY expr_list')
    def window(self, p):
        window = p.window
        part_by = p.expr_list
        if not isinstance(part_by, list):
            part_by = [part_by]

        window['partition'] = part_by
        return window

    @_('window ORDER_BY ordering_terms')
    def window(self, p):
        window = p.window
        window['order_by'] = p.ordering_terms
        return window

    @_('empty')
    def window(self, p):
        return {}

    # OPERATIONS

    @_('LPAREN select RPAREN')
    def expr(self, p):
        select = p.select
        select.parentheses = True
        return select

    @_('LPAREN expr RPAREN')
    def expr(self, p):
        if isinstance(p.expr, ASTNode):
            p.expr.parentheses = True
        return p.expr

    @_('DATABASE LPAREN RPAREN')
    def function(self, p):
        return Function(op=p.DATABASE, args=[])

    @_('id LPAREN DISTINCT expr_list RPAREN')
    def function(self, p):
        return Function(op=p.id, distinct=True, args=p.expr_list)

    @_('id LPAREN expr_list_or_nothing RPAREN')
    def function(self, p):
        args = p.expr_list_or_nothing
        if not args:
            args = []
        return Function(op=p.id, args=args)

    # arguments are optional in functions, so that things like `select database()` are possible
    @_('expr BETWEEN expr AND expr')
    def expr(self, p):
        return BetweenOperation(args=(p.expr0, p.expr1, p.expr2))

    @_('expr_list')
    def expr_list_or_nothing(self, p):
        return p.expr_list

    @_('empty')
    def expr_list_or_nothing(self, p):
        pass

    @_('CAST LPAREN expr AS id RPAREN')
    def expr(self, p):
        return TypeCast(arg=p.expr, type_name=str(p.id))

    @_('CONVERT LPAREN expr COMMA id RPAREN')
    @_('CONVERT LPAREN expr USING id RPAREN')
    def expr(self, p):
        return TypeCast(arg=p.expr, type_name=str(p.id))

    @_('enumeration')
    def expr_list(self, p):
        return p.enumeration

    @_('expr')
    def expr_list(self, p):
        return [p.expr]

    @_('LPAREN enumeration RPAREN')
    def expr(self, p):
        tup = Tuple(items=p.enumeration)
        return tup

    @_('STAR')
    def star(self, p):
        return Star()

    @_('expr NOT IN expr')
    def expr(self, p):
        op = p[1] + ' ' + p[2]
        return BinaryOperation(op=op, args=(p.expr0, p.expr1))

    @_('expr PLUS expr',
       'expr MINUS expr',
       'expr STAR expr',
       'expr DIVIDE expr',
       'expr MODULO expr',
       'expr EQUALS expr',
       'expr NEQUALS expr',
       'expr GEQ expr',
       'expr GREATER expr',
       'expr LEQ expr',
       'expr LESS expr',
       'expr AND expr',
       'expr OR expr',
       'expr IS_NOT expr',
       'expr NOT expr',
       'expr IS expr',
       'expr LIKE expr',
       'expr CONCAT expr',
       'expr IN expr')
    def expr(self, p):
        return BinaryOperation(op=p[1], args=(p.expr0, p.expr1))


    @_('MINUS expr %prec UMINUS',
       'NOT expr %prec UNOT', )
    def expr(self, p):
        return UnaryOperation(op=p[0], args=(p.expr,))

    # EXPRESSIONS

    @_('enumeration COMMA expr')
    def enumeration(self, p):
        return p.enumeration + [p.expr]

    @_('expr COMMA expr')
    def enumeration(self, p):
        return [p.expr0, p.expr1]

    @_('identifier')
    @_('parameter')
    @_('constant')
    @_('latest')
    @_('function')
    def expr(self, p):
        return p[0]

    @_('LATEST')
    def latest(self, p):
        return Latest()

    @_('NULL')
    def constant(self, p):
        return NullConstant()

    @_('TRUE')
    def constant(self, p):
        return Constant(value=True)

    @_('FALSE')
    def constant(self, p):
        return Constant(value=False)

    @_('integer')
    def constant(self, p):
        return Constant(value=int(p.integer))

    @_('float')
    def constant(self, p):
        return Constant(value=float(p.float))

    @_('string')
    def constant(self, p):
        return Constant(value=str(p[0]))

    # param list

    @_('id LPAREN kw_parameter_list RPAREN')
    def object(self, p):
        return Object(type=p.id, params=p.kw_parameter_list)

    @_('kw_parameter',
       'kw_parameter_list COMMA kw_parameter')
    def kw_parameter_list(self, p):
        params = getattr(p, 'kw_parameter_list', {})
        params.update(p.kw_parameter)
        return params

    @_('identifier EQUALS string')
    @_('identifier EQUALS integer')
    @_('identifier EQUALS float')
    @_('identifier EQUALS object')
    @_('identifier EQUALS json')
    @_('identifier EQUALS json_array_list')
    def kw_parameter(self, p):
        key = '.'.join(p.identifier.parts)
        return {key: p[2]}

    # json

    @_('LBRACE json_element_list RBRACE')
    @_('LBRACE RBRACE')
    def json(self, p):
        params = getattr(p, 'json_element_list', {})
        return params

    @_('json_element')
    @_('json_element_list COMMA json_element')
    def json_element_list(self, p):
        params = getattr(p, 'json_element_list', {})
        params.update(p.json_element)
        return params

    @_('string COLON json_value')
    def json_element(self, p):
        return {p.string: p.json_value}

    # json_array

    @_('LBRACKET json_array_list RBRACKET')
    @_('LBRACKET RBRACKET')
    def json_array(self, p):
        arr = getattr(p, 'json_array_list', [])
        return arr

    @_('json_value')
    @_('json_array_list COMMA json_value')
    def json_array_list(self, p):
        arr = getattr(p, 'json_array_list', [])
        arr.append(p.json_value)
        return arr

    @_('float',
       'string',
       'integer',
       'NULL',
       'TRUE',
       'FALSE',
       'json_array',
       'json')
    def json_value(self, p):

        if hasattr(p, 'NULL'):
            return None
        elif hasattr(p, 'TRUE'):
            return True
        elif hasattr(p, 'FALSE'):
            return False
        return p[0]


    @_('identifier DOT identifier')
    @_('identifier DOT star')
    def identifier(self, p):
        node = p[0]
        if isinstance(p[2], Star):
            node.parts.append(p[2])
        else:
            node.parts += p[2].parts
        return node

    @_('id')
    def identifier(self, p):
        value = p[0]
        return Identifier.from_path_str(value)

    @_('quote_string',
       'dquote_string')
    def string(self, p):
        return p[0]

    @_('PARAMETER')
    def parameter(self, p):
        return Parameter(value=p.PARAMETER)

   # convert to types
    @_('ID',
       'BEGIN',
       'CAST',
       'CHANNEL',
       'CHARSET',
       'CODE',
       'COLLATION',
       'COLUMNS',
       'COMMIT',
       'COMMITTED',
       'CONCAT',
       'DATASET',
       'DATASETS',
       'DATASOURCE',
       'DATASOURCES',
       'ENGINE',
       'ENGINES',
       'EXTENDED',
       'FIELDS',
       # 'FULL', # fixme: is parsed as alias
       'GLOBAL',
       'HORIZON',
       'HOSTS',
       'INDEXES',
       'INTEGRATION',
       'INTEGRATIONS',
       'ISOLATION',
       'KEYS',
       'LATEST',
       'LEVEL',
       'LOGS',
       'MASTER',
       'MUTEX',
       'OFFSET',
       'ONLY',
       'OPEN',
       'PARAMETER',
       'PARAMETERS',
       'PERSIST',
       'PLUGINS',
       'PREDICT',
       'PREDICTOR',
       'PREDICTORS',
       'PRIVILEGES',
       'PROCESSLIST',
       'PROFILES',
       'PUBLICATION',
       'PUBLICATIONS',
       'REPEATABLE',
       'REPLACE',
       'REPLICA',
       'REPLICAS',
       'RETRAIN',
       'ROLLBACK',
       'SERIALIZABLE',
       'SESSION',
       'SLAVE',
       'START',
       'STATUS',
       'STORAGE',
       'STREAM',
       'STREAMS',
       'TABLES',
       'TRAIN',
       'TRANSACTION',
       'TRIGGERS',
       'UNCOMMITTED',
       'VARIABLES',
       'VIEW',
       'VIEWS',
       'WARNINGS',
    )
    def id(self, p):
        return p[0]

    @_('FLOAT')
    def float(self, p):
        return float(p[0])

    @_('INTEGER')
    def integer(self, p):
        return int(p[0])

    @_('QUOTE_STRING')
    def quote_string(self, p):
        return p[0].strip('\'')

    @_('DQUOTE_STRING')
    def dquote_string(self, p):
        return p[0].strip('\"')

    # for raw query

    @_('LPAREN raw_query RPAREN')
    def raw_query(self, p):
        return [ p._slice[0] ] + p[1] + [ p._slice[2] ]

    @_('raw_query LPAREN RPAREN')
    def raw_query(self, p):
        return p[0] + [ p._slice[1], p._slice[2] ]

    @_('raw_query raw_query')
    def raw_query(self, p):
        return p[0] + p[1]

    @_(*all_tokens_list)
    def raw_query(self, p):
        return p._slice

    @_('')
    def empty(self, p):
        pass

    def error(self, p):
        if p:
            raise ParsingException(f"Syntax error at token {p.type}: \"{p.value}\"")
        else:
            raise ParsingException("Syntax error at EOF")
