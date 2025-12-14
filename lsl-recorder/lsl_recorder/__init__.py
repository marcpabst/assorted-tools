# import the contents of the Rust library into the Python extension
from .lsl_recorder import *
from .lsl_recorder import __all__

# optional: include the documentation from the Rust module
from .lsl_recorder import __doc__  # noqa: F401

# set gstreamer plugin environment variable to site-packages/psydk/.dylibs/
import platform
