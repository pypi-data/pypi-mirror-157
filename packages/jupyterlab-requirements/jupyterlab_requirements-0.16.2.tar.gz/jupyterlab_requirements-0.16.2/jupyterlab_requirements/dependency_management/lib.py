# jupyterlab-requirements
# Copyright(C) 2021 Francesco Murdaca
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

"""Library with core methods for jupyterlab-requirements."""

import os
import ast
import subprocess
import logging
import shutil
import typing
import tempfile
import json
import sys
import yaml  # type: ignore
import invectio
import distutils.sysconfig as sysconfig

from subprocess import CompletedProcess
from virtualenv import cli_run
from pathlib import Path

from rich.text import Text
from rich import box
from rich.console import Console
from rich.table import Table

from thoth.python import Project, Pipfile, PipfileLock
from thoth.python import PipfileMeta
from thoth.python import Source, PackageVersion
from thoth.common import ThothAdviserIntegrationEnum

from thamos.lib import advise_using_config, _get_origin
from thamos.lib import get_package_from_imported_packages
from thamos.lib import get_log
from thamos.config import _Configuration
from thamos.discover import discover_python_version

_LOGGER = logging.getLogger("jupyterlab_requirements.lib")


_EMOJI = {
    "WARNING": Text("\u26a0\ufe0f WARNING", style="yellow"),
    "ERROR": Text("\u274c ERROR", style="bold red"),
    "INFO": Text("\u2714\ufe0f INFO", "green"),
}


def print_report(report: typing.List[typing.Dict[str, typing.Any]], title: str = "") -> None:
    """Print reasoning to user."""
    console = Console()
    table = Table(
        show_header=True,
        header_style="bold green",
        title=title,
        box=box.MINIMAL_DOUBLE_HEAD,
    )

    header = set()  # type: typing.Set[str]
    to_remove = set()  # type: typing.Set[str]
    for item in report:
        header = header.union(set(item.keys()))
        to_remove = to_remove.union(set(i for i, v in item.items() if isinstance(v, dict)))

    # Remove fields that can be an array - these are addition details that are supressed from the table output.
    header = header - to_remove

    header_list = sorted(header)
    for item_ in header_list:
        table.add_column(item_.replace("_", " ").capitalize(), style="cyan", overflow="fold")

    for item in report:
        row = []
        for column in header_list:
            entry = item.get(column, "-")

            if not bool(int(os.getenv("JUPYTERLAB_REQUIREMENTS_NO_EMOJI", 0))) and isinstance(entry, str):
                entry = _EMOJI.get(entry, entry)

            if isinstance(entry, list):
                entry = ", ".join(entry)

            if isinstance(entry, str) and entry.startswith(("https://", "http://")):
                entry = f"[link {entry}]{entry}"

            row.append(entry)

        table.add_row(*row)

    console.print(table, justify="center")


def get_notebook_content(notebook_path: str, py_format: bool = False) -> typing.Any:
    """Get JSON of the notebook content."""
    actual_path = Path(notebook_path)

    if not actual_path.exists():
        raise FileNotFoundError(f"There is no file at this path: {actual_path.as_posix()!r}")

    if actual_path.suffix != ".ipynb":
        raise Exception("File submitted is not .ipynb")

    if not py_format:
        with open(notebook_path) as notebook_content:
            notebook = json.load(notebook_content)

        return notebook

    else:
        check_convert = subprocess.run(
            f"jupyter nbconvert --to python {actual_path} --stdout", shell=True, capture_output=True
        )

        if check_convert.returncode != 0:
            raise Exception(f"jupyter nbconvert failed converting notebook to .py: {check_convert.stderr!r}")

        notebook_content_py = check_convert.stdout.decode("utf-8")

        return notebook_content_py


