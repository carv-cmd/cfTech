# class MongoBroker:
#
#     __slots__ = ('root_client', 'working_db', 'working_col', '_long_check')
#
#     def __init__(self,
#                  client_ip: str = '127.0.0.1:27017',
#                  db_name: str = None,
#                  database: Database = None,
#                  collection: Collection = None):
#         self.root_client = self._start_client(host_ip=client_ip)
#         self.working_db = database
#         self.working_col = collection
#         if db_name:
#             self.set_database(db_name)
#
#     @staticmethod
#     def _start_client(host_ip: str = '127.0.0.1:27017'):
#         _initialze_client = MongoClient(host=host_ip)
#         try:
#             _initialze_client.admin.command('ismaster')
#         except ConnectionFailure:
#             logging.warning("Server not available. . .")
#             raise
#         return _initialze_client
#
#     @classmethod
#     def start_client(cls, hosting: str = '127.0.0.1:27017', db_name: str = None):
#         return cls(client_ip=hosting, db_name=db_name)
#
#     def set_database(self, database_name: str) -> None:
#         """
#         Set working database object instance if not passed to class constructor
#         :param database_name: DatabaseName -> str
#         :return: None, setter_method
#         """
#         if self.root_client is None:
#             self._start_client()
#         self.working_db = self.root_client[database_name]
#
#     def set_collection(self, collection_name: str) -> None:
#         assert self.working_db is not None, 'Need activeDatabase to reference'
#         self.working_col = self.working_db.get_collection(collection_name)
#
#     def get_server_info(self) -> Any:
#         if self.root_client is None:
#             self.root_client = self._start_client()
#         return self.root_client.server_info()
#
#     def get_nodes(self) -> Any:
#         if self.root_client is None:
#             self.root_client = self._start_client()
#         return self.root_client.nodes
#
#     def list_dbs_on_server(self) -> List:
#         if self.root_client is None:
#             self.root_client = self._start_client()
#         return self.root_client.list_database_names()
#
#     def list_col_in_db(self) -> List:
#         assert self.working_db is not None, 'Connect to a database instance first'
#         return self.working_db.list_collection_names()