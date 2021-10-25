# import matplotlib.dates as mdates
# import mongoDB.Mongos
# import numpy
# import pandas
# import numba
import logging
from typing import Dict
from datetime import datetime
import matplotlib.pyplot as plt

from matplotlib import style
from GlassNode.GlassNodeAPI import GlassAIO

# logging.getLogger('matplotlib').setLevel(logging.ERROR)


class GlassMongoQueries(GlassAIO):
    def __init__(self):
        super(GlassMongoQueries, self).__init__()

    @staticmethod
    def _fallback_decoder(_long_ki, _latter_ki, _encoded, _mask) -> Dict:
        _start = datetime.now()
        for _item in _encoded:
            try:
                for _mod_key in _long_ki:
                    _div_n1, _div_n2 = _item[_latter_ki][_mod_key]
                    _item[_latter_ki][_mod_key] = (_div_n1 * _mask) + _div_n2
            except KeyError:
                _div_s1, _div_s2 = _item[_latter_ki]
                _item[_latter_ki] = (_div_s1 * _mask) + _div_s2
        logging.info(f'-> DECODING.TIME(<{(datetime.now() - _start).total_seconds()}>) -> {_long_ki}\n')
        return _encoded

    def fallback_decoder(self, _json_encoded) -> Dict:
        """

        :param _json_encoded:
        :return:
        """
        try:
            _data_key = self._DOX_SCHEMA[-1:][0]
            _div_num, _div_key, _div_modified = self._DIV_KEYS
            _encoded = _json_encoded[_data_key]
            _nested = ('v' if 'v' in _encoded[_div_modified][0] else 'o')
            _decoded = self._fallback_decoder(
                _long_ki=_encoded[_div_key],  # DivKeys.class_key
                _latter_ki=_nested,  # is (single|multi) part response?
                _encoded=_encoded[_div_modified],  # DivModified.class_key
                _mask=_encoded[_div_num]  # DivMask.class_key
            )
        except TypeError:
            _decoded = _json_encoded
        except Exception as e:
            raise e
        return _decoded


class MatPlotLibs:
    _growler = ''.join(['-' for i in range(50)])

    style.use('dark_background')

    @staticmethod
    def _make_subplots(**kwargs):
        return plt.subplots(subplot_kw=kwargs)

    @staticmethod
    def get_plt_params():
        print(plt.rcParams)

    def _loader_plt(self, dp):
        #     # plt.suptitle('GlassNode: Apes-Linked-Api')
        #     for result in dp:
        #         for col_key in result.keys():
        #             print(f'\n{self._growler}\nresult[col_key]: {result[col_key]}')
        #         plt.plot(result[col_key], label=f'{result.name}.{col_key}')
        #         plt.yscale('symlog', linthresh=('2008', '2014'))
        #
        # plt.xlabel('Time Series')
        # plt.ylabel('Apes')
        # fig = plt.gcf()
        # fig.set_size_inches(9, 6, forward=True)
        # # plt.legend(loc='upper left')
        # plt.tight_layout()
        # plt.show()
        pass

    def glass_pandas(self):
        """ TODO Implement pandas loader """
        # pandas.set_option('display.width', 120)
        # TODO timeit (git_implementation) vs (my_implementation)
        #  * df = pd.DataFrame(json.loads(r.text))
        #  * df = df.set_index('t')
        #  * df.index = pd.to_datetime(df.index, unit='s')
        #  * df = df.sort_index()
        #  * s = df.v
        #  * s.name = '_'.join(url.split('/')[-2:])
        #  * return s
        # for elem in self.loaded:
        #     _metric, _data = elem[1]['_metrics'], elem[1]['_data']
        #     try:
        #         frame_keys = ['t'] + list(_data[0]['o'].keys())
        #         framed = pandas.DataFrame(
        #             data=[{k: (_data[iters]['t'] if k in 't' else _data[iters]['o'][k])
        #                    for k in frame_keys} for iters in range(len(_data))],
        #             columns=frame_keys)
        #     except KeyError:
        #         framed = pandas.DataFrame(_data)
        #     framed.set_index('t', inplace=True)
        #     framed.index = pandas.to_datetime(
        #         framed.index.to_flat_index(), unit='s', infer_datetime_format=True)
        #     framed.sort_index(inplace=True)
        #     framed.name = _metric
        #     print(framed.name)
        #     print(framed)


if __name__ == '__main__':
    pass
