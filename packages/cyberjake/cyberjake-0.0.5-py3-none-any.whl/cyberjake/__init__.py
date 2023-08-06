"""Common code"""
from .check_update import check_update
from .database import build_database_url
from .discord_common import error_embed
from .discord_common import make_embed
from .make_logger import make_logger
from .file_utils import remove_bom_inplace

__version__ = "0.0.5"

__all__ = [
    "__version__",
    "make_logger",
    "make_embed",
    "error_embed",
    "build_database_url",
    "check_update",
    "remove_bom_inplace",
]
