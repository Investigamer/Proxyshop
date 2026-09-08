from base64 import b64decode
from collections.abc import Callable
from logging import getLogger
from os import PathLike
from typing import Literal

from backoff import expo, on_exception
from limits import RateLimitItemPerHour
from limits.storage import MemoryStorage
from limits.strategies import MovingWindowRateLimiter
from omnitils.exceptions import return_on_exception
from omnitils.fetch.download import download_file
from omnitils.rate_limit import rate_limit
from pydantic import BaseModel, RootModel
from requests import RequestException, get

from src import DEFAULT_HEADERS
from src.utils.logging import log_on_exception

_logger = getLogger(__name__)

# Rate limiter to safely limit GitHub requests
_rate_limit_storage = MemoryStorage()
_rate_limiter = MovingWindowRateLimiter(_rate_limit_storage)
_rate_limit = RateLimitItemPerHour(60)

_headers = {**DEFAULT_HEADERS, "accept": "application/vnd.github+json"}

GITHUB_API_BASE_URL = "https://api.github.com/"
GITHUB_API_REPO_URL = GITHUB_API_BASE_URL + "repos/{repo}"
GITHUB_API_BRANCH_URL = GITHUB_API_BASE_URL + "repos/{repo}/branches/{branch}"
GITHUB_API_RELEASES_URL = (
    GITHUB_API_BASE_URL + "repos/{repo}/releases?per_page={per_page}&page={page}"
)
GITHUB_API_REPOSITORY_ARCHIVE_ZIP_URL = (
    GITHUB_API_BASE_URL + "repos/{repo}/zipball/{ref}"
)
GITHUB_API_REPOSITORY_CONTENT_URL = GITHUB_API_BASE_URL + "repos/{repo}/contents/{path}"

# These definitions are incomplete since we don't need most of the fields.


class GitHubRepo(BaseModel):
    default_branch: str


class GitHubCommit(BaseModel):
    sha: str


class GitHubBranch(BaseModel):
    commit: GitHubCommit


class GitHubReleaseAsset(BaseModel):
    id: int
    name: str
    content_type: str
    state: Literal["uploaded", "open"]
    size: int
    """Bytes"""
    created_at: str
    updated_at: str
    browser_download_url: str


class GitHubRelease(BaseModel):
    id: int
    tag_name: str
    name: str
    draft: bool
    prerelease: bool
    created_at: str
    updated_at: str
    published_at: str
    assets: list[GitHubReleaseAsset]


GitHubReleases = RootModel[list[GitHubRelease]]


class GitHubRepoContent(BaseModel):
    encoding: Literal["base64"]
    content: str


def github_request_wrapper[T, **P](func: Callable[P, T]) -> Callable[P, T]:
    @log_on_exception(logger=_logger)
    @rate_limit(limiter=_rate_limiter, limit=_rate_limit)
    @on_exception(expo, RequestException, logger=None, max_tries=1, max_time=1)
    def wrapper(*args: P.args, **kwargs: P.kwargs):
        return func(*args, **kwargs)

    return wrapper


@github_request_wrapper
def get_github_repo(repository: str) -> GitHubRepo:
    response = get(
        GITHUB_API_REPO_URL.format(repo=repository),
        headers=_headers,
        timeout=(10, 10),
    )
    if response.status_code == 200:
        return GitHubRepo.model_validate_json(response.content)
    raise RequestException(response=response)


@github_request_wrapper
def get_github_branch(repository: str, branch: str) -> GitHubBranch:
    response = get(
        GITHUB_API_BRANCH_URL.format(repo=repository, branch=branch),
        headers=_headers,
        timeout=(10, 10),
    )
    if response.status_code == 200:
        return GitHubBranch.model_validate_json(response.content)
    raise RequestException(response=response)


def get_latest_github_repo_commit_hash(
    repository: str, branch: str | None = None
) -> str:
    if not branch:
        branch = get_github_repo(repository).default_branch

    return get_github_branch(repository, branch).commit.sha


_default_releases: list[GitHubRelease] = []


@return_on_exception(_default_releases)
@github_request_wrapper
def get_github_releases(
    repository: str, per_page: int = 5, page: int = 1
) -> list[GitHubRelease]:
    response = get(
        GITHUB_API_RELEASES_URL.format(repo=repository, per_page=per_page, page=page),
        headers=_headers,
        timeout=(10, 10),
    )
    if response.status_code == 200:
        return GitHubReleases.model_validate_json(response.content).root
    raise RequestException(response=response)


@github_request_wrapper
def download_github_repository_archive_zip(
    repository: str, path: str | PathLike[str], ref: str = ""
) -> None:
    download_file(
        url=GITHUB_API_REPOSITORY_ARCHIVE_ZIP_URL.format(repo=repository, ref=ref),
        path=path,
        header=DEFAULT_HEADERS,
    )


@github_request_wrapper
def get_github_file_contents(repository: str, path: str) -> bytes:
    response = get(
        GITHUB_API_REPOSITORY_CONTENT_URL.format(repo=repository, path=path),
        headers=_headers,
        timeout=(10, 10),
    )
    if response.status_code == 200:
        data = GitHubRepoContent.model_validate_json(response.content)
        return b64decode(data.content)
    raise RequestException(response=response)
