import sqlalchemy
import pandas as pd
from enum import Enum
from sqlalchemy.engine import Engine
from sqlalchemy.inspection import inspect

class DbType(Enum):
    MySql = 1


def get_sql_dialect_driver(db_type : DbType) -> str:
    if db_type == DbType.MySql:
        return 'mysql+mysqlconnector'
    else:
        raise Exception('Unhandled db_type')


def sql_alchemy_engine(db_host : str,
                       db_port : str,
                       db_name : str,
                       db_user : str,
                       db_pswd : str,
                       db_type : DbType)-> Engine:
    dialet_driver = get_sql_dialect_driver(db_type)
    # create the db string: 'dialect+driver://user:pass@host:port/db'
    db_string = dialet_driver + '://' + db_user +':' + db_pswd +'@'+db_host+':'+db_port+'/'+db_name
    engine = sqlalchemy.create_engine(db_string)
    return engine


def get_primary_keys(db_engine : Engine,
                     tablename : str,
                     dbtype : DbType) -> []:
    if dbtype == DbType.MySql:
        with db_engine.connect() as con:
            result_set = con.execute('SHOW KEYS FROM ' + tablename + ' WHERE Key_name = \'PRIMARY\'')
            keys = [row['Column_name'] for row in result_set]
            return keys
    else:
        raise Exception('Unsupported')


def append_dataframe_into_table(df : pd.DataFrame, table_name : str, engine : Engine):
    df.to_sql(table_name,
              con=engine,
              if_exists='append',
              index=False)