def horus_check_metadata_content(
    notebook_metadata: typing.Dict[str, typing.Any], is_cli: bool = True
) -> typing.List[typing.Dict[str, typing.Any]]:
    """Check the metadata of notebook for dependencies."""
    result = []

    if notebook_metadata.get("language_info"):
        language = notebook_metadata["language_info"]["name"]

        if language:
            if language != "python":
                result.append(
                    {
                        "key": "programming_language",
                        "message": "Only python is supported.",
                        "type": "ERROR",
                    }
                )
                return result

            else:
                result.append(
                    {
                        "key": "programming_language",
                        "message": f"{language}",
                        "type": "INFO",
                    }
                )

    kernelspec = notebook_metadata.get("kernelspec")

    if kernelspec:
        kernel_name = kernelspec["name"]
    else:
        # kernelspec is not available only when a new notebook is started and not saved.
        kernel_name = "ipykernel"

    result.append(
        {
            "key": "kernel_name",
            "message": kernel_name,
            "type": "INFO",
        }
    )

    if "dependency_resolution_engine" not in notebook_metadata.keys():
        if is_cli:
            command = "horus lock [NOTEBOOK].ipynb"
        else:
            command = "%horus lock"

        result.append(
            {
                "key": "dependency_resolution_engine",
                "message": "key is not present in notebook metadata. "
                f"It will be set after creating Pipfile and running {command}",
                "type": "WARNING",
            }
        )
    else:
        result.append(
            {
                "key": "dependency_resolution_engine",
                "message": f"{notebook_metadata['dependency_resolution_engine']}",
                "type": "INFO",
            }
        )

    resolution_engine = notebook_metadata.get("dependency_resolution_engine")

    if resolution_engine == "thoth":
        for thoth_specific_key in ["thoth_config", "thoth_analysis_id"]:
            if thoth_specific_key not in notebook_metadata.keys():

                if is_cli:
                    command = "horus lock [NOTEBOOK].ipynb"
                else:
                    command = "%horus lock"

                result.append(
                    {
                        "key": thoth_specific_key,
                        "message": "key is not present in notebook metadata. " f"You can run {command}.",
                        "type": "ERROR",
                    }
                )
            else:
                if thoth_specific_key == "thoth_analysis_id":
                    thoth_analysis_id = notebook_metadata.get("thoth_analysis_id")
                    result.append(
                        {
                            "key": thoth_specific_key,
                            "message": f"{thoth_analysis_id}",
                            "type": "INFO",
                        }
                    )
                else:
                    result.append(
                        {
                            "key": thoth_specific_key,
                            "message": "key is present in notebook metadata.",
                            "type": "INFO",
                        }
                    )

    for mandatory_key in ["requirements"]:
        if mandatory_key not in notebook_metadata.keys():

            if is_cli:
                command = "horus requirements [NOTEBOOK].ipynb"
            else:
                command = "%horus requirements"

            result.append(
                {
                    "key": mandatory_key,
                    "message": "key is not present in notebook metadata. "
                    f"You can run {command} with its options to set them.",
                    "type": "ERROR",
                }
            )
        else:
            result.append(
                {
                    "key": mandatory_key,
                    "message": "key is present in notebook metadata.",
                    "type": "INFO",
                }
            )

    for mandatory_key in ["requirements_lock"]:
        if mandatory_key not in notebook_metadata.keys():
            if is_cli:
                command = "horus lock [NOTEBOOK].ipynb"
            else:
                command = "%horus lock"

            result.append(
                {
                    "key": mandatory_key,
                    "message": f"key is not present in notebook metadata. "
                    f"You can run {command} if Pipfile already exists.",
                    "type": "ERROR",
                }
            )

        else:
            result.append(
                {
                    "key": mandatory_key,
                    "message": "key is present in notebook metadata.",
                    "type": "INFO",
                }
            )

    if "requirements" in notebook_metadata and "requirements_lock" in notebook_metadata:
        project = Project.from_strings(
            pipfile_str=notebook_metadata["requirements"], pipfile_lock_str=notebook_metadata["requirements_lock"]
        )

        if project.pipfile_lock.meta.hash["sha256"] != project.pipfile.hash()["sha256"]:
            if is_cli:
                command = "horus lock [NOTEBOOK].ipynb"
            else:
                command = "%horus lock"

            result.append(
                {
                    "key": "requirements_hash_match",
                    "message": f"Pipfile hash stated in Pipfile.lock {project.pipfile_lock.meta.hash['sha256'][:6]} "
                    f"does not correspond to Pipfile hash {project.pipfile.hash()['sha256'][:6]} - was Pipfile "
                    f"adjusted? Then you should run {command}.",
                    "type": "ERROR",
                }
            )
        else:
            result.append(
                {
                    "key": "requirements_hash_match",
                    "message": f"Pipfile hash stated in Pipfile.lock {project.pipfile_lock.meta.hash['sha256'][:6]} "
                    f"correspond to Pipfile hash {project.pipfile.hash()['sha256'][:6]}.",
                    "type": "INFO",
                }
            )

        kernel_packages = get_packages(kernel_name=kernel_name)
        notebook_packages = project.pipfile_lock.packages

        check = 0
        if kernel_packages:
            for package in notebook_packages:
                if str(package.name) in kernel_packages:
                    if str(package.version).strip("==") in kernel_packages[str(package.name)]:
                        check += 1
                else:
                    break

        if check == len([p.name for p in notebook_packages]):
            result.append(
                {
                    "key": "kernel_check",
                    "message": f"kernel {kernel_name} matches packages (name,version,PyPI index) "
                    "from requirements lock in your notebook metadata.",
                    "type": "WARNING",
                }
            )
        else:
            if is_cli:
                command = "horus set-kernel [NOTEBOOK].ipynb"
            else:
                command = "%horus set-kernel"

            result.append(
                {
                    "key": "kernel_check",
                    "message": f"kernel {kernel_name} does not match your dependencies. \n"
                    f"Please run command {command} to create kernel for your notebook.",
                    "type": "WARNING",
                }
            )

    return result


def install_packages(
    kernel_name: str,
    resolution_engine: str,
    kernels_path: Path = Path.home().joinpath(".local/share/thoth/kernels"),
    is_cli: bool = False,
    is_magic_command: bool = False,
) -> None:
    """Install dependencies in the virtualenv."""
    _LOGGER.info(f"kernel_name selected: {kernel_name}")

    env_path = kernels_path.joinpath(kernel_name)

    if not is_magic_command:
        env_path.mkdir(parents=True, exist_ok=True)

    package_manager: str = "micropipenv"

    _LOGGER.info(f"Installing requirements using {package_manager} in virtualenv at {env_path}.")

    # 1. Creating new environment
    if is_cli or resolution_engine != "pipenv":
        cli_run([str(env_path)])

    # 2. Install micropipenv and jupyterlab-requirements if not installed already
    packages = [package_manager, "jupyterlab-requirements"]

    for package in packages:
        check_install = subprocess.run(
            f". {kernel_name}/bin/activate &&"
            f"python3 -c \"import sys, pkgutil; sys.exit(0 if pkgutil.find_loader('{package}') else 1)\"",
            shell=True,
            cwd=kernels_path,
            capture_output=True,
        )

        if check_install.returncode != 0:
            _LOGGER.debug(f"{package} is not installed in the host!: %r", check_install.stderr)
            _ = subprocess.run(f". {kernel_name}/bin/activate && pip install {package}", shell=True, cwd=kernels_path)
        else:
            _LOGGER.debug(f"{package} is already present on the host!")

    # 3. Install packages using micropipenv
    _ = subprocess.run(
        f". {kernel_name}/bin/activate " f"&& cd {kernel_name} && micropipenv install --dev",
        shell=True,
        cwd=kernels_path,
    )


