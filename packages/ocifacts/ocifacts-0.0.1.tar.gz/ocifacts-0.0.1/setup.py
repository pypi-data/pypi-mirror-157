from setuptools import find_packages
from setuptools import setup

import os
import stat
import platform
import sys
import urllib.request


REPO = "vmware-tanzu/carvel-imgpkg"
VERSION = "v0.29.0"
BIN_PATH = "./ocifacts/bin"


def download():
    """Download imgpkg"""

    build = platform.platform()
    os_name = sys.platform
    print(f"downloading imgpkg for '{os_name}' '{build}'")

    asset_url = ""

    if os_name == "darwin":
        if "x86_64" in build:
            asset_url = f"https://github.com/{REPO}/releases/download/{VERSION}/imgpkg-darwin-amd64"
        if "arm64" in build:
            asset_url = f"https://github.com/{REPO}/releases/download/{VERSION}/imgpkg-darwin-arm64"
    elif os_name == "linux":
        if "x86_64" in build:
            asset_url = f"https://github.com/{REPO}/releases/download/{VERSION}/imgpkg-linux-amd64"
        if "arm64" in build:
            asset_url = f"https://github.com/{REPO}/releases/download/{VERSION}/imgpkg-linux-arm64"
    else:
        raise ValueError(f"os name not supported '{os_name}'")

    # download the url contents in binary format
    headers = {"Accept": "application/octet-stream"}
    req = urllib.request.Request(asset_url, headers=headers)
    r = urllib.request.urlopen(req)

    if not os.path.exists(BIN_PATH):
        os.mkdir(BIN_PATH)

    file_path = os.path.join(BIN_PATH, "imgpkg")
    with open(file_path, "wb") as code:
        code.write(r.read())

    st = os.stat(file_path)
    os.chmod(file_path, st.st_mode | stat.S_IEXEC)


download()

setup(
    name="ocifacts",
    version="0.0.1",
    url="https://github.com/old-ocean-creature/ocifacts",
    project_urls={
        "Documentation": "https://github.com/old-ocean-creature/ocifacts",
        "Code": "https://github.com/old-ocean-creature/ocifacts",
        "Issue tracker": "https://github.com/old-ocean-creature/ocifacts/issues",
    },
    maintainer="Sole Ahab",
    description="Artifact storage using OCI registries",
    python_requires=">=3.6",
    packages=find_packages(include=("ocifacts", "ocifacts.*")),
    package_data={"ocifacts": ["bin/*"]},
)
