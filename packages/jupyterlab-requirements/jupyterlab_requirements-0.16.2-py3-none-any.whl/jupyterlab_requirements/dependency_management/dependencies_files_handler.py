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

"""Requirements API for jupyterlab requirements."""

import json
import os
import logging
import subprocess

from pathlib import Path

from jupyter_server.base.handlers import APIHandler
from tornado import web

from thoth.python import Project

_LOGGER = logging.getLogger("jupyterlab_requirements.dependencies_files_handler")


class DependenciesFilesHandler(APIHandler):
    """Dependencies files handler to store dependencies files."""

    @web.authenticated
    def post(self):  # type: ignore
        """Store requirements file to disk."""
        initial_path = Path.cwd()
        input_data = self.get_json_body()  # type: ignore

        # Path of the repo where we need to store
        path_to_store: str = input_data["path_to_store"]

        kernel_name: str = input_data["kernel_name"]
        requirements: str = input_data["requirements"]
        requirements_lock: str = input_data["requirements_lock"]
        complete_path: str = input_data["complete_path"]

        env_path = Path(complete_path).joinpath(path_to_store).joinpath(kernel_name)

        _LOGGER.info("Path used to store dependencies is: %r", env_path.as_posix())

        # Delete and recreate folder
        if env_path.exists():
            _ = subprocess.call(f"rm -rf ./{kernel_name} ", shell=True, cwd=Path(complete_path).joinpath(path_to_store))

        env_path.mkdir(parents=True, exist_ok=True)

        os.chdir(env_path)

        requirements_format = "pipenv"

        project = Project.from_strings(requirements, requirements_lock)

        pipfile_path = env_path.joinpath("Pipfile")
        pipfile_lock_path = env_path.joinpath("Pipfile.lock")

        if requirements_format == "pipenv":
            _LOGGER.debug("Writing to Pipfile/Pipfile.lock in %r", env_path)
            project.to_files(pipfile_path=pipfile_path, pipfile_lock_path=pipfile_lock_path)

        os.chdir(initial_path)
        self.finish(json.dumps({"message": f"Successfully stored requirements at {env_path}!"}))  # type: ignore


class DependenciesNotebookNameHandler(APIHandler):
    """Notebook name handler for notebook file name."""

    @web.authenticated
    def post(self):  # type: ignore
        """Store current notebook name handled."""
        input_data = self.get_json_body()  # type: ignore

        notebook_path: str = input_data["notebook_path"]
        notebook_name: str = Path(notebook_path).name

        home = Path.home()
        store_path: Path = home.joinpath(".local/share/thoth/kernels")
        _LOGGER.debug("Path used to store notebook handled is: %r", store_path.as_posix())

        file_name = "thoth_notebook_tracker.json"

        file_path = store_path.joinpath(file_name)

        # Delete and recreate file in case
        if file_path.exists():
            _ = subprocess.call(f"rm -rf {file_name}", shell=True, cwd=store_path)

        data = {"notebook_name": notebook_name}

        store_path.mkdir(parents=True, exist_ok=True)

        with open(file_path, "w") as outfile:
            json.dump(data, outfile)

        self.finish({"message": f"Successfully stored notebook tracker at {file_path}!"})  # type: ignore