def get_packages(
    kernel_name: str, kernels_path: Path = Path.home().joinpath(".local/share/thoth/kernels")
) -> typing.Dict[str, str]:
    """Get packages in the virtualenv (pip list)."""
    _LOGGER.info(f"kernel_name selected: {kernel_name}")

    packages = {}

    if kernels_path.joinpath(kernel_name).exists():
        process_output = subprocess.run(
            f". {kernel_name}/bin/activate && pip list", shell=True, capture_output=True, cwd=kernels_path
        )

        processed_list = process_output.stdout.decode("utf-8").split("\n")[2:]

        for processed_package in processed_list:
            if processed_package:
                package_version = [el for el in processed_package.split(" ") if el != ""]
                packages[package_version[0]] = package_version[1]

    # default kernel for Jupyter
    if kernel_name == "python3":
        process_output = subprocess.run("pip list", shell=True, capture_output=True)

        processed_list = process_output.stdout.decode("utf-8").split("\n")[2:]

        for processed_package in processed_list:
            if processed_package:
                package_version = [el for el in processed_package.split(" ") if el != ""]
                packages[package_version[0]] = package_version[1]

    return packages


def create_kernel(kernel_name: str, kernels_path: Path = Path.home().joinpath(".local/share/thoth/kernels")) -> None:
    """Create kernel using new virtualenv."""
    _LOGGER.info(f"Setting new jupyter kernel {kernel_name} from {kernels_path}/{kernel_name}.")

    package = "ipykernel"

    check_install = subprocess.run(
        f". {kernel_name}/bin/activate &&"
        f"python3 -c \"import sys, pkgutil; sys.exit(0 if pkgutil.find_loader('{package}') else 1)\"",
        shell=True,
        cwd=kernels_path,
        capture_output=True,
    )

    if check_install.returncode != 0:
        _LOGGER.debug(f"{package} is not installed in the host!: %r", check_install.stderr)
        _ = subprocess.run(f". {kernel_name}/bin/activate && pip install {package}", shell=True, cwd=kernels_path)
    else:
        _LOGGER.debug(f"{package} is already present on the host!")

    _LOGGER.debug(f"Installing kernelspec called {kernel_name}.")

    try:
        process_output = subprocess.run(
            f". {kernel_name}/bin/activate && ipython kernel install --user"
            f" --name={kernel_name} --display-name 'Python ({kernel_name})'",
            shell=True,
            cwd=kernels_path,
            capture_output=True,
        )

        _LOGGER.info(process_output.stdout.decode("utf-8"))

    except Exception as e:
        _LOGGER.error(f"Could not enter environment {e}")


def horus_list_kernels(kernels_path: Path = Path.home().joinpath(".local/share/thoth/kernels")) -> typing.List[str]:
    """List kernels from host."""
    # List jupyter kernel
    try:
        command_output = subprocess.run(
            "jupyter kernelspec list --json",
            shell=True,
            capture_output=True,
        )
        _LOGGER.debug(command_output.returncode)

    except Exception as e:
        _LOGGER.error(f"Kernel list could not be obtained: {e}")

    # Parse json output from command
    kernels = [k for k in json.loads(command_output.stdout.decode("utf-8"))["kernelspecs"]]

    return kernels


def horus_delete_kernel(
    kernel_name: str, kernels_path: Path = Path.home().joinpath(".local/share/thoth/kernels")
) -> CompletedProcess:  # type: ignore
    """Delete kernel from host."""
    # Delete jupyter kernel
    try:
        command_output = subprocess.run(
            f"jupyter kernelspec remove -f {kernel_name}",
            shell=True,
            capture_output=True,
        )
        _LOGGER.debug(command_output.returncode)

    except Exception as e:
        _LOGGER.error(f"Selected kernel could not be deleted: {e}")

    # Delete folder from host
    env_path = kernels_path.joinpath(kernel_name)

    if env_path.exists():
        try:
            shutil.rmtree(env_path)
        except Exception as e:
            _LOGGER.debug(f"Repo at {env_path.as_posix()} was not removed because of: {e}")

    return command_output


def verify_gathered_libraries(
    gathered_libraries: typing.List[str],
) -> typing.List[typing.Dict[str, str]]:
    """Verify gathered libraries from invectio."""
    # Use Thoth user-API endpoint to verify what is the packages using that import name
    verified_libraries = []

    for import_name in gathered_libraries:
        unique_packages: typing.List[typing.Dict[str, str]] = []

        try:
            imported_packages = get_package_from_imported_packages(import_name)

            if imported_packages:
                for package in imported_packages:
                    if package["package_name"] not in [p["package_name"] for p in unique_packages]:
                        unique_packages.append(
                            {
                                "package_name": package["package_name"],
                                "index_url": package["index_url"],
                            }
                        )
                    else:
                        existing_indexes = [
                            p["index_url"] for p in unique_packages if p["package_name"] == package["package_name"]
                        ]

                        if package["index_url"] not in existing_indexes:
                            unique_packages.append(
                                {
                                    "package_name": package["package_name"],
                                    "index_url": package["index_url"],
                                }
                            )

                for unique_package in unique_packages:
                    verified_libraries.append(unique_package)
                    _LOGGER.info(
                        f"Package name {unique_package['package_name']} identifed for import name {import_name}"
                    )

        except Exception as error:
            _LOGGER.warning(f"No packages identified for import name {import_name}: {error}")
            _LOGGER.warning(f"Using {import_name} as package identified.")
            verified_libraries.append(
                {
                    "package_name": import_name,
                    "index_url": "https://pypi.org/simple",
                }
            )

    return verified_libraries


def gather_libraries(notebook_path: str) -> typing.List[str]:
    """Gather libraries with invectio."""
    gathered_libraries = []
    try:
        notebook_content_py = get_notebook_content(notebook_path=notebook_path, py_format=True)

        try:
            tree = ast.parse(notebook_content_py)
        except Exception:
            raise

        visitor = invectio.lib.InvectioLibraryUsageVisitor()
        visitor.visit(tree)

        report = visitor.get_module_report()

        std_lib_path = Path(sysconfig.get_python_lib(standard_lib=True))
        std_lib = {p.name.rstrip(".py") for p in std_lib_path.iterdir()}

        libs = filter(lambda k: k not in std_lib | set(sys.builtin_module_names), report)
        gathered_libraries = list(libs)
    except Exception as e:
        _LOGGER.error(f"Could not gather libraries: {e}")

    return gathered_libraries


