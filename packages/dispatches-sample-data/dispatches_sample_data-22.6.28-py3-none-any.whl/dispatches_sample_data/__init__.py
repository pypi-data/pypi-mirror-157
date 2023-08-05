try:
    # Python 3.8+
    from importlib import metadata
except ImportError:
    # Python 3.7
    import importlib_metadata as metadata


__version__ = metadata.version("dispatches-sample-data")
