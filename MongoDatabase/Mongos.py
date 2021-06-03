from datetime import datetime
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from pymongo.errors import ConnectionFailure
from typing import Any, Optional, Dict, Tuple, List
from threading import Thread, Event, RLock

from MongoDatabase.monLoggers import logging
logging.basicConfig(level=logging.INFO, format='(%(threadName)-9s) %(message)s')

__all__ = [
    'logging',
    'datetime',
    'Any',
    'Optional',
    'Dict',
    'Tuple',
    'List',
    'Thread',
    'RLock',
    'Event',
    'MongoBroker'
]


class RootMongo:
    __slots__ = ('_locker', 'root_client', 'working_db', 'working_col')

    def __init__(self,
                 start: bool = True,
                 client_ip: str = None,
                 db_name: str = None,
                 coll_name: str = None,
                 client: MongoClient = None,
                 database: Database = None,
                 collection: Collection = None):
        self._locker = RLock()
        self.root_client = client
        self.working_db = database
        self.working_col = collection
        if client_ip and start:
            self.start_client(ip=client_ip)
        if db_name and start:
            self.set_database(database_name=db_name)
        if coll_name and start:
            self.set_collection(collection_name=coll_name)

    @classmethod
    def start_mongo_client(cls, host: str = '127.0.0.1:27017', db: str = None, collect: str = None):
        return cls(client_ip=host, db_name=db, coll_name=collect)

    def start_client(self, ip: str = '127.0.0.1:27017'):
        assert self.root_client is None, 'MonClient instance should be closed before opening'
        with self._locker:
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
        Set working database object instance if not passed to class constructor
        :param database_name: DatabaseName -> str
        :return: None, setter_method
        """
        if self.root_client is None:
            self.start_client()
        self.working_db = self.root_client[database_name]

    def set_collection(self, collection_name):
        raise NotImplementedError()


class MongoBroker(RootMongo):

    def set_collection(self, collection_name: str) -> None:
        assert self.working_db is not None, 'Need activeDatabase to reference'
        if self.working_col is None:
            self.working_col = self.working_db.get_collection(collection_name)

    def get_server_info(self) -> Any:
        if self.root_client is None:
            self.start_client()
        return self.root_client.server_info()

    def get_nodes(self) -> Any:
        if self.root_client is None:
            self.start_client()
        return self.root_client.nodes

    def list_dbs_on_server(self) -> List:
        if self.root_client is None:
            self.start_client()
        return self.root_client.list_database_names()

    def list_col_in_db(self) -> List:
        assert self.working_db is not None, 'Connect to a database instance first'
        return self.working_db.list_collection_names()

    def mongo_insert_one(self, one_dump, col_name: str = None):
        """ Pass loads(JSON) and the collection name to perform insert on """
        assert self.working_db and one_dump is not None
        self.set_collection(col_name)
        with self._locker:
            self.working_col.insert_one(self.fallback_encoder(one_dump))

    def mongo_insert_many(self, big_dump, col_name: str = None) -> None:
        assert isinstance(big_dump, list), f'type(List[Dox,]) -> passed({type(big_dump)})'
        self.set_collection(collection_name=col_name)
        with self._locker:
            try:
                self.working_col.insert_many(big_dump)
            except OverflowError:
                print('Implement insert many fallback handler')

    def mongo_query(self, user_defined: dict = None,  metrics: str = None) -> Any:
        assert self.working_col is not None, 'Need activeCollection to query'
        if user_defined:
            _cursor = self.working_col.find(user_defined)
        if metrics:
            _cursor = self.working_col.find(
                {'_metrics': {'$eq': f'{metrics}'.upper()}})
        else:
            _cursor = self.working_col.find()

        try:
            _cursor = list(_cursor)[0]
            return self.fallback_decoder(_cursor)
        except IndexError:
            logging.warning('>>> VERIFY: [DOCUMENT_EXISTS + VALID_QUERY_FILTER]')
        except NotImplementedError:
            logging.warning('>>> QUERY FROM CLASS W/ DECODER IF ENCODER WAS IMPLEMENTED')
            return _cursor

    def mongo_update(self):
        """ TODO Implement updateOperators """
        pass

    def mongo_delete(self, del_db=False) -> None:
        """
        ExecuteCommand -> 'monClient.db.drop()' or 'db.collection.drop()'

        :param del_db: if true working_db.drop(); else working_col.drop()
        :return: None, check for confirmation in console server logs
        """
        # TODO Include document.drop()
        # TODO db.drop_collection needs (drop_collection OR drop_contents)
        if not del_db:
            self.working_db.drop_collection(name_or_collection=self.working_col)
        else:
            self.root_client.drop_database(name_or_database=self.working_db)

    def kill_client(self) -> None:
        """
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
    (hosted, dbm, colt) = ('127.0.0.1:27017', 'Glassnodes', 'BTC_24h')
    mons = MongoBroker.start_mongo_client(host=hosted, db=dbm, collect=colt)
    mons.mongo_delete()
    mons.kill_client()


########################################################
# JSON Document Validation
########################################################
# def validate_longs(data):
#     longer = LongHandler()
#     bats = longer.clean_writer(data)
#     print(f"\n* Encoded(py -> mongo):\n\t>>> {bats['_DATA_']['_divModified'][0]}")
#     jesus = longer.clean_reader(bats)
#     print(f"\n* Decoded(mongo -> py):\n\t>>> {jesus['_DATA_']['_divModified'][0]}")


# def quick_wizard(queries):
#     _glassed = _GlassClient()
#     return _glassed.glass_quest(index=queries[0], endpoint=queries[1], **queries[2])
