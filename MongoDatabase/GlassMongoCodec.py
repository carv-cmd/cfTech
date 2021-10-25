# Pymongo Example Link. Includes Datetime example below.
# https://pymongo.readthedocs.io/en/stable/examples/index.html

import datetime
from bson.codec_options import CodecOptions

# db.times.find_one()['date']

# datetime.datetime(2002, 10, 27, 14, 0)
#
# aware_times = db.times.with_options(
#     codec_options=CodecOptions(
#         tz_aware=True,
#         tzinfo=pytz.timezone('US/Pacific'))
# )
# result = aware_times.find_one()

# datetime.datetime(2002, 10, 27, 6, 0,  # doctest: +NORMALIZE_WHITESPACE
#                   tzinfo=<DstTzInfo 'US/Pacific' PST-1 day, 16:00:00 STD>)

# https://pymongo.readthedocs.io/en/stable/api/bson/son.html#bson.son.SON
