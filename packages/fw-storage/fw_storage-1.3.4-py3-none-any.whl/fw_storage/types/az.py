"""Azure blob storage module."""
import functools
import io
import os
import re
import stat
import typing as t

from azure.core.exceptions import AzureError
from azure.identity import DefaultAzureCredential
from azure.storage.blob import ContainerClient, _blob_client
from azure.storage.blob._shared.policies import StorageRetryPolicy
from fw_utils import AnyFile, Filters, open_any
from pydantic import BaseSettings

from ..errors import FileNotFound, PermError, StorageError
from ..fileinfo import FileInfo
from ..filters import StorageFilter
from ..storage import AnyPath, CloudStorage

__all__ = ["AzureBlob"]


def translate_error(func):
    """Raise storage errors from Azure errors."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except AzureError as exc:
            if hasattr(exc, "status_code"):
                status_code = getattr(exc, "status_code")
                if status_code in (403, 404):
                    err_cls = FileNotFound if status_code == 404 else PermError
                    msg = f"{getattr(exc, 'reason')}"
                    raise err_cls(msg) from exc
            raise StorageError(exc.message) from exc

    return wrapper


class RetryConfig(BaseSettings):
    """Retry config."""

    class Config:
        """Enable envvars with prefix 'AZURE_RETRY_'."""

        # pylint: disable=too-few-public-methods
        env_prefix = "AZURE_RETRY_"

    backoff: t.Optional[float] = 0.5
    total: t.Optional[int] = 3


class AzureRetryPolicy(StorageRetryPolicy):
    """Custom Azure retry policy."""

    def __init__(self, config: RetryConfig):
        self.backoff_factor = config.backoff
        super().__init__(retry_total=config.total, retry_to_secondary=False)

    def get_backoff_time(self, settings):
        """Calculates how long to sleep before retrying."""
        return self.backoff_factor * (2 ** settings["count"] - 1)


def create_default_client(
    account_url: str,
    container: str,
    access_key: t.Optional[str],
    **kwargs: t.Any,
) -> ContainerClient:
    """Create Azure Blob Storage ContainerClient.

    See how azure-identity determines credentials:
    https://docs.microsoft.com/en-us/python/api/azure-identity/azure.identity.defaultazurecredential
    """
    config = RetryConfig()
    access_key = access_key or os.getenv("AZ_ACCESS_KEY")
    if access_key:
        return ContainerClient(
            account_url,
            container,
            credential=str(access_key),
            retry_policy=AzureRetryPolicy(config),
        )
    if kwargs:
        sas_params = "&".join(
            [
                f"{param}={kwargs.pop(param)}"
                for param in SAS_QUERY_PARAMS
                if param in kwargs
            ]
        )
        if sas_params:
            sas_url = f"https://{account_url}/{container}?{sas_params}"
            return ContainerClient.from_container_url(
                sas_url, retry_policy=AzureRetryPolicy(config)
            )
    return ContainerClient(
        account_url,
        container,
        credential=DefaultAzureCredential(),
        retry_policy=AzureRetryPolicy(config),
    )


class AzureBlob(CloudStorage):
    """Storage class for Azure blob storage."""

    # NOTE Azure only supports up to 256 subrequests in a single batch
    delete_batch_size: t.ClassVar[int] = 256

    url_re = re.compile(
        r"az://"
        r"(?P<account>[^/]+)"
        r"(/(?P<container>[^:/?#]+))"
        r"(/(?P<prefix>[^?#]+))?"
        r"(\?(?P<query>[^#]+))?"
    )

    def __init__(
        # pylint: disable=too-many-arguments
        self,
        account: str,
        container: str,
        prefix: t.Optional[str] = "",
        access_key: t.Optional[str] = None,
        create_client: t.Optional[t.Callable] = create_default_client,
        **kwargs: t.Any,
    ) -> None:
        """Construct Azure storage."""
        if not create_client:
            raise StorageError("create_client function required")
        self.client = create_client(
            account,
            container,
            access_key,
            **kwargs,
        )
        if not isinstance(self.client, ContainerClient):
            raise StorageError(
                "Azure storage implementation can only use ContainerClient"
                f" and not {type(self.client).__name__}"
            )
        self.prefix = prefix
        self.container = container
        super().__init__(**kwargs)

    def abspath(self, path: AnyPath) -> str:
        """Return absolute path for a given path."""
        return f"{self.prefix}/{self.relpath(path)}".lstrip("/")

    @translate_error
    def check_access(self):
        """Check container is accessible."""
        self.client.get_container_properties()

    @translate_error
    def ls(
        self, path: str = "", *, include: Filters = None, exclude: Filters = None, **_
    ) -> t.Iterator[FileInfo]:
        """Yield each item under prefix matching the include/exclude filters."""
        path = self.abspath(path)
        filt = StorageFilter(include=include, exclude=exclude)
        for meta in self.client.list_blobs(name_starts_with=path):
            relpath = re.sub(rf"^{self.prefix}", "", meta.name).lstrip("/")
            info = FileInfo(
                path=relpath,
                size=meta.size,
                created=meta.creation_time.timestamp(),
                modified=meta.last_modified.timestamp(),
            )
            if filt.match(info):
                yield info

    @translate_error
    def stat(self, path: str) -> FileInfo:
        """Return FileInfo for a single file."""
        abspath = self.abspath(path)
        blob_client = self.client.get_blob_client(abspath)
        meta = blob_client.get_blob_properties()
        return FileInfo(
            path=path,
            size=meta.size,
            created=meta.creation_time.timestamp(),
            modified=meta.last_modified.timestamp(),
        )

    @translate_error
    def download_file(self, path: str, dst: t.IO[bytes]) -> None:
        """Download file and it is opened for reading in binary mode."""
        blob_stream = self.client.download_blob(path)
        blob_stream.readinto(dst)

    @translate_error
    def upload_file(self, path: str, file: AnyFile) -> None:
        """Write source file to the given path."""
        # upload_blob uses automatic chunking stated by Azure documentation
        with open_any(file, mode="rb") as r_file:
            self.client.upload_blob(name=path, data=r_file, overwrite=True)

    @translate_error
    def flush_delete(self) -> None:
        """Remove a file at the given path."""
        self.client.delete_blobs(*self.delete_keys, delete_snapshots="include")
        self.delete_keys.clear()

    def __repr__(self) -> str:
        """Return string representation of the storage."""
        return f"{type(self).__name__}('{self.container}/{self.prefix}')"


# patch Azure SDK's get_length to support streaming from requests (sockets)
# see: https://flywheelio.atlassian.net/browse/FLYW-11776

orig_get_length = _blob_client.get_length


def get_length_patch(data) -> t.Optional[int]:
    """Return None instead of 0 if data is a socket."""
    try:
        fileno = data.fileno()
        fstat = os.fstat(fileno)
        if stat.S_ISSOCK(fstat.st_mode):
            return None
    except (AttributeError, io.UnsupportedOperation, OSError):
        pass
    return orig_get_length(data)


_blob_client.get_length = get_length_patch


SAS_QUERY_PARAMS: set = {
    "sp",
    "st",
    "se",
    "skoid",
    "sktid",
    "skt",
    "ske",
    "sks",
    "skv",
    "saoid",
    "suoid",
    "scid",
    "sip",
    "spr",
    "sv",
    "sr",
    "rscc",
    "rscd",
    "rsce",
    "rscl",
    "rsct",
    "sig",
}