def load_files(base_path: str) -> typing.Tuple[str, typing.Optional[str]]:
    """Load Pipfile/Pipfile.lock from path."""
    _LOGGER.info("Looking for Pipenv files located in %r directory", base_path)
    pipfile_path = Path(base_path).joinpath("Pipfile")
    pipfile_lock_path = Path(base_path).joinpath("Pipfile.lock")

    project = Project.from_files(
        pipfile_path=str(pipfile_path),
        pipfile_lock_path=str(pipfile_lock_path),
        without_pipfile_lock=not pipfile_lock_path.exists(),
    )

    if pipfile_lock_path.exists() and project.pipfile_lock.meta.hash["sha256"] != project.pipfile.hash()["sha256"]:
        _LOGGER.error(
            "Pipfile hash stated in Pipfile.lock %r does not correspond to Pipfile hash %r - was Pipfile "
            "adjusted? This error is not critical.",
            project.pipfile_lock.meta.hash["sha256"][:6],
            project.pipfile.hash()["sha256"][:6],
        )

    return (
        project.pipfile.to_string(),
        project.pipfile_lock.to_string() if project.pipfile_lock else None,
    )


def lock_dependencies_with_thoth(
    kernel_name: str,
    pipfile_string: str,
    config: str,
    timeout: int,
    force: bool,
    debug: bool,
    notebook_content: str,
    kernels_path: Path = Path.home().joinpath(".local/share/thoth/kernels"),
    labels: typing.Optional[typing.Dict[str, str]] = None,
) -> typing.Tuple[int, typing.Dict[str, typing.Any]]:
    """Lock dependencies using Thoth resolution engine."""
    initial_path = Path.cwd()
    # Get origin before changing path
    origin: typing.Optional[str] = _get_origin()
    _LOGGER.info("Origin identified by thamos: %r", origin)

    env_path = kernels_path.joinpath(kernel_name)

    env_path.mkdir(parents=True, exist_ok=True)
    os.chdir(env_path)

    _LOGGER.info("Resolution engine used: thoth")

    _LOGGER.info("Current path: %r ", env_path.as_posix())
    _LOGGER.info(f"Input Pipfile: \n{pipfile_string}")

    advise = {
        "thoth_analysis_id": "",
        "requirements": {},
        "requirements_lock": {},
        "error": False,
        "error_msg": "",
        "stack_info": [],
        "justification": [],
    }

    returncode = 0

    temp = tempfile.NamedTemporaryFile(prefix="jl_thoth_", mode="w+t")

    try:
        adviser_inputs = {"pipfile": pipfile_string, "config": config, "origin": origin}
        _LOGGER.info("Adviser inputs are: %r", adviser_inputs)

        temp.write(notebook_content)
        _LOGGER.info("path to temporary file is: %r", temp.name)

        response = advise_using_config(
            pipfile=pipfile_string,
            pipfile_lock="",  # TODO: Provide Pipfile.lock retrieved?
            runtime_environment_name=kernel_name,
            force=force,
            config=config,
            origin=origin,
            nowait=False,
            source_type=ThothAdviserIntegrationEnum.JUPYTER_NOTEBOOK,
            no_static_analysis=False,
            timeout=timeout,
            src_path=temp.name,
            debug=debug,
            labels=labels,
        )

        _LOGGER.info(f"Response: {response}")

        if not response:
            raise Exception("Analysis was not successful.")

        result, error_result = response
        thoth_analysis_id = result["parameters"]["output"].split("/")[-1]
        advise["thoth_analysis_id"] = thoth_analysis_id

        if error_result:
            advise["error"] = True
            advise["error_msg"] = result.get("error_msg")
            returncode = 1

        else:
            # Use report of the best one, therefore index 0
            if result["report"] and result["report"]["products"]:
                justifications = result["report"]["products"][0]["justification"]
                pipfile = result["report"]["products"][0]["project"]["requirements"]
                pipfile_lock = result["report"]["products"][0]["project"]["requirements_locked"]

                advise["requirements"] = pipfile
                advise["requirements_lock"] = pipfile_lock
                advise["error"] = False
                advise["justification"] = justifications

            if result["report"] and result["report"]["stack_info"]:
                stack_info = result["report"]["stack_info"]
                advise["stack_info"] = stack_info

    except Exception as api_error:
        _LOGGER.debug(f"error locking dependencies using Thoth: {api_error}")
        advise["error"] = True
        if not advise.get("error_msg"):
            advise[
                "error_msg"
            ] = f"Error locking dependencies, check pod logs for more details about the error. {api_error}"
        returncode = 1

    finally:
        temp.close()

    _LOGGER.info(f"advise received: {advise}")

    if not advise["error"]:
        try:
            requirements_format = "pipenv"

            project = Project.from_dict(pipfile, pipfile_lock)

            pipfile_path = env_path.joinpath("Pipfile")
            pipfile_lock_path = env_path.joinpath("Pipfile.lock")

            if requirements_format == "pipenv":
                _LOGGER.info("Writing to Pipfile/Pipfile.lock in %r", env_path.as_posix())
                project.to_files(pipfile_path=str(pipfile_path), pipfile_lock_path=str(pipfile_lock_path))
        except Exception as e:
            _LOGGER.debug("Requirements files cannot be stored due to: %r", e)

    os.chdir(initial_path)

    return returncode, advise


def get_thoth_config(
    kernel_name: str,
    kernels_path: Path = Path.home().joinpath(".local/share/thoth/kernels"),
) -> _Configuration:
    """Get Thoth config."""
    initial_path = Path.cwd()
    env_path = kernels_path.joinpath(kernel_name)
    env_path.mkdir(parents=True, exist_ok=True)

    os.chdir(env_path)

    _LOGGER.info(f"kernel_name selected: {kernel_name} and path: {env_path}")

    config = _Configuration()  # type: ignore

    if not config.config_file_exists():
        _LOGGER.debug("Thoth config does not exist, creating it...")
        try:
            config.create_default_config()
        except Exception as e:
            raise Exception("Thoth config file could not be created! %r", e)

    config.load_config()

    os.chdir(initial_path)

    return config


