"""Implementations of storage catalogs."""


from __future__ import annotations


def __resolve_cms_path(file_path: str, storage_catalog: str) -> str:
    """Resolve the CMS path of a file."""
    raise NotImplementedError()


def resolve_file_path(file_path: str, storage_catalog: str) -> str:
    """Resolve the file path given a file catalog."""
    if not storage_catalog:
        return file_path

    return file_path
