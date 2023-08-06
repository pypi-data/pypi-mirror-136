"""Tools to help with debugging your Python code."""

__program__: str = "dbugging"
__author__: str = "Niklas Larsson"
__copyright__: str = ""
__credits__: list = ["Niklas Larsson"]
__license__: str = ""
__version__: str = "0.0.1a3"
__maintainer__: str = "Niklas Larsson"
__email__: str = ""
__status__: str = "Alpha"

from dbugging.decorators import debug
from dbugging.decorators import verbose
from dbugging.decorators import slow_down
