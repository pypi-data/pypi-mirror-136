from typing import Iterable, List, Optional, Tuple, Union, Dict

import re
import hashlib
import pandas as pd

from toolbox.db.api.sql_connection import SQLConnection
from toolbox.db.read.etf_universe import ETFUniverse
from toolbox.db.settings import DB_ADJUSTOR_FIELDS

# try to import sqlparse, but not required
try:
    import sqlparse
except ImportError as e:
    pass

# this allows compatibility with python 3.6
try:
    import pandas_market_calendars as mcal
except ImportError as e:
    pass


class QueryConstructor:
    """
    constructs dynamic queries to go and hit the database

    Functionality:
        possibly cache the data in a feather file
    """

    def __init__(self, sql_con: SQLConnection = None, freq: Optional[str] = 'D'):
        """
        :param sql_con: the connection to the database, if non is passed then will use default SQLConnection
        :param freq: frequency for the period, if None then return a Timestamp
        """
        self._con: SQLConnection = sql_con if sql_con else SQLConnection()

        self._query_string = {'select': '', 'from': '', 'where': '', 'group_by': '', 'window': '', 'order_by': ''}
        self._df_options = {'freq': freq, 'index': []}
        self._query_metadata = {'asset_id': '', 'fields': []}

        self._asset_table = None
        self._dict_asset_tables = {}

    @property
    def raw_sql(self) -> str:
        """
        returns the raw sql query the user has created
        """
        where_clause = 'WHERE ' + self._query_string['where'] if self._query_string['where'] != '' else ''
        group_by_clause = 'GROUP BY ' + self._query_string['group_by'] if self._query_string['group_by'] != '' else ''
        window_clause = 'WINDOW ' + self._query_string['window'] if self._query_string['window'] != '' else ''
        order_by_clause = 'ORDER BY ' + self._query_string['order_by'] if self._query_string['order_by'] != '' else ''

        query_string = f"""
                    SELECT {self._query_string['select']}
                    FROM {self._query_string['from']}
                    {where_clause}
                    {group_by_clause}
                    {window_clause}
                    {order_by_clause}
                """
        return query_string

    @property
    def pretty_sql(self) -> str:
        """
        returns pretty version of raw sql
        """
        return sqlparse.format(self.raw_sql, reindent=True)

    @property
    def fields(self):
        """
        returns the fields(columns) of a query
        """
        return self._query_metadata['fields'] + [
            self._query_metadata['asset_id']] if self._query_metadata['asset_id'] else []

    @property
    def df(self):
        """
        executes the sql query that the user has created
        """
        self._register_universe()
        raw_df = self._con.execute(self.raw_sql).fetchdf()
        self._con.close()

        return self._make_df_changes(raw_df)

    @property
    def asset_tables(self) -> Dict[str, Union[str, pd.DataFrame]]:
        """
        returns self._dict_asset_tables
        """
        return self._dict_asset_tables

    def _make_df_changes(self, raw_df):
        """
        makes the changes to the dataframe query specified by self._df_options
        :param raw_df: the dataframe we are applying the changes to
        """
        if self._df_options['freq'] and 'date' in raw_df.columns:
            raw_df['date'] = raw_df['date'].dt.to_period(self._df_options['freq'])

        raw_df = raw_df.set_index(self._df_options['index']) if self._df_options['index'] else raw_df

        return raw_df

    def _register_universe(self) -> None:
        """
        regesters the tables in self._dict_asset_tables
        :return: None
        """
        if not self._dict_asset_tables:
            return

        for name, tbl in self._dict_asset_tables.items():
            if isinstance(tbl, str):
                self._con.execute(tbl)
            elif isinstance(tbl, pd.DataFrame):
                self._con.con.register(name, tbl)
            else:
                raise ValueError('Unknown type to regester asset table')

    def query_timeseries_table(self, table: str, fields: List[str], assets: Union[Iterable[any], str],
                               search_by: str, start_date: str, end_date: str = '3000', adjust: bool = True):
        """
        constructs a query to get timeseries data from the database
        :param assets: the assets we want to get data for, or a universe table, if '*' then will not filter assets
        :param search_by: the identifier we are searching by
        :param fields: the fields we are getting in our query
        :param table: the table we are searching must be prefixed by the schema
        :param start_date: the first date to get data on in '%Y-%m-%d' format
        :param end_date: the last date to get data on in '%Y-%m-%d' format
        :param adjust: should we adjust the pricing?
        :return: self
        """

        self._query_string['select'] = self._create_columns_to_select_sql(table=table,
                                                                          fields=fields + ['date', search_by],
                                                                          adjust=adjust)

        self._create_asset_filter_sql(assets=assets, search_by=search_by, start_date=start_date,
                                      end_date=end_date, timeseries_table=table)
        self._query_string['from'] = f"""{table} AS data JOIN {self._asset_table} AS uni 
                                        ON uni.{search_by} = data.{search_by}"""

        self._query_string['where'] = f"""data.date >= '{start_date}' AND data.date <= '{end_date}'"""

        self._df_options['index'] = ['date', search_by]
        self._query_metadata['asset_id'] = search_by
        self._query_metadata['fields'] = fields

        return self

    def query_static_table(self, table: str, fields: List[str], assets: Union[Iterable[any], str],
                           search_by: str, start_date: str = '1900', end_date: str = '3000'):
        """
        Reads static data fom the database.
        gets all variations of the static data
        if an asset has 3 changes of the static data then there will be 3 rows of static data for the asset
        :param table: the table we are searching must be prefixed by the schema
        :param assets: the assets we want to get data for, or a universe table
        :param search_by: the identifier we are searching by
        :param fields: the fields we are getting in our query
        :param start_date: the first date to get data on in '%Y-%m-%d' format, defaults to 1900
        :param end_date: the last date to get data on in '%Y-%m-%d' format, defaults to 3000
        :return: self
        """
        select_col_sql = self._create_columns_to_select_sql(table=table, fields=fields + [search_by], adjust=False)
        self._create_asset_filter_sql(assets=assets, search_by=search_by, start_date=start_date,
                                      end_date=end_date, timeseries_table=table)

        self._query_string['select'] = f"""{select_col_sql}, min(data.date) AS min_date, max(data.date) AS max_date"""
        self._query_string['from'] = f"""{table} AS data JOIN {self._asset_table} AS uni 
                                        ON uni.{search_by} = data.{search_by}"""
        self._query_string['where'] = f"""data.date >= '{start_date}' AND data.date <= '{end_date}'"""
        self._query_string['group_by'] = select_col_sql

        self._df_options['index'] = [search_by]
        self._query_metadata['asset_id'] = search_by
        self._query_metadata['fields'] = fields + ['min_date', 'max_date']

        return self

    def query_universe_table(self, table: str, fields: List[str], start_date: str, end_date: str,
                             index: List[str] = None, keep_date_col: bool = True):
        """
        makes sql query for a timeseries of a universe table
        :param table: the universe table to query
        :param fields: to full from the table
        :param start_date: first date to query on
        :param end_date: last date to query on
        :param index: what should the index of the returned frame be
        :param keep_date_col: should the date column be returned?
        :return: self
        """
        query_fields = fields
        if keep_date_col:
            query_fields += ['date']

        select_col_sql = self._create_columns_to_select_sql(fields=query_fields, adjust=False, tbl_alias='')

        self._query_string['select'] = select_col_sql
        self._query_string['from'] = (f"'{ETFUniverse().get_universe_path_parse(table)}'" if 'ETF' in table
                                      else f"universe.{table}")
        self._query_string['where'] = f"""date >= '{start_date}' AND date <= '{end_date}'"""

        if index:
            self._df_options['index'] = index

        return self

    def query_no_date_table(self, table: str, fields: List[str], assets: Union[Iterable[any], str],
                            search_by: str):
        """
        get data from a table with no date column
        :param table: the table we are searching must be prefixed by the schema
        :param fields: fields to pull from the table
        :param assets: the assets we want to get data for, or a universe table
        :param search_by: the identifier we are searching by
        :return: self
        """
        select_col_sql = self._create_columns_to_select_sql(table=table, fields=fields + [search_by], adjust=False)
        self._create_asset_filter_sql(assets=assets, search_by=search_by)

        self._query_string['select'] = select_col_sql
        self._query_string['from'] = f"""{table} AS data JOIN {self._asset_table} AS uni 
                                                ON uni.{search_by} = data.{search_by}"""

        self._df_options['index'] = [search_by]
        self._query_metadata['asset_id'] = search_by
        self._query_metadata['fields'] = fields + ['min_date', 'max_date']
        return self

    def distinct(self):
        """
        will make add a distinct keyword to the select clause of a query
        """
        self._query_string['select'] = 'DISTINCT ' + self._query_string['select']
        return self

    def set_freq(self, freq: Optional[str]):
        """
        sets the freq to apply to the date column
        freq of None will return a timestamp
        :param freq: the freq to set
        """
        self._df_options['freq'] = freq
        return self

    def set_calendar(self, calendar: str = 'NYSE', keep_old: bool = False):
        """
        sets the trading calendar to filter the dates by
        :param calendar: trading calendar we are resampling to, if 'full' then will use a 365 calendar
        :param keep_old: should we keep the old NULL columns?
        """
        # getting the first and last date of data in the query
        start_date, end_date = self._get_start_end_date()

        asset_id = self._query_metadata['asset_id']

        if calendar.lower() != 'full':
            # geting the trading calander
            trading_cal = mcal.get_calendar(
                calendar).valid_days(start_date=start_date, end_date=end_date).to_series().to_frame('date')
            full_date_id_sql = f"""(
                                    SELECT {asset_id}, date
                                    FROM {self._asset_table} as assets
                                    CROSS JOIN trading_cal_{calendar}
                                    ) as cal
                                """

            # registering the trading calander
            self._dict_asset_tables[f'trading_cal_{calendar}'] = trading_cal
            # self._con.con.register('trading_cal', trading_cal)
        else:
            make_full_date = lambda x: pd.Timestamp(x).strftime('%Y-%m-%d')
            full_date_id_sql = f"""(
                                    SELECT {asset_id}, range as date
                                        FROM {self._asset_table} as assets
                                        CROSS JOIN 
                                            (
                                            SELECT * 
                                            FROM range(DATE '{make_full_date(start_date)}', 
                                            DATE '{make_full_date(end_date)}', INTERVAL 24 HOURS)
                                            )
                                    ) as cal
                                """

        wanted_outer_cols = self._create_columns_to_select_sql(
            fields=self._query_metadata['fields'] + ['date', self._query_metadata['asset_id']], adjust=False)

        wanted_inner_cols = self._create_columns_to_select_sql(
            fields=self._query_metadata['fields'] + [self._query_metadata['asset_id']], adjust=False)
        # wanted_inner_cols = re.sub('data\.,|, data\.$', '', wanted_inner_cols)

        old_col_outter = f', old_date, old_{asset_id}' if keep_old else ''
        old_col_inner = f', data.date as old_date, data.{asset_id} as old_{asset_id}' if keep_old else ''

        raw_query = self.raw_sql
        self._query_string['select'] = f"""{wanted_outer_cols} {old_col_outter}"""
        self._query_string['from'] = f"""
                        (SELECT cal.date, cal.{asset_id}, {wanted_inner_cols} {old_col_inner}
                        FROM
                        ({raw_query}) AS data RIGHT JOIN {full_date_id_sql} 
                            ON data.{asset_id} = cal.{asset_id} and data.date = cal.date) as data
                        """

        self._clear_query_string(['select', 'from'])

        return self

    def resample(self, calendar: str, fill_limit: Optional[int] = None):
        """
        will resample any data down to daily data with the specified calendar
        :param fill_limit: the max amount of consecutive NA to fill in a row, 365 days
        :param calendar: trading calendar we are resampling to, if None then will use 365 calander
        """
        # Join ontot 365 calander
        # forward fill the data
        # if calendar then reindex for the calander
        self.set_calendar('full', keep_old=True)
        self._forward_fill(fill_limit)
        self.set_calendar(calendar)

        return self

    def _forward_fill(self, fill_limit: Optional[int] = None):
        """
        forward fills every column in a table
        :param fill_limit: max amount of fills in a row, CURRENTLY NOT WORKING
        """
        asset_id = self._query_metadata['asset_id']

        self._query_string['select'] += f""", COUNT(CASE WHEN data.old_{asset_id} IS NOT NULL THEN 1 END) 
                                            OVER (ORDER BY data.{asset_id}, "date" ROWS BETWEEN UNBOUNDED PRECEDING 
                                            AND CURRENT ROW) AS grouper """

        self.nest()

        row_num = ''
        if fill_limit:
            row_num = f""", row_number() OVER (PARTITION BY grouper, {self._query_metadata['asset_id']} 
                    ORDER BY date) as row_num"""

        query_str = ', '.join([f"MIN(data.{col}) OVER ffill as {col}" for col in self._query_metadata['fields']])
        self._query_string['select'] = f"""data.date, data.{asset_id}, {query_str} {row_num}"""
        self._query_string['window'] = f"""ffill AS (PARTITION BY {asset_id}, grouper)"""

        self._clear_query_string(['select', 'from', 'window'])

        if fill_limit:
            self._query_string['from'] = f"""({self.raw_sql}) as data"""
            self._query_string['select'] = self._create_columns_to_select_sql(
                fields=self._query_metadata['fields'] + [self._query_metadata['asset_id'], 'date'], adjust=False)
            self._query_string['where'] = f"""row_num <= {fill_limit}"""
            self._clear_query_string(['from', 'select', 'where'])

        return self

    def shift(self, column: str, days: int, new_name: Optional[str] = None):
        """
        Shifts data in a query back by n days
        :param column: the columns to shift back
        :param days: the amount of days to shift backwards
        :param new_name: the new name to assign to the column, if None then will overwrite old column
        """

        if new_name is None:
            new_name = f'{column}_lag_{days}'

        qs = self._query_string
        if qs['where'] != '' or (qs['window'] != '' and 'lag_window' not in qs['window']):
            self._query_string['from'] = f"""({self.raw_sql}) as data"""
            self._clear_query_string(['from'])

            wanted_cols = self._create_columns_to_select_sql(
                fields=self._query_metadata['fields'] + [self._query_metadata['asset_id']], adjust=False)
            self._query_string['select'] = wanted_cols
            self._query_string['window'] = f"""lag_window AS (PARTITION BY {self._query_metadata['asset_id']} 
                                                    ORDER BY data.date)"""

        if qs['window'] == '':
            self._query_string['window'] = f"""lag_window AS (PARTITION BY {self._query_metadata['asset_id']} 
                                                                ORDER BY data.date ASC)"""

        self._query_string['select'] += f""", lag({column}, {days}, NULL) OVER lag_window AS {new_name} """

        self._query_metadata['fields'] += [new_name]

        return self

    def join(self, other, on: Dict[str, str], tbl_name: str, join_type: str = 'INNER', nest: bool = True):
        """
        Joins this QueryConstructor with another QueryConstructor
        :param other: the other query constructor
        :param on: fields to join on, the key is the current QueryConstructor value is the other QueryConstructor
        :param tbl_name: the name of the other table
        :param join_type: the type of join to do
        :param nest: should we nest self before joining the two queries
        """

        to_join = other.raw_sql.replace('data', tbl_name)
        on_str = ' AND '.join([f"""data.{pair[0]} = {tbl_name}.{pair[1]}""" for pair in on.items()])

        if nest:
            self.nest()

        self._query_string['from'] += f""" {join_type} JOIN ({to_join}) AS {tbl_name} ON {on_str} """

        fields_to_add = list(set(other.fields) - set(self._query_metadata['fields']))

        if len(fields_to_add) > 0:
            self._query_string['select'] += ', ' + self._create_columns_to_select_sql(fields=other.fields, adjust=False,
                                                                                      tbl_alias=tbl_name)

        self._query_metadata['fields'] += fields_to_add
        self._dict_asset_tables = {**self._dict_asset_tables, **other.asset_tables}
        self.nest()

        return self

    def add_to_select(self, column: str, add_field: str = None):
        """
        add custom arithmetic to the select clause
        :param column: the calculation to add to the select column
        :param add_field: the name to add to the fields metadata, if None then wont asdd anything
        """
        self._query_string['select'] += f""", {column} """

        if add_field:
            self._query_metadata['fields'].append(add_field)

        return self

    def nest(self, rewrite_select: bool = True, include_date=True):
        """
        will nest the current sql statement in to the from clause
        and will name the table data
        :param rewrite_select: should we make the default select statement or leave the select statement blank?
        :param include_date: should we include date in the select statement
        """
        self._query_string['from'] = f""" ({self.raw_sql}) AS data """
        self._clear_query_string(['from'])

        fields = self._query_metadata['fields'] + [self._query_metadata['asset_id']]

        if include_date:
            fields.append('date')

        if rewrite_select:
            self._query_string['select'] = self._create_columns_to_select_sql(fields=fields, adjust=False)

        return self

    def where(self, where_condition: str):
        """
        adds a condition to the sql to the where cause string
        """
        self._query_string['where'] += f"""{' AND ' if self._query_string['where'] else ''} {where_condition}"""
        return self

    def shift_all(self):
        """
        shifts all columns in a query
        """

    def order_by(self, column: str, way: str = 'ASC'):
        """
        ordering the query by a column
        :param column: columns to order by
        :param way: the keyword to order by
        """
        self._query_string['order_by'] = f""" {column} {way} """
        return self

    def add_linker_table(self, link_table: str, join_on: Dict[str, str], link_columns: List[str],
                         link_start_col: str = None, link_end_col: str = None, extra_filter: str = ''):
        """
        joins a linker table onto the current query
        :param link_table:the table containing the linking information
        :param join_on: dict of the columns to join {timeseries_tbl_col : link_col}
        :param link_columns: the columns to get from the linking table
        :param link_start_col: the startdate of the link
        :param link_end_col: the end date of the link
        :param extra_filter: extra join filter to be applied
        """
        columns_linker = self._create_columns_to_select_sql(fields=set(link_columns + list(join_on.values())),
                                                            adjust=False, tbl_alias='link')

        on_clause = ' AND '.join([f'data.{main} = link.{link}' for main, link in join_on.items()])

        self._query_string['select'] += ', ' + columns_linker
        self._query_string['from'] += f""" LEFT JOIN {link_table} AS link ON ({on_clause} """

        if link_start_col and link_end_col:
            self._query_string['from'] += f""" AND data.date > link.{link_start_col} AND data.date < link.{link_end_col}"""

        self._query_string['from'] += f"""{' AND ' + extra_filter if extra_filter else ''})"""

        self._query_metadata['fields'] += link_columns

        return self

    def reset_universe(self, assets: Union[List[any], str], search_by: str = None, reindex: bool = True):
        """
        will reset the universe for adding from here on. will not alter old universes
        is string then will infer the start and end dates from the query
        :param assets: the assets we want to sent the new universe to. '*' not supported
        :param search_by: what should the search by be, will be set to the QueryConstructors main identifier
        :param reindex: should we reindex the frame by the universe constitutes
        :return: self
        """
        if search_by:
            self._query_metadata['fields'].append(self._query_metadata['asset_id'])
            self._df_options['index'].remove(self._query_metadata['asset_id'])
            self._df_options['index'].append(search_by)
            self._query_metadata['asset_id'] = search_by

        start_date, end_date = self._get_start_end_date()

        self._create_asset_filter_sql(assets=assets, search_by=self._query_metadata['asset_id'], start_date=start_date,
                                      end_date=end_date)

        if reindex:
            self._query_string['from'] += f""" JOIN {self._asset_table} AS uni 
                                        ON uni.{self._query_metadata['asset_id']} = 
                                        data.{self._query_metadata['asset_id']} """

        return self

    def dropna(self, column):
        """
        convince method to drop nas for a column
        """
        return self.where(f""" data.{column} IS NOT NULL """)

    def rename(self, mapping: Dict[str, str]):
        """
        Will rename the columns in the current select statement of the query
        :param mapping: dict of names to map {'lpermno':'permno', 'liid':'iid'}
        """
        for old, new in mapping.items():
            self._query_string['select'] = self._query_string['select'].replace(old, f'{old} AS {new}')
            self._query_metadata['fields'].remove(old)
            self._query_metadata['fields'].append(new)

        return self

    def _clear_query_string(self, keep: Iterable[str]) -> None:
        """
        clears all fields in self._query_string except for the fields passed to keep
        """
        clear = {'select', 'from', 'where', 'group_by', 'window', 'order_by'} - set(keep)
        for field in clear:
            self._query_string[field] = ''

    def _get_start_end_date(self) -> Tuple[str, str]:
        """
        returns the start and end query date parsed from the current sql query
        """
        searching = self._query_string['where'] + ' ' + self._query_string['from']
        start_date = re.compile("data\.date >= ([^\s]+)").search(searching).group(1).replace('\'', '')
        end_date = re.compile("data\.date <= ([^\s]+)").search(searching).group(1).replace('\'', '')
        return start_date, end_date

    def _create_asset_filter_sql(self, assets: Union[List[Union[int, str]], str], search_by: str,
                                 start_date: str = None, end_date: str = None, timeseries_table: str = None) -> None:
        """
        Sets the self._asset_table to the table name of thew table containing the assets
        param assets: the assets we want to get data for, or a universe table
            if not table then will register the passed assets as a view so they can be refrenced by the query
            if assets == '*' then timeseries_table must be True
        :param search_by: the identifier we are searching assets by
        :param start_date: the first date to get data on in '%Y-%m-%d' format, only used if assets is a universe table
        :param end_date: the last date to get data on in '%Y-%m-%d' format, only used if assets is a universe table
        :return: string of the table name that the wanted assets are in
        """

        asset_table = f'universe.{assets}'
        # checking to see if the user wants all columns
        if isinstance(assets, str) and assets == '*':
            if timeseries_table is None:
                raise ValueError('Must pass a timeseries_table if assets = \'*\'')

            asset_table = timeseries_table

        #  user passes a etf to use as universe
        if isinstance(assets, str) and 'ETF' in assets:
            path = ETFUniverse(con=self._con).get_universe_path_parse(assets)
            tbl_name = assets
            table = f"""CREATE TEMP TABLE {tbl_name} AS (SELECT DISTINCT {search_by}
                                    FROM '{path}'
                                    WHERE date >= '{start_date}' AND date <= '{end_date}')"""
            tbl_name = f'temp.{tbl_name}'

        # user passes a built universe
        elif isinstance(assets, str):
            tbl_name = '_' + hashlib.sha224(str(assets + str(timeseries_table)).encode()).hexdigest()
            table = f"""CREATE TEMP TABLE {tbl_name} AS (SELECT DISTINCT {search_by}
                        FROM {asset_table}
                        WHERE date >= '{start_date}' AND date <= '{end_date}')"""
            tbl_name = f'temp.{tbl_name}'

        # We have an iterable of assets
        elif isinstance(assets, Iterable):
            tbl_name = '_' + hashlib.sha224(str(list(assets)).encode('utf-8')).hexdigest()
            table = pd.DataFrame(assets, columns=[search_by])

        # dont know what the user passed raise an error
        else:
            raise ValueError(f'Assets type: {type(assets)} not recognised')

        # table = self._add_uni_args(assets, table)

        self._asset_table = tbl_name
        self._dict_asset_tables[tbl_name] = table

        #     def _add_uni_args(self, assets: any, table: any):
        #         """
        #         Parses string arguments for performing alterations to the universe before any SQL is executed
        #         :param assets: the assets passed by the user
        #         :param table: the current query to make the universe table
        #
        #         possible args:
        #             "CRSP_US_1000 --link"
        #             Will link to ccm llinker table and ibes linker table
        #         """
        #         if (not isinstance(assets, str)) or '--' in assets:
        #             return table
        #
        #         args = assets.split('--')[1:]
        #
        #         for arg in args:
        #             if 'link' in arg:
        #                 self._add_link_to_uni(arg, table)
        #             else:
        #                 raise ValueError(f'Command {arg} is not recognised')
        #
        #     def _add_link_to_uni(self, arg:str, table: str):
        #         """
        #         "CRSP_US_1000 --link"
        #          Will link to ccm llinker table and ibes linker table
        #          Assumes we have permno in universe
        #         """
        #
        #         link_tbl_from = arg.split(' ')[1]
        #         linto_tbl_to =
        #
        #         regex_ptn = r'FROM(.*?)WHERE'
        #         passed_from = re.search(regex_ptn, table).group(1)
        #
        #         new_from = f""" {passed_from} LEFT JOIN """
        #
        # passed_from += """ JOIN """

    def _create_columns_to_select_sql(self, fields: Iterable[str], adjust: bool, table: str = None,
                                      tbl_alias: str = 'data') -> str:
        """
        Creates sql code for the columns we want to get data for and adjusts the data when necessary
        :param table: the table we are searching must be prefixed by the schema, if not passed then adjust must be false
        :param fields: the fields we are getting in our query
        :param adjust: should we adjust the pricing?
        :param tbl_alias: the alias for the table
        :return: Sql columns for the select statement
        """

        if adjust and table.lower() not in DB_ADJUSTOR_FIELDS:
            raise ValueError(f'Table {table} is not in DB_ADJUSTOR_FIELDS. '
                             f'Valid tables are {list(DB_ADJUSTOR_FIELDS.keys())}')

        if adjust and table is None:
            raise ValueError('Must pass table if you are adjusting fields')

        # setting the table refrence
        if tbl_alias == '':
            alias = ''
        else:
            alias = f'{tbl_alias}.'

        columns_to_select = []
        for field in fields:
            if adjust:
                columns_to_select.append(self._adjust_field(field=field, table=table, alias=alias))
            else:
                columns_to_select.append(alias + field)

        return ', '.join(set(columns_to_select))

    @staticmethod
    def _adjust_field(field, table, alias) -> str:
        """
        Makes the SQL code to adjust a given field.
        If there s no adjustement to be done then it will just return data.field
        :param field: the single field we want to adjust
        """
        table_adj = DB_ADJUSTOR_FIELDS.get(table.lower())

        if table_adj is None:
            return f'{alias}{field}'

        for diff_adj in table_adj:
            fields_to_adjust = diff_adj.get('fields_to_adjust')
            function = diff_adj.get('function')
            wanted_diff_adj = field in fields_to_adjust

            if wanted_diff_adj and function:
                return (f'{diff_adj["function"]}({alias}{field} {diff_adj["operation"]} '
                        f'{alias}{diff_adj["adjustor"]}) AS {field}')

            if wanted_diff_adj:
                return f'{alias}{field} {diff_adj["operation"]} {alias}{diff_adj["adjustor"]} AS {field}'

        return f'{alias}{field}'

# handle lagging all columns by x
