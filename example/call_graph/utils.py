"""Utilities"""

import os
import sys
from functools import wraps


def suppressConsoleOut(meth):
    """Disable console output during the method is run."""
    @wraps(meth)
    def decorate(*args, **kwargs):
        """Decorate"""
        # Disable ansible console output
        _stdout = sys.stdout
        fptr = open(os.devnull, 'w')
        sys.stdout = fptr
        try:
            return meth(*args, **kwargs)
        except Exception as e:
            raise e
        finally:
            # Enable console output
            sys.stdout = _stdout
    return decorate
