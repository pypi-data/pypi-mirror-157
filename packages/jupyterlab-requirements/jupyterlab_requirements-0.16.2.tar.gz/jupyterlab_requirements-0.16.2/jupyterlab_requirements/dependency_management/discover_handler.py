# jupyterlab-requirements
# Copyright(C) 2020, 2021 Francesco Murdaca
#
# This program is free software: you can redistribute it and / or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""Dependency management API for jupyterlab requirements."""

import json
import subprocess
import logging

from pathlib import Path

from thamos.discover import discover_python_version

from jupyter_server.base.handlers import APIHandler
from tornado import web

from .lib import get_packages

_LOGGER = logging.getLogger("jupyterlab_requirements.discover_handler")


class DependencyInstalledHandler(APIHandler):
    """Dependency management handler to discover dependencies installed."""

    @web.authenticated
    def post(self):  # type: ignore
        """Discover list of packages installed."""
        input_data = self.get_json_body()  # type: ignore

        kernel_name: str = input_data["kernel_name"]

        packages = get_packages(kernel_name=kernel_name)

        self.finish(json.dumps(packages))  # type: ignore


class PythonVersionHandler(APIHandler):
    """Dependency management handler to discover Python version present."""

    @web.authenticated
    def get(self):  # type: ignore
        """Discover python version available."""
        python_version = discover_python_version()

        self.finish(json.dumps(python_version))  # type: ignore


class RootPathHandler(APIHandler):
    """Discover root for the project."""

    @web.authenticated
    def get(self):  # type: ignore
        """Discover root directory of the project."""
        try:
            process_output = subprocess.run("git rev-parse --show-toplevel", capture_output=True, shell=True)
            git_root = process_output.stdout.decode("utf-8").strip()
            complete_path = Path(git_root)
            _LOGGER.info("complete path used is: %r", complete_path.as_posix())

        except Exception as not_git_exc:
            _LOGGER.error(
                "Using home path because there was an error to identify root of git repository: %r", not_git_exc
            )
            complete_path = Path.home()

        self.finish(json.dumps(complete_path.as_posix()))  # type: ignore
