"""Temporary fix for https://github.com/iterative/dvc/issues/5618."""

from PyInstaller.utils.hooks import (
    collect_data_files
)

datas = collect_data_files("googleapiclient.discovery_cache")
