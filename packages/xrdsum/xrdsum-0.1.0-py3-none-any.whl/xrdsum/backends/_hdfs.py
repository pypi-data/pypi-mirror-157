"""Implementation of the HDFS backend."""
# we want non-top-level imports to avoid pulling HDFS dependency early
# pylint: disable=import-outside-toplevel
from __future__ import annotations

import xml.etree.ElementTree as ET
from contextlib import closing
from dataclasses import dataclass
from typing import IO, Any, Generator

from ..checksums import Checksum
from ..logger import logger as log
from ._base import XrdsumBackend

CONF = "/etc/hadoop/conf/hdfs-site.xml"
USER = "xrootd"


@dataclass
class HDFSSettings:
    """Settings for the HDFS backend."""

    config_file: str = CONF
    user: str = USER
    read_size: int = 64 * 1024 * 1024


def __get_namenodes() -> list[str]:
    """
    Get the list of namenodes from the HDFS configuration file.
    """

    tree = ET.parse(CONF)
    root = tree.getroot()
    namenodes = []

    for prop in root.findall("property"):
        name = prop.find("name")
        if name is None:
            continue
        name_str = str(name.text)

        if name_str.startswith("dfs.namenode.http-address"):
            value = prop.find("value")
            if value is None:
                continue
            namenodes.append(str(value.text))
    return namenodes


def get_hdfs_client() -> Any:
    """Retrieving the HDFS client to execute operations on HDFS."""
    import pyhdfs

    namenodes = __get_namenodes()
    log.debug("Connecting to HDFS via %s", namenodes)
    client = pyhdfs.HdfsClient(namenodes, user_name=USER)  # can throw AssertionError
    return client


def read_file_in_chunks(
    file_path: str, chunk_size_in_bytes: int
) -> Generator[IO[bytes], None, None]:
    """Reads HDFS file in chunks."""
    client = get_hdfs_client()
    file_status = client.get_file_status(file_path)
    total_size = file_status.length
    read_bytes = 0
    log.debug(
        "Reading %s in chunks of %s bytes (out of %s)",
        file_path,
        chunk_size_in_bytes,
        total_size,
    )
    with closing(client.open(file_path)) as file_handle:
        while True:
            chunk = file_handle.read(chunk_size_in_bytes)
            if chunk:
                read_bytes += len(chunk)
                yield chunk
            else:
                return


class HDFSBackend(XrdsumBackend):
    """Implementation of the HDFS backend."""

    client: Any
    settings: HDFSSettings

    def __init__(self, file_path: str, read_size: int, **kwargs: dict[str, Any]):
        """HDFS backend requires at least the file_path and read_size"""
        self.client = get_hdfs_client()
        self.file_path = file_path
        self.settings = HDFSSettings(
            read_size=read_size,
            **kwargs,  # type: ignore[arg-type]
        )

    def _get_xattr(self, xattr_name: str) -> str:
        import pyhdfs

        try:
            xattr_value = self.client.get_xattrs(
                self.file_path, xattr_name=xattr_name, encoding="text"
            )
        except pyhdfs.HdfsIOException as error:
            # this is OK, just means the xattr does not exist
            log.debug(
                "No checksum found in metadata (%s) for file %s: %s",
                xattr_name,
                self.file_path,
                error,
            )
            return ""
        if xattr_value:
            return str(xattr_value[xattr_name])

        return ""

    def get_checksum(self, checksum: Checksum) -> Checksum:
        # check if file exists
        exists = self.client.exists(self.file_path)
        if not exists:
            log.error("File %s does not exist", self.file_path)
            return checksum
        # try to get from metadata
        xattr_name = f"user.Xrdsum.{checksum.name}"
        xattr_value = self._get_xattr(xattr_name)
        if xattr_value:
            checksum.value = xattr_value
            return checksum
        # did not find it in metadata, try to calculate it
        checksum.value = checksum.calculate(
            read_file_in_chunks(self.file_path, self.settings.read_size)
        )

        return checksum

    def store_checksum(self, checksum: Checksum, force: bool = False) -> None:
        if not checksum.value:
            checksum = self.get_checksum(checksum)

        xattr_name = f"Xrdsum.{checksum.name}"
        xattr_value = self._get_xattr(xattr_name)
        xattr_flag = "CREATE"
        if xattr_value is not None and not force:
            log.error(
                "Checksum already exists in metadata (%s) for file %s",
                xattr_name,
                self.file_path,
            )
            raise ValueError(
                f"Xattr {xattr_name} already exists for file {self.file_path}"
            )
        if xattr_value is not None and force:
            xattr_flag = "REPLACE"
        self.client.set_xattr(
            self.file_path,
            xattr_name,
            checksum.value,
            encoding="text",
            flag=xattr_flag,
        )
