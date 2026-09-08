from logging import getLogger
from subprocess import DEVNULL, CalledProcessError, check_output, run

_logger = getLogger(__name__)


def is_git_available() -> bool:
    try:
        run(("git", "--version"), stdout=DEVNULL, check=True)
        return True
    except CalledProcessError:
        return False


def get_latest_remote_git_commit_hash(repo_url: str) -> str | None:
    try:
        output = check_output(
            ["git", "ls-remote", repo_url, "HEAD"],
        )
        if output:
            return output.decode().split()[0]
    except CalledProcessError as exc:
        _logger.exception(
            f"Failed to get latest remote Git commit hash from {repo_url}", exc_info=exc
        )
    return None
