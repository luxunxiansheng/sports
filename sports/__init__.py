import importlib.metadata as importlib_metadata

try:
    # This will read version from pyproject.toml
    __version__ = importlib_metadata.version(__package__ or __name__)
except importlib_metadata.PackageNotFoundError:
    __version__ = "development"


from sports.common.core import MeasurementUnit
from sports.configs.basketball import BasketballCourtConfiguration
from sports.annotators.basketball import draw_court, draw_made_and_miss_on_court
from sports.tools.basketball import ShotType, ShotEvent, ShotEventTracker

__all__ = [
    "MeasurementUnit",
    "BasketballCourtConfiguration",
    "draw_court",
    "draw_made_and_miss_on_court",
    "ShotType",
    "ShotEvent",
    "ShotEventTracker"
]