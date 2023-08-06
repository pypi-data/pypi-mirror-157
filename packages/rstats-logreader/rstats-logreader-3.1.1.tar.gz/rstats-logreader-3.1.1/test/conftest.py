################################################################################
#                               rstats-logreader                               #
#   Parse RStats logfiles, display bandwidth usage, convert to other formats   #
#                    (C) 2016, 2019-2020, 2022 Jeremy Brown                    #
#                Released under Prosperity Public License 3.0.0                #
################################################################################

from hypothesis import HealthCheck, settings
from hypothesis.database import ExampleDatabase


settings.register_profile(
    "ci",
    database=ExampleDatabase(":memory:"),
    deadline=None,
    max_examples=200,
    stateful_step_count=200,
    suppress_health_check=[HealthCheck.too_slow],
)
