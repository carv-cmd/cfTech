# import signal
from typing import Any, Optional, Dict, Tuple, List

from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from pymongo.errors import ConnectionFailure

from MongoDatabase.monLoggers import logging

logging.basicConfig(level=logging.INFO, format='(%(threadName)-9s) %(message)s')

__all__ = [
    'logging',
    'Any',
    'Optional',
    'Dict',
    'Tuple',
    'List',
    'MongoBroker'
]


class _RootMongo:
    __slots__ = ('_locker', 'root_client', 'working_db', 'working_col')

    def __init__(self,
                 start: bool = True,
                 client_ip: str = None,
                 db_name: str = None,
                 coll_name: str = None,
                 client: MongoClient = None,
                 database: Database = None,
                 collection: Collection = None):
        self.root_client = client
        self.working_db = database
        self.working_col = collection
        if start:
            if client_ip:
                self.start_client(ip=client_ip)
            if db_name:
                self.set_database(database_name=db_name)
            if coll_name:
                self.set_collection(collection_name=coll_name)

    @classmethod
    def start_mongo_client(cls, host: str = '127.0.0.1:27017', db: str = None, collect: str = None):
        return cls(client_ip=host, db_name=db, coll_name=collect)

    def start_client(self, ip: str = '127.0.0.1:27017') -> None:
        assert self.root_client is None, 'MonClient instance should be closed before opening'
        _initialze_client = MongoClient(host=ip)
        try:
            _initialze_client.admin.command('ismaster')
        except ConnectionFailure:
            logging.warning("Server not available. . .")
            raise
        finally:
            self.root_client = _initialze_client

    def set_database(self, database_name: str) -> None:
        """
        Sets MongoClient.db.instance pointer.
        If database does not exist, one is created on method call.

        :param database_name: DatabaseName -> str
        :return: None -> Indicates successful setter.op
        """
        assert self.root_client is not None, 'Need active client to reference'
        try:
            if database_name is not self.working_db.name:
                self.working_db = self.root_client.get_database(name=database_name)
        except AttributeError:
            self.working_db = self.root_client.get_database(name=database_name)
        except Exception as e:
            raise e
        finally:
            return None

    def set_collection(self, collection_name: str) -> None:
        """
        Sets db.collection.instance pointer.
        If collection does not exist, one is created on method call.

        :param collection_name: str: Collection.name
        :return: None -> Indicates successful setter.op
        """
        assert self.working_db is not None, 'Need activeDatabase to reference'
        try:
            if collection_name is not self.working_col.name:
                self.working_col = self.working_db.get_collection(name=collection_name)
        except AttributeError:
            self.working_col = self.working_db.get_collection(name=collection_name)
        except Exception as e:
            raise e
        finally:
            return None

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

    def mongo_drop_database(self, drop_db: Any = None, check: bool = False) -> None:
        """
        MongoEquivalent -> MongoClient.db.drop()

        :param drop_db: accepts: [client.database, database.name]
        :param check: Must pass check=True to execute db.drop()
        :return: None
        """
        assert self.root_client is not None, 'Need valid Mongo.client to reference'
        assert check is True, f'* VERIFY: [check_is_True = {check}]'
        if not drop_db:
            self.root_client.drop_database(name_or_database=self.working_db)
        elif isinstance(drop_db, (Database, str)):
            self.root_client.drop_database(name_or_database=drop_db)
        else:
            raise TypeError('NoLive.db:(name/obj): PRESET|PASSED by caller')

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
            raise TypeError("NoLive.db.Collection:(col.name/col.obj): PRESET|PASSED by caller ")


class MongoBroker(_RootMongo):

    # Endpoint fast/lazy requests-projection-filter
    _ID_IGNORE = {'_id': False}

    def mongo_bulk_write(self):
        pass

    def mongo_insert_many(self, big_dump: list, col_name: str = None) -> None:
        """
        MongoEquivalent -> db.collection.insertMany()
        Better suited for textDox inserts when structuring is of lesser importance.

        :param big_dump: list: Array of valid documents.
        :param col_name: str: Optional[collection_name]
        :return: None
        """
        assert isinstance(big_dump, list), 'Insert Many Requires Array/List data structure'
        self.set_collection(col_name)
        try:
            self.working_col.insert_many(big_dump)
        except Exception as e:
            raise e

    def mongo_insert_one(self, one_dox, col_name: str = None):
        """
        MongoEquivalent -> db.collection.insertOne()
        Inserts single document to the active db.collection.instance.

        :param one_dox: type['dict', 'mutable.mapping', 'bson.RAW.doc']
        :param col_name: str = db.collection.name
        :return:
        """
        assert self.working_db is not None, 'Need active db instance to reference.'
        assert isinstance(one_dox, dict), 'Object must be dictionary to insert.'
        self.set_collection(col_name)
        try:
            self.working_col.insert_one(one_dox)
        except Exception as e:
            logging.warning(f'* mon_sert_one raised -> {e}')

    def mongo_replace_one(self, one_dox: dict, col_name: str = None):
        """
        MongoEquivalent -> db.collection.replaceOne()
        Replaces whole documents, if document doesnt exist insert is performed
        :param one_dox: dict: document to find and replace, upsert if !exist
        :param col_name: str
        :return:
        """
        assert self.working_db is not None, 'Need active db instance to reference'
        self.set_collection(col_name)
        try:
            self.working_col.replace_one(
                filter={'_metrics': {'$eq': one_dox[1]}},
                replacement=self.fallback_encoder(one_dox),
                upsert=True)
        except Exception as e:
            raise e

    def mongo_query(self, user_defined: dict = None, projection: dict = None) -> Any:
        """
        MongoEquivalent -> db.collection.find()

        :param user_defined: Query filter as per MongoDB documentation specifications
        :return: List[obj(documents_matched_filter), ...]
        """
        assert self.working_col is not None, 'Need activeCollection to query'
        if user_defined:
            _cursor = self.working_col.find(user_defined, projection=projection)
        else:
            _cursor = self.working_col.find()
        return self.fallback_decoder(list(_cursor)[0])

    def mongo_update(self):
        """ TODO Implement updateOperators """
        pass

    def kill_client(self) -> None:
        """
        MongoEquivalent -> TODO WhatCommand: MongoClient.terminate/close?
        Safely terminate/close MongoDB socket connection. *(Instance reused if started again)

        :return: None
        """
        assert self.root_client is not None, 'MongoClient socket must be open before closing'
        self.root_client.close()

    def mongo_command(self, cmd: str):
        self.working_db.command(command=cmd)

    def fallback_encoder(self, _json_decoded):
        raise NotImplementedError()

    def fallback_decoder(self, _json_encoded):
        raise NotImplementedError()


if __name__ == '__main__':
    _delete = 'BTC_24H', 'BadRequests'
    for _thermonuclear in _delete:
        (hosted, dbm, colt) = ('127.0.0.1:27017', 'Glassnodes', _thermonuclear)
        mons = MongoBroker.start_mongo_client(host=hosted, db=dbm, collect=colt)
        mons.mongo_drop_collection(check=True)
        mons.kill_client()
