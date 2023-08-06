"""Persistent cache."""

import contextlib
import os
import shutil
import typing as t

import appdirs
import diskcache

from project_config.compat import cached_function, importlib_metadata


@cached_function
def _directory() -> str:
    project_config_metadata = importlib_metadata.metadata("project_config")
    return appdirs.user_data_dir(  # type: ignore
        appname=project_config_metadata["name"],
        appauthor=project_config_metadata["author"],
        version=project_config_metadata["version"],
    )


class Cache:
    """Wrapper for a unique :py:class:`diskcache.Cache` instance."""

    class Keys:  # noqa: D106
        expiration = "_project_config_cache_expiration"

    @staticmethod
    @cached_function
    def _get_cache() -> diskcache.Cache:
        return diskcache.Cache(_directory())

    @classmethod
    def set(cls, *args: t.Any, **kwargs: t.Any) -> t.Any:  # noqa: A003, D102
        kwargs["expire"] = cls.get(cls.Keys.expiration)
        return cls._get_cache().set(*args, **kwargs)

    @classmethod
    def get(cls, *args: t.Any, **kwargs: t.Any) -> t.Any:  # noqa: D102
        if os.environ.get("PROJECT_CONFIG_USE_CACHE") == "false":
            return None
        return cls._get_cache().get(*args, **kwargs)  # pragma: no cover

    @staticmethod
    def clean() -> bool:
        """Remove the cache directory."""
        with contextlib.suppress(FileNotFoundError):
            shutil.rmtree(_directory())
        return True

    @staticmethod
    def get_directory() -> str:
        """Return the cache directory."""
        return _directory()
