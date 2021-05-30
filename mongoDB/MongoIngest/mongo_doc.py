# import json
from pprint import pprint

from pymongo import MongoClient
# import bson

# from RESTClient import Rested




# class MonClient(MongoClient):
#     def __init__(self, host_server):
#         super(MonClient, self).__init__()
#         self.db_client = MongoClient(host_server)
#         self.daterbase = None
#         self.container = None
    
    # @classmethod
    # def initially_as(cls, host):
    #     print('\n>>> RUNNING: @classmethod.initialize_client')fgfdsgfdgfdgdg
    #     return cls(host_server=host)
    #
    # @property
    # def daterbase(self):
    #     print('>>> Calling: @property.daterbase')
    #     return self.daterbase
    #
    # @property
    # def container(self):
    #     print('>>> Calling: @property.container')
    #     return self.container
    #
    # @daterbase.setter
    # def daterbase(self, value):
    #     print(f'>>> Calling: @daterbase.setter')
    #     self.daterbase = value
    #     # self.daterbase = self.db_client[value]
    #
    # @container.setter
    # def container(self, value):
    #     print(f'>>> Calling: @container.setter')
    #     self.container = value
    #     # self.container = self.daterbase[value]


# class UserClient(MonClient):
#     def __init__(self, host_server):
#         super(UserClient, self).__init__(host_server)

    # def set_db(self, db):
    #     self.daterbase = self.db_client[db]
    #
    # def set_col(self, col):
    #     self.container = self.daterbase[col]


# monClient = r'mongodb://localhost:27017'
#
# bb = MonClient.
# cc = UserClient.initially_as(monClient)
#
# # cc.set_db('test')
# # cc.set_col('testCollection')
#
# cc.close()


# class Foobar(MonClient):
#     def __init__(self, host_server):
#         super(Foobar, self).__init__(host_server=host_server)
#         self.wrk_database = None
#         self.wrk_collection = None
#
#     @property
#     def wrk_database(self):
#         print(f'>>> RUNNING: @property.wrk_database')
#         return self.wrk_database
#
#     @property
#     def wrk_collection(self):
#         print(f'>>> RUNNING: @property._working_col')
#         return self.wrk_collection
#
#     @wrk_database.setter
#     def wrk_database(self, value):
#         print(f'>>> RUNNING: @__working_db.setter')
#         try:
#             self.wrk_database = self.db_client[value]
#         except ConnectionError or ConnectionRefusedError:
#             self.wrk_database = None
#
#     @wrk_collection.setter
#     def wrk_collection(self, value):
#         print(f'>>> RUNNING: @__working_col.setter')
#         try:
#             self.wrk_collection = self.wrk_database[value]
#         except ConnectionError or ConnectionRefusedError:
#             self.wrk_collection = None
#
#     def ready_client(self, live_database, collection):
#         try:
#             self.wrk_database = live_database
#             self.wrk_collection = collection
#         except AttributeError or TypeError or ConnectionError:
#             raise
#
#     def finder(self):
#         try:
#             for dater in self.wrk_collection.find():
#                 pprint(dater)
#         except AttributeError or TypeError:
#             raise

'wombat'

# monClient = r'mongodb://localhost:27017'
# mC_subset = dict(live_database='test', collection='testCollection')
#
# cc = Foobar.initially_as(monClient)
# cc.ready_client(**mC_subset)
#
# print(f'\ncc.wrk_database: {cc.wrk_database}\n'
#       f'\ncc.wrk_collection: {cc.wrk_collection}')

# cc.finder()

# cc.db_client.close()

'fuck'

# @staticmethod
# def _get_data(end_points, **kwargs):
#     Rested.set_help(enders=end_points, **kwargs)
#     try:
#         return json.dumps(Rested.daters)
#     except json.JSONDecodeError:
#         raise
#
# @classmethod
# def db_insert(cls, end_points, **kwargs):
#     try:
#         cls.testCollection.insert_one(json.loads(cls._get_data(end_points, **kwargs)))
#         print('\n>>> testCollection.insert_one(rested.daters)\n\t<<< FAILED SUCCESSFULLY >>>')
#
#     except TypeError:
#         print('\n>>> testCollection.insert_one(rested.daters)\n\t<<< FAILED FATALLY >>>')
#         raise

# def _insert_wrap(func):
#     def feeder(end_pts, **kwargs):
#         try:
#             Rested.set_help(enders=end_pts, **kwargs)
#             rest_response = json.dumps(Rested.daters)
#             print('\n>>> Rested <<< FAILED SUCCESSFULLY >>>')
#         except json.JSONDecodeError or BytesWarning or UnicodeEncodeError:
#             return None
#
#         try:
#             testCollection.insert_one(json.loads(rest_response))
#             print('\n>>> testCollection.insert_one(rested.daters)\n\t<<< FAILED SUCCESSFULLY >>>')
#
#         except TypeError:
#             print('\n>>> testCollection.insert_one(rested.daters)\n\t<<< FAILED FATALLY >>>')
#         return feeder
#
#
# def _find_wrap(func):
#     def finder():
#         try:
#             for dater in testCollection.find():
#                 pprint(dater)
#         except TypeError:
#             raise
#     return finder
#
#
# def _delete_wrap(func):
#     def deleter():
#         """ TODO Create delete query filter """
#         try:
#             testCollection['Top_Percent_Change'].delete_one()
#         except TypeError:
#             raise
#     return deleter
#
#
# @_insert_wrap
# def create():
#     pass
#
#
# @_find_wrap
# def read():
#     pass
#
#
# @_delete_wrap
# def delete():
#     pass


# kk = ['Top_Percent_Change']  # , 'Top_By_Price']
# create(kk)
# read()
# update()
# delete()

# monClient.close()

# bulk_write(), as long as UpdateMany or DeleteMany are not included.
# delete_one()
# insert_one()
# insert_many()
# replace_one()
# update_one()
# find_one_and_delete()
# find_one_and_replace()
# find_one_and_update()

# In Python, @g @f def foo() translates to foo=g(f(foo).
