from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from pymongo.errors import ConnectionFailure
from bson.json_util import dumps, loads

from MongoLoggers import logging
from GlassNode.GlassNodeBroker import GlassClient


class MongoBroker:
    def __init__(self, db: Database = None, cols: Collection = None):
        self._root_client = MongoClient(host='127.0.0.1:27017')
        try:
            self._root_client.admin.command('ismaster')
        except ConnectionFailure:
            logging.warning("Server not available. . .")
            raise
        self.live_database = db
        self.live_collection = cols

    def mongo_delete(self, db=False):
        if db:
            self._root_client.drop_database(name_or_database=self.live_database)
        else:
            self.live_database.drop_collection(name_or_collection=self.live_collection)

    def get_server_info(self):
        return self._root_client.server_info()

    def get_nodes(self):
        return self._root_client.nodes

    def set_database(self, database_name):
        assert self._root_client is not None, 'Need active server client to reference. . .'
        self.live_database = self._root_client[database_name]

    def set_collection(self, collection_name):
        assert self.live_database is not None, 'Need active db to reference. . .'
        self.live_collection = \
            self.live_database.get_collection(collection_name)

    def list_dbs_on_server(self):
        return self._root_client.list_database_names()

    def list_col_in_db(self):
        return self.live_database.list_collection_names()

    def curtain_close(self):
        assert self._root_client is not None, 'DB socket must be open to close'
        self._root_client.close()

    def mongo_command(self, cmd: str):
        self.live_database.command(command=cmd)

    def mongo_insert(self, dox):
        # int64_max = {'_int64_': 9223372036854775807}
        # uint64_max = {'uint64': 18446744073709551615}
        assert dox is not None, 'Need active collection to insert. . .'
        pa, pi = dox['_PARAMS_']['a'], dox['_PARAMS_']['i']
        self.live_collection = self.live_database[f"{pa}_{pi}"]
        self.live_collection.insert_one(dox)

    def mongo_query(self, q_metric=None, q_endpoint=None):
        assert self.live_collection is not None, 'Need active collection to query. . .'
        if q_metric:
            result = self.live_collection.find(
                {'_METRIC_': {'$eq': f'{q_metric}_{q_endpoint}'.upper()}})
        else:
            result = self.live_collection.find()
        logging.info(f'Cursor -> {result.collection}')
        return result


class LongHands:
    _MASK = 1024

    def fallback_encode(self, long_keys, bad_json) -> dict:
        # if key in 'v':
        #     elem[key] = elem[key]
        # elif key in long_keys:
        #     for failed in long_keys:
        #         elem[key][failed] = divmod(elem[key][failed], self._MASK)
        #
        # elif key in failed:
        #     elem[key]['v'] = divmod(elem[key]['v'], self._MASK)
        # else:
        #     for failed in long_keys:
        #         elem[key][failed] = divmod(elem[key][failed], self._MASK)
        for elem in bad_json:
            elem['t'] = elem['t']
            for key, val in elem.items():
                try:
                    elem[key]['v'] = divmod(elem[key]['v'], self._MASK)
                except KeyError:
                    pass
                except TypeError:
                    pass
                try:
                    for failed in long_keys:
                        elem[key][failed] = divmod(elem[key][failed], self._MASK)
                except KeyError:
                    pass
                except TypeError:
                    pass
        return {'_long_keys': long_keys, '_div_mask': self._MASK,  '_long_encoded': bad_json}

    def fallback_decode(self, bad_json):
        _dati = bad_json['_DATA_']
        _long_ki, _mask, _decode = _dati['_long_keys'], _dati['_div_mask'], _dati['_long_encoded']
        for elem in _decode:
            elem['t'] = elem['t']
            for modify in _long_ki:
                try:
                    _div_o, _mod_o = elem['o'][modify]
                    elem['o'][modify] = (_div_o * self._MASK) + _mod_o
                except KeyError:
                    pass
                try:
                    _div_v, _mod_v = elem['v'][modify]
                    elem['v'][modify] = (_div_v * self._MASK) + _mod_v
                except KeyError:
                    pass
        return _decode

    def validation(self, bar):
        _glassy = GlassClient()
        _data, _path, _params = _glassy.glass_quest(index=bar[0], endpoint=bar[1], **bar[2])
        _data = _data.json()
        _v_key = list(_data[0].keys())[1]
        for i in range(0, len(_data), 500):
            _filter = dict(filter(lambda elem: elem[1] > 9223372036854775807, _data[i][_v_key].items()))
            if len(_filter) > 0:
                _data = self.fallback_encode(tuple(_filter.keys()), _data)
                break
        return dumps({'_METRIC_':  _path, '_PARAMS_': _params, '_DATA_': _data}).encode('utf-8')


if __name__ == '__main__':
    from pprint import pprint
    MONGO = MongoBroker()
    LONGS = LongHands()

    query = ('indicators', 'hash_ribbon', {'a': 'BTC'})

    MONGO.set_database('typeTester')
    try:
        # MONGO.mongo_delete(db=True)

        # MONGO.mongo_insert(loads(LONGS.validation(query)))
        MONGO.set_collection('BTC_24h')
        CURSOR = MONGO.mongo_query(query[0], query[1])
        jesus = LONGS.fallback_decode(list(CURSOR)[0])

    except Exception as e:
        raise e

    # print(list(MONGO.list_col_in_db()))
    # print(list(MONGO.mongo_query()))

    MONGO.curtain_close()
    pprint(jesus)
