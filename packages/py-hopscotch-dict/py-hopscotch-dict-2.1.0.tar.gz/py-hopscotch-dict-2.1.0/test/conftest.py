################################################################################
#                              py-hopscotch-dict                               #
#    Full-featured `dict` replacement with guaranteed constant-time lookups    #
#                    (C) 2017, 2019-2020, 2022 Jeremy Brown                    #
#                Released under Prosperity Public License 3.0.0                #
################################################################################

from hypothesis import HealthCheck, settings
from hypothesis.database import ExampleDatabase


settings.register_profile(
    "ci",
    database=ExampleDatabase(":memory:"),
    deadline=None,
    max_examples=500,
    stateful_step_count=200,
    suppress_health_check=[HealthCheck.too_slow],
)