def lock_dependencies_with_pipenv(
    kernel_name: str,
    pipfile_string: str,
    kernels_path: Path = Path.home().joinpath(".local/share/thoth/kernels"),
) -> typing.Tuple[int, typing.Dict[str, typing.Any]]:
    """Lock dependencies using Pipenv resolution engine."""
    initial_path = Path.cwd()
    env_path = kernels_path.joinpath(kernel_name)

    # Delete and recreate folder
    if not env_path.exists():
        _ = subprocess.call(f"rm -rf ./{kernel_name} ", shell=True, cwd=kernels_path)

    env_path.mkdir(parents=True, exist_ok=True)

    result = {"requirements_lock": "", "error": False, "error_msg": ""}
    returncode = 0

    ## Create virtualenv
    cli_run([str(env_path)])

    pipfile_path = env_path.joinpath("Pipfile")

    _LOGGER.info("Resolution engine used: pipenv")

    with open(pipfile_path, "w") as pipfile_file:
        pipfile_file.write(pipfile_string)

    _LOGGER.info(f"kernel path: {env_path}")
    _LOGGER.info(f"Input Pipfile: \n{pipfile_string}")

    # 2. Install pipenv if not installed already
    package = "pipenv"
    check_install = subprocess.run(
        f"python3 -c \"import sys, pkgutil; sys.exit(0 if pkgutil.find_loader('{package}') else 1)\"",
        shell=True,
        cwd=kernels_path,
        capture_output=True,
    )

    if check_install.returncode != 0:
        _LOGGER.debug(f"pipenv is not installed in the host!: {check_install.stderr!r}")

        try:
            subprocess.run("pip install pipenv", cwd=kernels_path, shell=True)
        except Exception as pipenv_install_error:
            _LOGGER.debug("error installing pipenv: %r", pipenv_install_error)
            result["error"] = True
            result["error_msg"] = pipenv_install_error
            returncode = 1
            os.chdir(initial_path)

            return returncode, result
    else:
        _LOGGER.debug("pipenv is already present on the host!")

    pipfile_lock_path = env_path.joinpath("Pipfile.lock")

    try:
        output = subprocess.run(
            f". {kernel_name}/bin/activate && cd {kernel_name} && pipenv lock",
            env=dict(os.environ, PIPENV_CACHE_DIR="/tmp"),
            cwd=kernels_path,
            shell=True,
            capture_output=True,
        )
    except Exception as pipenv_error:
        _LOGGER.debug("error locking dependencies using Pipenv: %r", pipenv_error)
        result["error"] = True
        result["error_msg"] = str(pipenv_error)
        returncode = 1

    if output.returncode != 0:
        _LOGGER.debug("error in process trying to lock dependencies with pipenv: %r", output.stderr)
        result["error"] = True
        result["error_msg"] = str(output.stderr)
        returncode = 1

    os.chdir(env_path)

    if not result["error"]:

        if pipfile_lock_path.exists():

            with open(pipfile_lock_path, "r") as pipfile_lock_file:
                pipfile_lock_str = pipfile_lock_file.read()

            pipfile = Pipfile.from_string(pipfile_string)
            pipfile_lock_: PipfileLock = PipfileLock.from_string(pipfile_lock_str, pipfile=pipfile)

            result["requirements_lock"] = pipfile_lock_.to_dict()

            _LOGGER.debug(f"result from pipenv received: {result}")

        else:
            _LOGGER.debug("Pipfile.lock cannot be found at: %r", str(pipfile_lock_path))
            result["error"] = True
            result["error_msg"] = "Error retrieving Pipfile.lock created from pipenv."

    os.chdir(initial_path)

    return returncode, result


def horus_requirements_command(
    path: str,
    index_url: str,
    dev: bool,
    add: typing.Optional[typing.List[str]] = None,
    remove: typing.Optional[typing.List[str]] = None,
    save_in_notebook: bool = True,
) -> Pipfile:
    """Horus requirements command."""
    notebook = get_notebook_content(notebook_path=path)
    notebook_metadata = dict(notebook.get("metadata"))

    pipfile_string = notebook_metadata.get("requirements")

    if not pipfile_string:
        python_version = discover_python_version()
        pipfile_ = create_pipfile_from_packages(packages=[], python_version=python_version)
    else:
        pipfile_ = Pipfile.from_string(pipfile_string)

    if add:
        for req in add:
            _LOGGER.info(
                "Adding %r to %s requirements",
                req,
                "development" if dev else "default",
            )
            pipfile_.add_requirement(req, is_dev=dev, index_url=index_url, force=True)

    if remove:
        for req in remove:
            any_change = False

            if req in pipfile_.packages.packages:
                pipfile_.packages.packages.pop(req)
                _LOGGER.info(
                    "Removed %r from default requirements",
                    req,
                )
                any_change = True

            if req in pipfile_.dev_packages.packages:
                pipfile_.dev_packages.packages.pop(req)
                _LOGGER.info(
                    "Removed %r from development requirements",
                    req,
                )
                any_change = True

            if not any_change:
                _LOGGER.error(
                    "Requirement %r not found in requirements, " "aborting making any changes.",
                    req,
                )
                sys.exit(1)

    if save_in_notebook:
        notebook_metadata["requirements"] = json.dumps(pipfile_.to_dict())

        notebook["metadata"] = notebook_metadata
        save_notebook_content(notebook_path=path, notebook=notebook)

    return pipfile_


def create_pipfile_from_packages(packages: typing.List[str], python_version: str) -> Pipfile:
    """Create Pipfile from list of packages."""
    source = Source(url="https://pypi.org/simple", name="pypi", verify_ssl=True)

    pipfile_meta = PipfileMeta(sources={"pypi": source}, requires={"python_version": python_version})

    packages_versions = []

    for package_name in packages:
        package_version = PackageVersion(name=package_name, version="*", develop=False)
        packages_versions.append(package_version)

    pipfile_ = Pipfile.from_package_versions(packages=packages_versions, meta=pipfile_meta)

    return pipfile_


