from .base import *

try:
    from .dev_secrets import *
except ImportError as e:
    pass

DEBUG = True
