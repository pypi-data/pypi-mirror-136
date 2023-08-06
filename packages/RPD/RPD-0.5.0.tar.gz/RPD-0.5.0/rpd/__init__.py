"""
RPD
~~~
Asynchronous Discord API Wrapper For Python

:copyright: 2021-present VincentRPS
:license: MIT
"""

__title__: str = "RPD"
__author__: str = "VincentRPS"
__license__: str = "MIT"
__copyright__: str = "Copyright 2021-present VincentRPS"
__version__: str = "0.5.0"

import logging
import typing

# there are a lot of
# problems with importing rpd.apps for some reason.
from rpd.api import *
from rpd.apps import *
from rpd.audio import *
from rpd.color import *
from rpd.colour import *
from rpd.events import *
from rpd.intents import *
from rpd.interactions import *
from rpd.internal.exceptions import *
from rpd.internal.warnings import *
from rpd.message import *
from rpd.modules import *
from rpd.snowflake import *
from rpd.traits import *
from rpd.ui import *
from rpd.util import *
from rpd.webhooks import *
from rpd.state import *


class VersionInfo(typing.NamedTuple):
    major: str
    minor: str
    micro: str
    releaselevel: typing.Literal["alpha", "beta", "candidate", "final"]
    serial: int


version_info: VersionInfo = VersionInfo(
    major=0, minor=5, micro=0, releaselevel="final", serial=0
)

logging.getLogger(__name__).addHandler(logging.NullHandler())

__all__: typing.List[str] = [
    "__title__",
    "__author__",
    "__license__",
    "__copyright__",
    "__version__",
    "VersionInfo",
    "version_info",
]
