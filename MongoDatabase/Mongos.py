# import signal
from typing import Any, Dict, List
from threading import RLock
# from collections import

from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from pymongo.errors import ConnectionFailure

from MongoDatabase.monLoggers import logging, event_listeners

logging.basicConfig(level=logging.INFO, format='(%(threadName)-9s) %(message)s')

__all__ = ['MongoBroker', 'MongoServerStats']


class _BaseMongo(dict):

    def __init__(self):
        super(_BaseMongo, self).__init__()
        self._root_client = None
        self._working_db = None
        self._working_col = None

    @property
    def root_client(self) -> MongoClient:
        return self._root_client

    @property
    def working_db(self) -> Database:
        return self._working_db

    @property
    def working_col(self) -> Collection:
        return self._working_col

    @root_client.setter
    def root_client(self, value: str) -> None:
        # logging.info(f'<<<SETTING.root_client[{value}]>>>')
        assert self._root_client is None, 'MonClient instance should be closed before opening'
        try:
            self._root_client = MongoClient(host=value, event_listeners=event_listeners)
            self._root_client.admin.command('ismaster')
        except ConnectionFailure:
            raise logging.warning("Server not available. . .")

    @working_db.setter
    def working_db(self, value: str):
        # logging.info(f'<<<SETTING.working_db[{value}]>>>')
        assert self._root_client is not None, 'Need MongoClient.instance to reference!'
        try:
            if value is not self.working_db.name:
                self._working_db = self.root_client.get_database(name=value)
        except AttributeError:
            self._working_db = self.root_client.get_database(name=value)

    @working_col.setter
    def working_col(self, value: str) -> None:
        # logging.info(f'<<<SETTING.working_col[{value}]>>>')
        assert self._working_db is not None, '>>> Need MongoClient.db.instance to reference!'
        try:
            if value is not self.working_col.name:
                self._working_col = self._working_db.get_collection(name=value)
        except AttributeError:
            self._working_col = self._working_db.get_collection(name=value)


class MongoBroker(_BaseMongo):

    # __slots__ = ('_locker', 'root_client', 'working_db', 'working_col')

    def __init__(self, start: bool = True, mon_ip: str = None, db_name: str = None, coll_name: str = None):
        super(MongoBroker, self).__init__()
        self.locker = RLock()
        if start:
            if mon_ip:
                self.root_client = mon_ip
            if db_name:
                self.working_db = db_name
            if coll_name:
                self.working_col = coll_name

    def kill_client(self) -> None:
        """
        MongoEquivalent -> TODO WhatCommand: MongoClient.terminate/close?
        Safely terminate/close MongoDB socket connection. *(Instance reused if started again)

        :return: None
        """
        assert self.root_client is not None, 'MongoClient socket must be open before closing'
        self.root_client.close()

    def mongo_drop_database(self, drop_db: Any = None, check: bool = False) -> None:
        """
        MongoEquivalent -> MongoClient.db.drop()

        :param drop_db: accepts: [client.database, database.name]
        :param check: Must pass check=True to execute db.drop()
        :return: None
        """
        assert check is True, f'* VERIFY: [check_is_True -> {check}]'
        assert self.root_client is not None, 'Need valid Mongo.client to reference'
        if not drop_db:
            self.root_client.drop_database(name_or_database=self.working_db)
        elif isinstance(drop_db, (Database, str)):
            self.root_client.drop_database(name_or_database=drop_db)
        else:
            raise TypeError('NoLive.db:(name|obj): PRESET|PASSED by caller')

    def mongo_drop_collection(self, drop_col: Any = None, check: bool = False) -> None:
        """
        MongoEquivalent -> db.collection.drop()

        :param drop_col: accepts: [db.collection, collection.name]
        :param check: Must pass check=True to execute db.collection.drop()
        :return: None
        """
        assert check is True, f'Invalid: [check_is_True -> {check}]'
        assert self.working_db is not None, 'Need valid db.instance to reference'
        if not drop_col:
            self.working_db.drop_collection(name_or_collection=self.working_col)
        elif isinstance(drop_col, (Collection, str)):
            self.working_db.drop_collection(name_or_collection=drop_col)
        else:
            raise TypeError("NoLive.db.Collection:(name|obj): PRESET|PASSED by caller ")

    def mongo_insert_many(self, collection: str, big_dump: List) -> None:
        """
        MongoEquivalent -> db.collection.insertMany()
        Better suited for textDox inserts when structuring is of lesser importance.

        :param collection: str: Optional[collection_name]
        :param big_dump: list: Array of valid documents.
        :return: None
        """
        with self.locker:
            try:
                self.working_col = collection
                self.working_col.insert_many(big_dump)
            except Exception as e:
                raise e

    def mongo_insert_one(self, collection: str, one_dox: Dict) -> None:
        """
        MongoEquivalent -> db.collection.insertOne()
        Inserts single document to the active db.collection.instance.

        :param collection: str = db.collection.name
        :param one_dox: type['dict', 'mutable.mapping', 'bson.RAW.doc']
        :return:
        """
        with self.locker:
            try:
                self.working_col = collection
                self.working_col.insert_one(one_dox)
            except Exception as e:
                raise e

    def mongo_query(self, collection: str, mon_filter: dict = None, projector: dict = None) -> List:
        """
        MongoEquivalent -> db.collection.find()

        :param mon_filter: Query filter as per MongoDB documentation specifications
        :return: List[obj(documents_matched_filter), ...]
        """
        _no_id = {'_id': False}
        with self.locker:
            try:
                self.working_col = collection
                projector = {'projection': {**_no_id, **projector}}
                if mon_filter:
                    projector = {**{'filter': mon_filter}, **projector}
                return list(self.working_col.find(**projector))
            except Exception as e:
                raise e

    def mongo_replace_one(self, collection: str, one_dox: Dict) -> None:
        """
        MongoEquivalent -> db.collection.replaceOne()
        Replaces whole documents, if document doesnt exist insert is performed

        :param one_dox: dict: document to find and replace, upsert if !exist
        :param collection: str
        :return:
        """
        with self.locker:
            try:
                self.working_col = collection
                _filter = {'_metrics': {'$eq': one_dox[1]}}
                self.working_col.replace_one(filter=_filter, replacement=one_dox, upsert=True)
            except Exception as e:
                raise e

    def mongo_drop_document(self):
        """ TODO Implement single document drop """

    def mongo_bulk_write(self):
        """ TODO Implement bulkWrite/executeWrite methods """

    def mongo_update(self):
        """ TODO Implement updateOperators """


class MongoServerStats(MongoBroker):

    def get_server_info(self) -> Any:
        assert self.root_client is not None, 'Connect to client instance first'
        return self.root_client.server_info()

    def get_nodes(self) -> Any:
        assert self.root_client is not None, 'Connect to client instance first'
        return self.root_client.nodes

    def list_dbs_on_server(self) -> List:
        assert self.root_client is not None, 'Connect to client instance first'
        return self.root_client.list_database_names()

    def list_col_in_db(self) -> List:
        assert self.working_db is not None, 'Connect to database instance first'
        return self.working_db.list_collection_names()

    def mongo_command(self, cmd: str):
        self.working_db.command(command=cmd)


if __name__ == '__main__':
    pass
