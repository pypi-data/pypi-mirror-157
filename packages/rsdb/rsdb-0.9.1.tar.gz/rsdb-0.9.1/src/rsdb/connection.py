import sys
import os
import pyodbc
import ipaddress
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from urllib.parse import quote_plus
from collections.abc import Iterable
from typing import Union


class Connector:
    """
    Class building connection strings to the model database
    """
    _server_name: str
    _uid: str
    _pwd: str
    _ip: str
    _port: int
    _driver: str

    def __init__(self,
                 ip: str = '127.0.0.1',
                 port: int = 1433,
                 server_name: str = '.\RISKSPEC_PSA2012',
                 uid: str = 'sa',
                 pwd: str = '82sbDiF%5_2&33d%hvTP!4'):
        """Setting parameters for connecting to the SQL server"""

        if len(server_name) < 0:
            ValueError('Server name should be longer')
        if 0 > port > 65535:
            ValueError('The server port must be between 1 and 65534')

        try:
            self._ip = ipaddress.ip_address(ip)
        except ValueError:
            ValueError('Invalid ip address format')

        self._server_name = server_name
        self._uid = uid
        self._pwd = pwd
        self._port = port

    def AttachModelFromFile(self, file_path: str) -> str:
        dbname = os.path.basename(file_path).split('.')[0]
        params = self.GetConnectString(model_name='master')
        try:
            with pyodbc.connect(params) as cnxn:
                cnxn.autocommit = True
                with cnxn.cursor() as cursor:
                    cursor.execute(
                        f'''
                            USE [master];
                            EXEC sp_attach_db
                            @dbname={dbname},
                            @filename1 = '{file_path}';
                            ''')
        except pyodbc.Error as ex:
            print(f'pyodbc error: {ex.args[0]}', file=sys.stderr)
        return self.GetConnectString(dbname)

    def DetachModel(self, model_name: Union[str, Iterable[str]]):
        if isinstance(model_name, str):
            params = self.GetConnectString('master')
            try:
                with pyodbc.connect(params) as cnxn:
                    cnxn.autocommit = True
                    with cnxn.cursor() as cursor:
                        cursor.execute(
                            f'''
                                    USE [master];
                                    ALTER DATABASE [{model_name}] SET TRUSTWORTHY ON;
                                    EXEC sp_detach_db @dbname={model_name};
                                    ''')
            except pyodbc.Error as ex:
                print(f'pyodbc error: {ex.args[0]}', file=sys.stderr)

    def DetachAll(self):
        """
        Detach all models connected to the SQL server
        """
        params = self.GetConnectString('master')
        for model_name in self.GetAvailableModels():
            try:
                with pyodbc.connect(params) as cnxn:
                    cnxn.autocommit = True
                    with cnxn.cursor() as cursor:
                        cursor.execute(
                            f'''
                                USE [master];
                                ALTER DATABASE [{model_name}] SET TRUSTWORTHY ON;
                                EXEC sp_detach_db @dbname={model_name};
                                ''')
            except pyodbc.Error as ex:
                print(f'pyodbc error: {ex.args[0]}', file=sys.stderr)

    def GetAvailableModels(self, name_only: bool = True) -> list:
        """
        Get a list of all active models on the SQL server
        """
        params = self.GetConnectString('master')
        try:
            with pyodbc.connect(params) as cnxn:
                with cnxn.cursor() as cursor:
                    cursor.execute(
                        '''
                        SELECT * FROM master.dbo.sysdatabases
                        WHERE name NOT IN ('master', 'tempdb', 'model', 'msdb')
                        ''')
                    rows = cursor.fetchall()
                    if len(rows) > 0:
                        if name_only:
                            return [r[0] for r in rows]
                        else:
                            return rows
        except pyodbc.Error as ex:
            print(f'pyodbc error: {ex.args[0]}', file=sys.stderr)

    def GetConnectString(self, model_name: str) -> str:
        """
        Get model connection string
        """
        if sys.platform == 'linux':
            # Удалённое подключение для Linux через FreeTDS и unixODBC
            return f'driver={{FreeTDS}};server={self._ip};port={self._port};database={model_name};uid={self._uid};pwd={self._pwd};'

        elif sys.platform == 'win32':
            # Локальное подключение для Windows со стандартным драйвером
            return f'DRIVER={{SQL Server}};SERVER={self._server_name};DATABASE={model_name};Uid={self._uid};Pwd={self._pwd};'
        else:
            raise Exception('OS not supported')

    def GetCMDConnectString(self, model_name: str) -> str:
        """
        Get model connection string for console call
        """
        if sys.platform == 'linux':
            return f'mssql+pyodbc://{self._uid}:{self._pwd}@{self._ip}\{model_name}?driver=FreeTDS'
        elif sys.platform == 'win32':
            return f'mssql+pyodbc://{self._uid}:{self._pwd}@{self._server_name}/{model_name}?driver=SQL+Server+Native+Client+11.0'
        else:
            raise Exception('OS not supported')

    def GetModelSession(self, model_name: str):
        """
        Get SqlAlchemy session
        """
        params = quote_plus(
            f'DRIVER=FreeTDS;SERVER={self._ip};PORT={self._port};DATABASE={model_name};UID={self._uid};Pwd={self._pwd};TDS_Version=8.0;')
        engine = create_engine("mssql+pyodbc:///?odbc_connect=%s" % params)

        Base = declarative_base(engine)
        metadata = Base.metadata
        Session = sessionmaker(bind=engine, future=True)
        return Session


if __name__ == "__main__":
    print('Модуль не может быть запущен')
