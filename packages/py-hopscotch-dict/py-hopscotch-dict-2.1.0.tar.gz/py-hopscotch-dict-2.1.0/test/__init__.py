################################################################################
#                              py-hopscotch-dict                               #
#    Full-featured `dict` replacement with guaranteed constant-time lookups    #
#                    (C) 2017, 2019-2020, 2022 Jeremy Brown                    #
#                Released under Prosperity Public License 3.0.0                #
################################################################################

from sys import maxsize

from hypothesis import settings
from hypothesis.strategies import (
    booleans,
    complex_numbers,
    deferred,
    dictionaries,
    floats,
    frozensets,
    integers,
    lists,
    none,
    one_of,
    text,
    tuples,
)


max_dict_entries = maxsize if settings._current_profile == "ci" else 2**20

dict_keys = deferred(
    lambda: one_of(
        none(),
        booleans(),
        integers(),
        floats(allow_infinity=False, allow_nan=False),
        complex_numbers(allow_infinity=False, allow_nan=False),
        text(),
        tuples(dict_keys),
        frozensets(dict_keys),
    )
)

dict_values = deferred(lambda: one_of(dict_keys, lists(dict_keys), sample_dict))

sample_dict = dictionaries(dict_keys, dict_values, max_size=max_dict_entries)
