from bson.codec_options import TypeCodec, TypeRegistry
from bson.int64 import Int64

nums = {
    '_int64': 9223372036854775807,
    '__divs': 1720023146393883015,
    'uint64': 18446744073709551615,
    "__ma30": 105726798925408530000,
    "__ma60": 108361458222814630000,
}


class NumLongCodec(TypeCodec):
    # Max: 9223372036854775807
    # Oof: 105698318936170410
    long_mask = 1024
    python_type = int
    bson_type = Int64

    def transform_python(self, value):
        # assert value > 9223372036854775807, 'Investigate why callback was wrongly triggered'
        div, mod = divmod(value, self.mask)
        return {'div': div, 'mod': mod}

    def transform_bson(self, value):
        return (value['div'] * self.mask) + value['mod']


# num_long_codec = NumLongCodec()
#
# type_registry = TypeRegistry([num_long_codec])

if __name__ == '__main__':
    foobat = NumLongCodec()
    NUMBER_TO_LONG = 83
    long_num_hack = foobat.transform_python(NUMBER_TO_LONG)
    bson_safe = foobat.transform_bson(long_num_hack)
    print(f"\n>>> NUMBER_TO_LONG:\t\t({NUMBER_TO_LONG})"
          f"\n>>> Db_Repr.someKey:\t({long_num_hack['div']}, {long_num_hack['mod']})"
          f"\n>>> ABSOLUTE_MAX:\t\t({nums['_int64']})"
          f"\n>>> NUM_'NOT'_2_LONG:\t({bson_safe})")