def save_notebook_content(notebook_path: str, notebook: typing.Dict[str, typing.Any]) -> typing.Dict[str, typing.Any]:
    """Save notebook content."""
    with open(notebook_path, "w") as notebook_content:
        json.dump(notebook, notebook_content)

    return notebook


def horus_show_command(
    path: str,
    pipfile: bool = False,
    pipfile_lock: bool = False,
    thoth_config: bool = False,
) -> typing.Dict[str, typing.Any]:
    """Horus show command."""
    show_all: bool = False

    if not pipfile and not pipfile_lock and not thoth_config:
        # If no parameter to be shown is set, show all is set.
        show_all = True

    results = {}
    results["kernel_name"] = ""
    results["dependency_resolution_engine"] = ""
    results["thoth_analysis_id"] = ""
    results["pipfile"] = ""
    results["pipfile_lock"] = ""
    results["thoth_config"] = ""

    notebook = get_notebook_content(notebook_path=path)
    notebook_metadata = notebook.get("metadata")

    if notebook_metadata.get("language_info"):
        language = notebook_metadata["language_info"]["name"]

        if language and language != "python":
            raise Exception("Only Python kernels are currently supported.")

    if notebook_metadata.get("kernelspec"):
        kernelspec = notebook_metadata.get("kernelspec")
        kernel_name = kernelspec.get("name")
    else:
        kernel_name = "python3"

    results["kernel_name"] = kernel_name

    dependency_resolution_engine = notebook_metadata.get("dependency_resolution_engine")
    results["dependency_resolution_engine"] = dependency_resolution_engine

    thoth_analysis_id = notebook_metadata.get("thoth_analysis_id")
    results["thoth_analysis_id"] = thoth_analysis_id

    pipfile_string = notebook_metadata.get("requirements")

    if pipfile or pipfile_lock or show_all:
        if not pipfile_string:
            results["pipfile"] = "No Pipfile identified in notebook metadata."
        else:
            pipfile_ = Pipfile.from_string(pipfile_string)

            if pipfile or show_all:
                results["pipfile"] = f"\nPipfile:\n\n{pipfile_.to_string()}"

    if pipfile_lock or show_all:

        if pipfile_string:
            pipfile_lock_string = notebook_metadata.get("requirements_lock")

            if not pipfile_lock_string:
                results["pipfile_lock"] = "No Pipfile.lock identified in notebook metadata."
            else:
                pipfile_lock_ = PipfileLock.from_string(pipfile_content=pipfile_lock_string, pipfile=pipfile_)
                results["pipfile_lock"] = f"\nPipfile.lock:\n\n{pipfile_lock_.to_string()}"
        else:
            results[
                "pipfile_lock"
            ] = "No Pipfile identified in notebook metadata, therefore Pipfile.lock cannot be created."

    if thoth_config or show_all:
        thoth_config_string = notebook_metadata.get("thoth_config")

        if not thoth_config_string:
            results["thoth_config"] = "No .thoth.yaml identified in notebook metadata."
        else:
            config = _Configuration()  # type: ignore
            config.load_config_from_string(thoth_config_string)
            results["thoth_config"] = f"\n.thoth.yaml:\n\n{yaml.dump(config.content)}"

    return results


def update_runtime_environment_in_thoth_config(
    kernel: str,
    config: str,
    os_name: typing.Optional[str] = None,
    os_version: typing.Optional[str] = None,
    python_version: typing.Optional[str] = None,
    recommendation_type: typing.Optional[str] = None,
) -> str:
    """Update runtime environment in thoth config."""
    thoth_config = _Configuration()  # type: ignore
    thoth_config.load_config_from_string(config)

    runtime_environments = []
    # runtime environment with same name does not exists.
    runtime_environment = dict(thoth_config.get_runtime_environment())
    runtime_environment["name"] = kernel

    # Assign parameters
    operating_system = {
        "name": runtime_environment["operating_system"]["name"],
        "version": runtime_environment["operating_system"]["version"],
    }

    if os_name:
        operating_system["name"] = os_name

    if os_version:
        operating_system["version"] = os_version

    runtime_environment["operating_system"] = operating_system

    if python_version:
        runtime_environment["python_version"] = python_version

    if recommendation_type:
        runtime_environment["recommendation_type"] = recommendation_type

    # Assign runtime environment to thoth config runtime environment.
    runtime_environments.append(runtime_environment)
    thoth_config.content["runtime_environments"] = runtime_environments

    # TODO: Use adjusted method from thamos
    # thoth_config.set_runtime_environment(runtime_environment=runtime_environment, force=True)

    return json.dumps(thoth_config.content)


