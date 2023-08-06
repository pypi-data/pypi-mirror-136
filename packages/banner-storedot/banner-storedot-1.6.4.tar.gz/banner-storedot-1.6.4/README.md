banner.connection:
    - Connection(Object):
        - ABS class

    - CacheConnection(Connection):
        - ABS class

    - MySqlConnection(Connection)(host, user, passwd, db, ssl_key, ssl_cert, name):
        - Create Connection object compatible with banner.queries  
        - **raises MySQLError for bad connection**

    - RedisConnection(CacheConnection)(host, port, passwd, db, ssl_key, ssl_cert, name, ttl):
        - Create CacheConnection object compatible with banner.queries  

    - connections(conns: Dict[str, Connection] = {}):
        - Getter/Setter for known(default) Connections dict

    - cache_connection(con: CacheConnection = None):
        - Getter/Setter for known(default) CacheConnection

banner.queries:
    - simple_query(query: str, connection=None, cache_connection=None, ttl=None) -> pd.DataFrame:
        - run a simple string query for Connection
        - connection=None try to get first known connection, **raise KeyError if None found**
        - Cache the result if cache_connection or banner.connection.cache_connection exists (ttl if provided otherwise use cache_connection.ttl)

    - table_query(table: str, columns: Union[list, str] = '*', condition: str = '1', connection=None, cache_connection=None, ttl=None, raw=False) -> pd.DataFrame:
        - Queries a given connection for 'SELECT {columns} FROM {table} WHERE {condition}'
        - Accepts both column values and labels
        - raw=True - column names as in db
        - Queries a given Connection(ip)/str of a known connection (or first known) return result as DataFrame
        - Cache if cache_connection or first known with ttl or default ttl for cache_connection
        - Raises OperationalError and KeyError(Failed to find a connection for given key) 

    - neware_query(device: int, unit: int, channel: int, test: int, connection: Union[Connection, str] = None, cache_connection=None, ttl=None, raw=False, dqdv=False):
        - query Connection for device, unit, channel, test 
        - connection=None try to get first known connection, **raise KeyError if None found**
        - raw=True return data as saved in the db
        - raw=False compute temp, voltage, current aswell as grouping by auxchl_id
        - dqdv=True -> banner.neware.calc_dq_dv 
        - Cache the result if cache_connection or banner.connection.cache_connection exists (ttl if provided otherwise use cache_connection.ttl)
        - **raises Type err if no data exists**

    - neware_query_by_test(table: str, cell: int, test: int, connection: Union[Connection, str] = None, cache_connection=None, ttl=None, raw=False, dqdv=False):
        - query Connection for device, unit, channel, test, as well as the connection storing the data
        - connection=None try to get first known connection, **raise KeyError if None found**
        - Try merging neware_cache_query for given test
        - raw=True return data as saved in the db
        - raw=False compute temp, voltage, current aswell as grouping by auxchl_id
        - dqdv=True -> banner.neware.calc_dq_dv 
        - Cache the result if cache_connection or banner.connection.cache_connection exists (ttl if provided otherwise use cache_connection.ttl)
        - returns neware_query for result values, **the connection has to be an entry in connections()**
        - **raises Type err if no data exists**
    
    - describe_table(table, connection: Union[Connection, str] = None)
        - Returns a series of table columns
        - connection=None try to get first known connection, **raise KeyError if None found**

    - describe(table, connection: Union[Connection, str] = None)
        - Returns a series of db tables
        - connection=None try to get first known connection, **raise KeyError if None found**

banner.neware:
    -calc_neware_cols(data: pd.DataFrame):
        - calculate neware columns for a valid neware DataFrame

    - calc_dq_dv(data: pd.DataFrame, raw=False):
        - Calculate DQ/DV for a valid neware df
        - raw=False: remove outliers

    - merge_cache(data: pd.DataFrame, cache_data: pd.DataFrame):
        - Given data(neware df), cache_data(neware_cache df), tries to merge cache_data into data  
        - ** Raises TypeError and Index Error**