"""ocifacts provides a simple means of storing artifacts in OCI registries"""

import os
import subprocess
from typing import List


imgpkg_relpath = os.path.dirname(__file__)
imgpkg_abspath = os.path.abspath(imgpkg_relpath)
BIN_PATHNAME = os.path.join(imgpkg_abspath, "bin/imgpkg")


def push(repo: str, tag: str, files: str | List[str]) -> None:
    """Push files to registry"""

    args = [
        BIN_PATHNAME,
        "push",
        "-i",
        f"{repo}:{tag}",
    ]
    fps = []
    if isinstance(files, str):
        fps = [files]
    else:
        fps = files

    for f in fps:
        args.append("-f")
        args.append(f)

    try:
        subprocess.run(
            args=args,
            capture_output=True,
            check=True,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        print(e.output)
        raise e


def pull(repo: str, tag: str, out: str) -> None:
    """Pull files from registry"""

    args = [
        BIN_PATHNAME,
        "pull",
        "-i",
        f"{repo}:{tag}",
        "-o",
        out,
    ]

    try:
        subprocess.run(
            args=args,
            capture_output=True,
            check=True,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        print(e.output)
        raise e