def horus_lock_command(
    path: str,
    resolution_engine: str = "thoth",
    timeout: int = 180,
    force: bool = False,
    debug: bool = False,
    recommendation_type: str = "latest",
    kernel_name: typing.Optional[str] = None,
    os_name: typing.Optional[str] = None,
    os_version: typing.Optional[str] = None,
    python_version: typing.Optional[str] = None,
    labels: typing.Optional[typing.Dict[str, str]] = None,
    save_in_notebook: bool = True,
    save_on_disk: bool = False,
) -> typing.Tuple[typing.Dict[str, typing.Any], typing.Dict[str, typing.Any]]:
    """Lock requirements in notebook metadata."""
    results = {}
    results["kernel_name"] = ""
    results["dependency_resolution_engine"] = resolution_engine

    notebook = get_notebook_content(notebook_path=path)
    notebook_metadata = notebook.get("metadata")

    if notebook_metadata.get("kernelspec"):
        kernelspec = notebook_metadata.get("kernelspec")
        notebook_kernel = kernelspec.get("name")
    else:
        kernel_name = "python3"

    if not kernel_name:
        kernel = notebook_kernel
    else:
        kernel = kernel_name

    if kernel == "python3":
        kernel = "jupyterlab-requirements"

    results["kernel_name"] = kernel

    requirements = notebook_metadata.get("requirements")

    if not requirements:
        raise KeyError(
            "No Pipfile identified in notebook metadata."
            "You can start creating one with command: "
            "`horus requirements [NOTEBOOK].ipynb --add [PACKAGE NAME]`"
        )

    pipfile_ = Pipfile.from_string(requirements)

    error = False
    if resolution_engine == "thoth":

        thoth_config_string = notebook_metadata.get("thoth_config")

        if not thoth_config_string:
            thoth_config = get_thoth_config(kernel_name=kernel)
        else:
            thoth_config = _Configuration()  # type: ignore
            thoth_config.load_config_from_string(thoth_config_string)

        try:
            notebook_content_py = get_notebook_content(notebook_path=path, py_format=True)
        except Exception as e:
            _LOGGER.error(f"Could not get notebook content!: {e!r}")
            notebook_content_py = ""

        # update runtime environment in thoth config
        thoth_config_updated = update_runtime_environment_in_thoth_config(
            kernel=kernel,
            config=json.dumps(thoth_config.content),
            os_name=os_name,
            os_version=os_version,
            python_version=python_version,
            recommendation_type=recommendation_type,
        )

        _, lock_results = lock_dependencies_with_thoth(
            kernel_name=kernel,
            pipfile_string=requirements,
            config=thoth_config_updated,
            timeout=timeout,
            force=force,
            debug=debug,
            notebook_content=notebook_content_py,
            labels=labels,
        )
        lock_results["thoth_config"] = thoth_config_updated

        if not lock_results["error"]:
            requirements = lock_results["requirements"]
            requirements_lock = lock_results["requirements_lock"]
            notebook_metadata["thoth_config"] = thoth_config_updated
            notebook_metadata["thoth_analysis_id"] = lock_results["thoth_analysis_id"]

        else:
            error = True

    if resolution_engine == "pipenv":
        _, lock_results = lock_dependencies_with_pipenv(kernel_name=kernel, pipfile_string=pipfile_.to_string())

        # Remove if Pipenv is used after Thoth was used.
        if notebook_metadata.get("thoth_analysis_id"):
            notebook_metadata["thoth_analysis_id"] = ""

        if not lock_results["error"]:
            requirements_lock = lock_results["requirements_lock"]
        else:
            error = True

    if save_on_disk and not error:
        home = Path.home()
        store_path: Path = home.joinpath(".local/share/thoth/kernels")

        complete_path: Path = store_path.joinpath(kernel)

        complete_path.mkdir(parents=True, exist_ok=True)

        _LOGGER.info("Path used to store dependencies is: %r", complete_path.as_posix())

        # requirements and requirements locked are already stored at this point

        if resolution_engine == "thoth":
            # thoth
            config = _Configuration()  # type: ignore
            config.load_config_from_string(thoth_config_updated)
            config_path = complete_path.joinpath(".thoth.yaml")
            config.save_config(path=str(config_path))

    if save_in_notebook and not error:
        notebook_metadata["dependency_resolution_engine"] = resolution_engine
        notebook_metadata["requirements"] = json.dumps(requirements)
        notebook_metadata["requirements_lock"] = json.dumps(requirements_lock)

        # Assign kernel name to kernelspec.
        kernelspec["name"] = kernel
        notebook_metadata["kernelspec"] = kernelspec

        notebook["metadata"] = notebook_metadata
        save_notebook_content(notebook_path=path, notebook=notebook)

    return results, lock_results


def horus_set_kernel_command(
    path: str,
    kernel_name: typing.Optional[str] = None,
    save_in_notebook: bool = True,
    resolution_engine: typing.Optional[str] = None,
    is_magic_command: bool = False,
    force: bool = False,
) -> typing.Dict[str, typing.Any]:
    """Create kernel using dependencies in notebook metadata."""
    results = {}
    results["kernel_name"] = ""
    results["dependency_resolution_engine"] = ""

    # 0. Check if all metadata for dependencies are present in the notebook
    notebook = get_notebook_content(notebook_path=path)
    notebook_metadata = notebook.get("metadata")

    if notebook_metadata.get("language_info"):
        language = notebook_metadata["language_info"]["name"]

        if language and language != "python":
            raise Exception("Only Python kernels are currently supported.")

    kernelspec = notebook_metadata.get("kernelspec")
    notebook_kernel = kernelspec.get("name")

    if not kernel_name:
        kernel = notebook_kernel
    else:
        kernel = kernel_name

    if kernel == "python3":
        kernel = "jupyterlab-requirements"

    results["kernel_name"]: str = kernel  # type: ignore

    home = Path.home()
    store_path: Path = home.joinpath(".local/share/thoth/kernels")

    if not resolution_engine:
        dependency_resolution_engine = notebook_metadata.get("dependency_resolution_engine")

        if not dependency_resolution_engine:
            raise KeyError("No Resolution engine identified in notebook metadata.")
    else:
        dependency_resolution_engine = resolution_engine

    results["dependency_resolution_engine"] = dependency_resolution_engine

    complete_path: Path = store_path.joinpath(kernel)

    if not is_magic_command or force:
        if complete_path.exists():
            horus_delete_kernel(kernel_name=kernel)

        complete_path.mkdir(parents=True, exist_ok=True)

    # 1. Get Pipfile, Pipfile.lock and .thoth.yaml and store them in ./.local/share/kernel/{kernel_name}

    # requirements
    if not is_magic_command:
        pipfile_string = notebook_metadata.get("requirements")
        pipfile_ = Pipfile.from_string(pipfile_string)
        pipfile_path = complete_path.joinpath("Pipfile")
        pipfile_.to_file(path=str(pipfile_path))

    # requirements lock
    if not is_magic_command:
        pipfile_lock_string = notebook_metadata.get("requirements_lock")
        pipfile_lock_ = PipfileLock.from_string(pipfile_content=pipfile_lock_string, pipfile=pipfile_)
        pipfile_lock_path = complete_path.joinpath("Pipfile.lock")
        pipfile_lock_.to_file(path=str(pipfile_lock_path))

    if dependency_resolution_engine == "thoth" and not is_magic_command:
        # thoth
        thoth_config_string = notebook_metadata.get("thoth_config")
        config = _Configuration()  # type: ignore
        config.load_config_from_string(thoth_config_string)
        config_path = complete_path.joinpath(".thoth.yaml")
        config.save_config(path=str(config_path))

    # 2. Create virtualenv and install dependencies
    install_packages(
        kernel_name=kernel,
        resolution_engine=dependency_resolution_engine,
        is_cli=True,
        is_magic_command=is_magic_command,
    )

    # 3. Assign virtualenv to jupyter kernel
    create_kernel(kernel_name=kernel)

    if save_in_notebook:
        # Update kernel name if different name selected.
        kernelspec["name"] = kernel
        notebook_metadata["kernelspec"] = kernelspec
        notebook["metadata"] = notebook_metadata
        save_notebook_content(notebook_path=path, notebook=notebook)

    return results


