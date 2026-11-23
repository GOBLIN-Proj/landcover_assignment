"""
Deprecated names
================
Helpers that keep misspelt public names working for one release, with a DeprecationWarning. Each use is marked
``DEPRECATED_NAME`` so that the spelling test (``tests/test_spelling.py``) skips it.
"""
import functools
import warnings


def warn_renamed(old, new):
    """Issue a DeprecationWarning for a renamed public name."""
    warnings.warn(f"'{old}' is deprecated and will be removed in a future release; use '{new}'.",
                  DeprecationWarning, stacklevel=3)


def renamed_method(new_name, old_name):
    """A method alias that warns, then calls the method called ``new_name``."""
    def alias(self, *args, **kwargs):
        warn_renamed(old_name, new_name)
        return getattr(self, new_name)(*args, **kwargs)
    alias.__name__ = old_name
    alias.__doc__ = f"Deprecated: use :meth:`{new_name}`."
    return alias


def renamed_attribute(new_name, old_name):
    """A read-only property alias that warns, then returns the attribute called ``new_name``."""
    def getter(self):
        warn_renamed(old_name, new_name)
        return getattr(self, new_name)
    return property(getter, doc=f"Deprecated: use ``{new_name}``.")


def renamed_keyword(old_name, new_name):
    """Decorator: accept the old keyword argument ``old_name`` as ``new_name``, with a warning."""
    def decorate(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if old_name in kwargs:
                warn_renamed(old_name, new_name)
                kwargs[new_name] = kwargs.pop(old_name)
            return func(*args, **kwargs)
        return wrapper
    return decorate
