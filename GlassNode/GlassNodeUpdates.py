# from functools import reduce
# from pymongo.bulk import BulkWriteOperation
# import asyncio
import logging
from datetime import datetime
from ciso8601 import parse_datetime
from typing import List, Union, Dict
from collections import defaultdict


from GlassNodeAPI import GlassAIO, MongoServerStats


class UpdateConstructor(MongoServerStats):

    _NO_UPDATE = ('zxGlassPoints', 'zxBadRequests')
    _UPDATE_PROJECTOR = ('Parameters', 'Signature', 'TuplePath', 'Updated')

    def __init__(self):
        super(UpdateConstructor, self).__init__()
        self._update_proj = None
        self._update_coll = None
        self._update_dox = defaultdict(list)

    @property
    def update_proj(self):
        return {kp: True for kp in ['Updated', 'Parameters']}

    @property
    def update_coll(self) -> List:
        return [col for col in self._update_coll if col not in self._NO_UPDATE]

    @property
    def update_dox(self) -> Union[Dict[str, list], dict]:
        return dict(self._update_dox)

    @update_coll.setter
    def update_coll(self, value):
        self._update_coll = value

    @update_dox.setter
    def update_dox(self, value: tuple):
        _collection, _dox = value
        _master, _sig, _tp, _last = self._UPDATE_PROJECTOR
        _refresher = [(_ref[_master][_tp], _ref[_last]) for _ref in _dox]
        _params = _dox[0][_master][_sig]
        self._update_dox[_collection].append({'Params': _params, 'Metrics': _refresher})

    @update_coll.deleter
    def update_coll(self):
        del self._update_coll

    @update_dox.deleter
    def update_dox(self):
        del self._update_dox


class UpdateOrchestrator(UpdateConstructor, GlassAIO):
    """
    *** EXAMPLE START/UNTIL TIMESTAMPS BELOW ***
    * All timestamps: [<defined as <UTC> & <refer to interval start>]
    Monthly resolution: -> (May:2019)
     * <2019-05-01 00:00> THRU <2019-05-31 23:59>
    Weekly resolution: -> (Week:20)
     * <2019-05-13 00:00> THRU <2019-05-19 23:59>
    Daily resolution: -> (Day:5)
     * <2019-05-13 00:00> THRU <2019-05-13 23:59>
    Hourly resolution:
     * <2019-05-13 10:00> THRU <2019-05-13 10:59>
    10 Min resolution:
     * <2019-05-13 10:20> THRU <2019-05-13 10:29>
    """

    _STD = {'f': 'JSON', 'timestamp_format': 'humanized'}

    def __init__(self, nuke: tuple = None):
        super(UpdateOrchestrator, self).__init__()

    def quick_delete(self, clearing, doc=None, verify=False):
        if doc:
            _dox_filter = {'Parameters.TuplePath': {"$eq": doc}}
            self.mongo_drop_document(clearing, _dox_filter, check=verify)
        else:
            for _nuked in [clearing]:
                self.mongo_drop_collection(drop_col=_nuked, check=verify)
        self.kill_client()

    def get_update(self):
        self.update_coll = self.list_col_in_db()
        for _ups in self.update_coll:
            self.update_dox = (_ups, self.mongo_query(_ups, projector=self.update_proj))
            return self.update_dox


def build_updater(glassed):
    _glass_dates = glassed.get_update()
    glassed.kill_client()
    # pprint(_glass_dates, width=120, sort_dicts=False)


def time_dilation(_until: str):
    # {'PERIOD': ('<2010-07-17>', '<2013-06-01>'),
    #   * 'DURATION': {'Days': 320, 'Years': 2},
    #     * 'interval(<24h>)': 'approx.len(1050)',
    #     * 'interval(<1h>)': 'approx.len(25200)',
    #     * 'interval(<10m>)': 'approx.len(151200)'}
    _start = '2010-07-17'
    time1, time2 = parse_datetime(_start), parse_datetime(_until)
    _delta = (time2 - time1).days
    _years, _days = divmod(_delta, 365)
    _time_tables = {
        'PERIOD': (f'<{_start}>', f'<{_until}>'),
        'DURATION': {'Days': _days, 'Years': _years},
        f'interval(<24h>)': f'approx.len({_delta})',
        f'interval(<1h>)': f'approx.len({_delta * 24})',
        f'interval(<10m>)': f'approx.len({_delta * 144})',
    }
    pprint(_time_tables, indent=4, width=40, sort_dicts=False)


def small_nuke(_nuked: UpdateOrchestrator):
    for ipx in ['BTC_24h', 'BTC_1h', 'ETH_24h', 'zxBadRequests']:
        _nuked.mongo_drop_collection(ipx, check=True)


if __name__ == '__main__':
    # del_func(_worker, dox='price_usd', yes=True)
    from pprint import pprint
    _worker = UpdateOrchestrator()
    small_nuke(_worker)