def horus_extract_command(
    notebook_path: str,
    store_files_path: str,
    pipfile: bool = False,
    pipfile_lock: bool = False,
    thoth_config: bool = False,
    use_overlay: bool = False,
    force: bool = False,
) -> typing.Dict[str, typing.Any]:
    """Horus extract command."""
    results = {}
    results["kernel_name"] = ""
    results["resolution_engine"] = ""

    extract_all: bool = False

    if not pipfile and not pipfile_lock and not thoth_config:
        # If no parameter to be extracted is set, extract all is set.
        extract_all = True

    notebook = get_notebook_content(notebook_path=notebook_path)
    notebook_metadata = notebook.get("metadata")

    if notebook_metadata.get("language_info"):
        language = notebook_metadata["language_info"]["name"]

        if language and language != "python":
            raise Exception("Only Python kernels are currently supported.")

    if notebook_metadata.get("kernelspec"):
        kernelspec = notebook_metadata.get("kernelspec")
        kernel_name = kernelspec.get("name")
    else:
        kernel_name = "python3"

    results["kernel_name"] = kernel_name
    store_path: Path = Path(store_files_path)

    if use_overlay:
        if not kernel_name:
            raise KeyError("No kernel name identified in notebook metadata kernelspec.")

        store_path = store_path.joinpath("overlays").joinpath(kernel_name)
        store_path.mkdir(parents=True, exist_ok=True)

    dependency_resolution_engine = notebook_metadata.get("dependency_resolution_engine")

    if not dependency_resolution_engine:
        raise KeyError("No Resolution engine identified in notebook metadata.")

    results["resolution_engine"] = dependency_resolution_engine

    if pipfile or pipfile_lock or extract_all:
        pipfile_string = notebook_metadata.get("requirements")

        if not pipfile_string:
            raise KeyError("No Pipfile identified in notebook metadata.")

        pipfile_ = Pipfile.from_string(pipfile_string)

    if pipfile or extract_all:

        pipfile_path = store_path.joinpath("Pipfile")

        if pipfile_path.exists() and not force:
            raise FileExistsError(
                f"Cannot store Pipfile because it already exists at path: {pipfile_path.as_posix()!r}. "
                "Use --force to overwrite existing content or --show-only to visualize it."
            )
        else:
            pipfile_.to_file(path=str(pipfile_path))

    if pipfile_lock or extract_all:
        pipfile_lock_string = notebook_metadata.get("requirements_lock")

        if not pipfile_lock_string:
            raise KeyError("No Pipfile.lock identified in notebook metadata.")

        pipfile_lock_ = PipfileLock.from_string(pipfile_content=pipfile_lock_string, pipfile=pipfile_)

        pipfile_lock_path = store_path.joinpath("Pipfile.lock")

        if pipfile_lock_path.exists() and not force:
            raise FileExistsError(
                f"Cannot store Pipfile.lock because it already exists at path: {pipfile_lock_path.as_posix()!r}. "
                "Use --force to overwrite existing content or --show-only to visualize it."
            )
        else:
            pipfile_lock_.to_file(path=str(pipfile_lock_path))

    if thoth_config or extract_all:
        thoth_config_string = notebook_metadata.get("thoth_config")

        if not thoth_config_string:
            raise KeyError("No .thoth.yaml identified in notebook metadata.")

        config = _Configuration()  # type: ignore
        config.load_config_from_string(thoth_config_string)

        yaml_path = Path(".thoth.yaml")
        if yaml_path.exists() and not force:
            raise FileExistsError(
                f"Cannot store .thoth.yaml because it already exists at path: {yaml_path.as_posix()!r}. "
                "Use --force to overwrite existing content or --show-only to visualize it."
            )
        else:
            config.save_config()

    return results


def horus_log_command(notebook_path: str) -> str:
    """Get log analysis results from adviser ID."""
    notebook = get_notebook_content(notebook_path=notebook_path)
    notebook_metadata = notebook.get("metadata")

    if "requirements_lock" not in notebook_metadata.keys():
        raise Exception(f"notebook at {notebook_path} does not has locked requirements.")

    if "dependency_resolution_engine" not in notebook_metadata.keys():
        raise Exception(f"notebook at {notebook_path} misses resolution engine key in metadata.")

    if notebook_metadata["dependency_resolution_engine"] != "thoth":
        raise Exception("This command is available only for Thoth resolution engine.")

    if "thoth_analysis_id" not in notebook_metadata.keys():
        raise Exception(f"thoth_analysis_id key is not present in the metadata of notebook at: {notebook_path}.")
    else:
        thoth_analysis_id = notebook_metadata["thoth_analysis_id"]

    log_str = get_log(thoth_analysis_id)

    return log_str  # type: ignore
