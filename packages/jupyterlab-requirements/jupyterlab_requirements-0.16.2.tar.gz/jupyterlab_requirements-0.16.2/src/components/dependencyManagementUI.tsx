/**
 * Jupyterlab requirements.
 *
 * Jupyterlab extension for managing dependencies.
 *
 * @link   https://github.com/thoth-station/jupyterlab-requirements#readme
 * @file   Jupyterlab extension for managing dependencies.
 * @author Francesco Murdaca <fmurdaca@redhat.com>
 * @since  0.0.1
 */

import _ from "lodash";

import * as React from 'react';

import { NotebookPanel } from '@jupyterlab/notebook';

import { DependencyManagementForm } from './dependencyManagementForm'
import { DependencyManagementSaveButton } from './dependencyManagementSaveButton'
import { DependencyManagementInstallButton } from './dependencyManagementInstallButton'
import { DependencyManagementNewPackageButton } from './dependencyManagementAddPackageButton';

import { delete_key_from_notebook_metadata, get_python_version, take_notebook_content } from "../notebook";
import { Requirements, RequirementsLock } from '../types/requirements';

import { ThothConfig } from '../types/thoth';

import {
  install_packages,
  create_new_kernel,
  discover_root_directory
} from '../kernel';

import {
  update_thoth_config_on_disk,
  lock_requirements_with_thoth,
  lock_requirements_with_pipenv
} from '../thoth';

import { INotification } from 'jupyterlab_toastify';

import {
  get_kernel_name
} from "../notebook"

import { KernelModel } from '../model';

import { Advise } from "../types/thoth";

import {
  parse_inputs_from_metadata,
  create_config,
  set_notebook_metadata,
  store_dependencies_on_disk,
  _parse_packages_from_state,
  _handle_deleted_packages_case,
  _handle_total_packages_case,
  _handle_thoth_config
} from "../helpers";
import StylizedTextInput from "./StylizedTextInput";
import StylizedDropdown from "./StylizedDropdown";
import axios from "axios";
import StylizedBanner from "./StylizedBanner";

/**
 * The class name added to the new package button (CSS).
 */
const OK_BUTTON_CLASS = "thoth-ok-button";
const CONTAINER_BUTTON = "thoth-container-button";
const CONTAINER_BUTTON_CENTRE = "thoth-container-button-centre";
const INPUT_FORM_BOX = "thoth-form-box";
const INPUT_OPTIONS = "thoth-inputs-options";
const FORM_GRID = "form-grid"

/**
 * Class: Holds properties for DependenciesManagementDialog.
 */

export interface IDependencyManagementUIProps {
  panel: NotebookPanel
  loaded_requirements: Requirements,
  loaded_requirements_lock: RequirementsLock,
  loaded_config_file: ThothConfig,
  loaded_resolution_engine: string
}

/**
 * Class: Holds state for DependenciesManagementDialog.
 */

export interface IDependencyManagementUIState {
  kernel_name: string
  recommendation_type: string
  status: string,
  packages: { [ name: string ]: string },
  installed_packages: { [ name: string ]: string },
  loaded_packages: { [ name: string ]: string },
  deleted_packages: { [ name: string ]: string },
  requirements: Requirements,
  thoth_config: ThothConfig,
  error_msg: string,
  resolution_engine: string,
  thoth_timeout: number,
  thoth_force: boolean,
  thoth_debug: boolean,
  os_name: string,
  os_version: string,
  python_version: string,
  root_directory: string,
  thoth_resolution_error_msg: string,
  pipenv_resolution_error_msg: string,
  labels: string,
  warnings: {inPyPI: (string)[], unknown: (string)[]}
}

/**
 * A React Component for handling dependency management.
 */

export class DependenciesManagementUI extends React.Component<IDependencyManagementUIProps, IDependencyManagementUIState> {
    constructor(
      props: IDependencyManagementUIProps
    ) {
      super(props);

      this.state = {
        kernel_name: get_kernel_name( this.props.panel ),
        recommendation_type: "latest",
        status: "loading",
        packages: {},  // editing
        loaded_packages: {},
        installed_packages: {},
        deleted_packages: {},
        requirements: {
          packages: {},
          requires: { python_version: get_python_version( this.props.panel ) },
          source: [{
            name: "pypi",
            url: "https://pypi.org/simple",
            verify_ssl: true,
          }]
        },
        thoth_config: {
          host: "khemenu.thoth-station.ninja",
          tls_verify: false,
          requirements_format: "pipenv",
          runtime_environments: [{
            name: "ubi:8",
            operating_system: {
              name: "ubi",
              version: "8",
            },
            python_version: "3.8",
            recommendation_type: "latest",
            base_image: "",
            labels: "",
            hardware: {
              cpu_model: null,
              cpu_family: null,
              gpu_family: null,
            }
          }]
        },
        error_msg: undefined,
        resolution_engine: "thoth",
        thoth_timeout: 180,
        thoth_force: false,
        thoth_debug: true,
        os_name: "ubi",
        os_version: "8",
        python_version: "3.8",
        root_directory: "",
        thoth_resolution_error_msg: undefined,
        pipenv_resolution_error_msg: undefined,
        labels: "",
        warnings: {inPyPI: [], unknown: []}
      }

      this.onStart = this.onStart.bind(this),
      this.execute_code_in_kernel = this.execute_code_in_kernel.bind(this),
      this.changeUIstate = this.changeUIstate.bind(this),
      this.addNewRow = this.addNewRow.bind(this),
      this.editRow = this.editRow.bind(this),
      this.editSavedRow = this.editSavedRow.bind(this),
      this.storeRow = this.storeRow.bind(this),
      this.deleteRow = this.deleteRow.bind(this),
      this.deleteSavedRow = this.deleteSavedRow.bind(this),
      this.onSave = this.onSave.bind(this),
      this.lock = this.lock.bind(this),
      this.lock_using_thoth = this.lock_using_thoth.bind(this),
      this.lock_using_pipenv = this.lock_using_pipenv.bind(this),
      this.install = this.install.bind(this),
      this.setKernel = this.setKernel.bind(this),
      this.setKernelName = this.setKernelName.bind(this)
      this.changeRecommendationType = this.changeRecommendationType.bind(this)
      this.setTimeout = this.setTimeout.bind(this)
      this.setPythonVersion = this.setPythonVersion.bind(this)
      this.setOSName = this.setOSName.bind(this)
      this.setOSVersion = this.setOSVersion.bind(this)
      this.setRootDirectoryPath = this.setRootDirectoryPath.bind(this)
      this.setThothLabels = this.setThothLabels.bind(this)
      this.setResolutionEngine = this.setResolutionEngine.bind(this)
      this.setDebugParameter = this.setDebugParameter.bind(this)
      this.setForceParameter = this.setForceParameter.bind(this)
      this.verifyPyPI = this.verifyPyPI.bind(this)
      this.verifyPackages = this.verifyPackages.bind(this)

      this._model = new KernelModel ( this.props.panel.sessionContext )
    }

    /**
     * Function to execute code in the kernel as a cell in the notebook
     */

    async execute_code_in_kernel(code: string) {
      await this._model.execute( code )
    }


    /**
     * Function: Main function to change state and status!
     */

    changeUIstate(
      status: string,
      packages: { [ name: string ]: string },
      loaded_packages: { [ name: string ]: string },
      installed_packages: { [ name: string ]: string },
      deleted_packages: { [ name: string ]: string },
      requirements: Requirements,
      kernel_name: string,
      thoth_config: ThothConfig,
      error_msg?: string,
      thoth_resolution_error_msg?: string,
      pipenv_resolution_error_msg?: string,
    ) {

      var new_state: IDependencyManagementUIState = this.state
      console.debug("initial", new_state)

      _.set(new_state, "status", status)

      _.set(new_state, "packages", packages)

      _.set(new_state, "loaded_packages", loaded_packages)

      _.set(new_state, "installed_packages", installed_packages)

      _.set(new_state, "deleted_packages", deleted_packages)

      _.set(new_state, "requirements", requirements)

      _.set(new_state, "kernel_name", kernel_name)

      _.set(new_state, "thoth_config", thoth_config)

      _.set(new_state, "error_msg", error_msg)

      _.set(new_state, "thoth_resolution_error_msg", thoth_resolution_error_msg)

      _.set(new_state, "pipenv_resolution_error_msg", pipenv_resolution_error_msg)

      console.debug("new", new_state)
      this.setState(new_state);
    }

    async setNewState(ui_state: IDependencyManagementUIState) {

      console.log("new state", ui_state)
      this.setState(ui_state);
    }

    /**
     * Function: Change recommendation type for thamos advise
     */

    changeRecommendationType(selected: string) {
      this.setState(
        {
          recommendation_type: selected,
        }
      );

    }

    /**
     * Function: Set force for thamos advise
     */

     setForceParameter(event: React.ChangeEvent<HTMLInputElement>) {
        this.setState(
          {
            thoth_force: event.target.checked
          }
        );
     }


    /**
     * Function: Set debug for thamos advise
     */

     setDebugParameter(event: React.ChangeEvent<HTMLInputElement>) {
      this.setState(
        {
          thoth_debug: event.target.checked
        }
      );
   }

    /**
     * Function: Set base image
     */

    setBaseImage(event: React.ChangeEvent<HTMLInputElement>) {

      var thoth_base_image = event.target.value

      var initial_thoth_config = this.state.thoth_config

      _.set(initial_thoth_config, initial_thoth_config.runtime_environments[0].base_image, thoth_base_image)

      this.setState(
        {
          thoth_config: initial_thoth_config
        }
      );
    }

    /**
     * Function: Set Python Version
     */

     setPythonVersion(event: React.ChangeEvent<HTMLInputElement>) {

      var thoth_python_version = event.target.value

      var initial_thoth_config = this.state.thoth_config

      _.set(initial_thoth_config, initial_thoth_config.runtime_environments[0].python_version, thoth_python_version)

      this.setState(
        {
          thoth_config: initial_thoth_config,
          python_version: thoth_python_version
        }
      );
    }

    /**
     * Function: Set OS name
     */

     setOSName(event: React.ChangeEvent<HTMLInputElement>) {

      var thoth_os_name = event.target.value

      var initial_thoth_config = this.state.thoth_config

      _.set(initial_thoth_config, initial_thoth_config.runtime_environments[0].operating_system.name, thoth_os_name)

      this.setState(
        {
          thoth_config: initial_thoth_config,
          os_name: thoth_os_name
        }
      );
    }

    /**
     * Function: Set OS version
     */

    setOSVersion(event: React.ChangeEvent<HTMLInputElement>) {

      var thoth_os_version = event.target.value

      var initial_thoth_config = this.state.thoth_config

      _.set(initial_thoth_config, initial_thoth_config.runtime_environments[0].operating_system.version, thoth_os_version)

      this.setState(
        {
          thoth_config: initial_thoth_config,
          os_version: thoth_os_version
        }
      );
    }


    /**
     * Function: Set Thoth labels (comma separated values)
     */

    setThothLabels(event: React.ChangeEvent<HTMLInputElement>) {

      var labels = event.target.value

      // Check labels inputs (comma separated) is done on the backend currently!
      var initial_thoth_config = this.state.thoth_config

      _.set(initial_thoth_config, initial_thoth_config.runtime_environments[0].base_image, labels)

      this.setState(
        {
          thoth_config: initial_thoth_config,
          labels: labels
        }
      );
    }

    /**
     * Function: Set Resolution engine
     */

     setResolutionEngine(selected: string) {
      this.setState(
        {
          resolution_engine: selected
        }
      );

    }

    /**
     * Function: Set root directory where to place overlays and where to find .thoth.yaml
     */

     setRootDirectoryPath(event: React.ChangeEvent<HTMLInputElement>) {

      var root_directory = event.target.value

      // TODO: Check if Path exists!

      this.setState(
        {
          root_directory: root_directory
        }
      );

    }

    /**
     * Function: Set Kernel name to be created and assigned to notebook
     */

    setKernelName(event: React.ChangeEvent<HTMLInputElement>) {

      var kernel_name = event.target.value

      if ( event.target.value == "python3" ) {
        console.warn('kernel_name python3 cannot be used assigning default one')
        var kernel_name = "jupyterlab-requirements"
      }

      if ( event.target.value.match(":") ) {
        console.warn('kernel_name cannot contain `:` due to configurations limits.')
        var kernel_name = event.target.value.replace(":", "-")
      }

      this.setState(
        {
          kernel_name: kernel_name
        }
      );

    }

    /**
     * Function: Set timeout for thoth resolution engine
     */

     setTimeout(event: React.ChangeEvent<HTMLInputElement>) {

      var thoth_timeout = Number(event.target.value)

      if ( Number(event.target.value) > 300 ) {
        console.warn('timeout for thoth resolution engine cannot be set more than 300 seconds due to constraint on server side.')
        var thoth_timeout: number = 300
      }

      this.setState(
        {
          thoth_timeout: thoth_timeout
        }
      );

    }

    /**
     * Function: Add new empty row (Only one can be added at the time)
     */

    addNewRow() {

      const packages = this.state.packages

      _.set(packages, "", "")
      console.debug("added package", packages)

      this.changeUIstate(
        "editing",
        packages,
        this.state.loaded_packages,
        this.state.installed_packages,
        this.state.deleted_packages,
        this.state.requirements,
        this.state.kernel_name,
        this.state.thoth_config
      )
    }

    /**
     * Function: Edit added row
     */

    editRow(package_name: string) {

      const packages = this.state.packages
      const loaded_packages = this.state.loaded_packages
      const installed_packages = this.state.installed_packages

      _.unset(packages, package_name)
      _.unset(loaded_packages, package_name)
      _.unset(installed_packages, package_name)
      _.set(packages, "", "*")

      console.debug("After editing (current)", packages)

      this.changeUIstate(
        "editing",
        packages,
        loaded_packages,
        installed_packages,
        this.state.deleted_packages,
        this.state.requirements,
        this.state.kernel_name,
        this.state.thoth_config
      )

    }

    /**
     * Function: Edit saved row
     */

    editSavedRow(package_name: string, package_version: string) {

      const loaded_packages = this.state.loaded_packages
      const packages = this.state.packages
      const installed_packages = this.state.installed_packages

      _.unset(packages, package_name)
      _.unset(loaded_packages, package_name)
      _.unset(installed_packages, package_name)
      _.set(packages, "", "*")

      console.debug("After editing (initial)", loaded_packages)
      console.debug("After editing (current)", packages)

      this.changeUIstate(
        "editing",
        packages,
        loaded_packages,
        installed_packages,
        this.state.deleted_packages,
        this.state.requirements,
        this.state.kernel_name,
        this.state.thoth_config
      )

    }

    /**
     * Function: Delete row not saved
     */

    deleteRow(package_name: string) {

      const packages = this.state.packages

      const deleted_packages = {}

      const version_deleted = _.get(packages, package_name)
      _.unset(packages, package_name)

      console.debug("After deleting", packages)

      _.set(deleted_packages, package_name, version_deleted)

      console.debug("Deleted", deleted_packages)

      this.changeUIstate(
        "editing",
        packages,
        this.state.loaded_packages,
        this.state.installed_packages,
        deleted_packages,
        this.state.requirements,
        this.state.kernel_name,
        this.state.thoth_config
      )

    }

    /**
     * Function: Delete row saved
     */

    deleteSavedRow(package_name: string) {

      const saved_packages = this.state.loaded_packages

      const version_deleted = _.get(saved_packages, package_name)
      _.unset(saved_packages, package_name)

      console.debug("After deleting saved", saved_packages)

      const deleted_packages = {}

      _.set(deleted_packages, package_name, version_deleted)

      console.debug("Deleted", deleted_packages)

      this.changeUIstate(
        "editing",
        this.state.packages,
        saved_packages,
        this.state.installed_packages,
        deleted_packages,
        this.state.requirements,
        this.state.kernel_name,
        this.state.thoth_config
      )
    }

    /**
     * Function: Store row when user requests it
     */

    storeRow(package_name: string, package_version: string) {

      let packages = this.state.packages

      _.set(packages, package_name, package_version)
      const new_dict: { [ name: string ]: string } = {}

      _.forIn(packages, function(value, key) {
        console.debug(key + ' goes ' + value);

        if ( key != "" ) {
          _.set(new_dict, key, value)
        }
      })

      console.debug("new packages", new_dict)

      this.changeUIstate(
        "editing",
        new_dict,
        this.state.loaded_packages,
        this.state.installed_packages,
        this.state.deleted_packages,
        this.state.requirements,
        this.state.kernel_name,
        this.state.thoth_config
      )

    }

    /**
     * Function: Save button to store every input in notebook
     */

    async onSave() {

      var packages_parsed = await _parse_packages_from_state(
        this.state.loaded_packages,
        this.state.packages
      )

      var deleted_case = await _handle_deleted_packages_case(
        this.state.deleted_packages,
        _.get(packages_parsed, "total_packages"),
        this.props.panel,
        this.state,
        _.get(packages_parsed, "new_packages")
      )

      if ( _.get(deleted_case, "action_required") == "relock" ) {
        // Go to saved state, so user can click install button
        var ui_state = this.state
        _.set(ui_state, "status", "saved")
        await this.setNewState(ui_state);
        return
      }

      if ( _.get(deleted_case, "action_required") == "go_to_state" ) {
        await this.setNewState( _.get(deleted_case, "new_state" ) );
        return
      }

      var new_state = await _handle_total_packages_case(
        _.get(packages_parsed, "total_packages"),
        this.props.panel,
        this.state
      )

      await this.setNewState(new_state);

      let warnings = await this.verifyPackages()
      this.setState({warnings: warnings})

      return
    }

    async install() {

      var ui_state = this.state

      try {
          // Create new virtual environment and install dependencies using selected dependency manager (micropipenv by default)
          const install_message = await install_packages(
            this.state.kernel_name,
            this.state.resolution_engine
          );
          console.debug("Install message", install_message);

          _.set(ui_state, "status", "setting_kernel" )
          _.set(ui_state, "packages", {} )
          await this.setNewState(ui_state);
          return

      } catch ( error ) {

        console.debug("Error installing requirements", error)
        _.set(ui_state, "status", "failed")
        _.set(ui_state, "error_msg", "Error install dependencies in the new virtual environment, please contact Thoth team.")
        await this.setNewState(ui_state);
        return
      }
    }

    async setKernel() {

      var ui_state = this.state

      try {
          // Add new virtualenv to jupyter kernel so that it can be assigned to notebook.
          const message = await create_new_kernel( this.state.kernel_name );
          console.debug("Kernel message", message);

          _.set(ui_state, "status", "ready" )
          _.set(ui_state, "packages", {} )
          _.set(ui_state, "installed_packages", ui_state.loaded_packages )
          await this.setNewState(ui_state);
          return

        } catch ( error ) {

          console.debug("Error creating jupyter kernel", error)

          _.set(ui_state, "status", "failed")
          _.set(ui_state, "error_msg", "Error setting new environment in a jupyter kernel, please contact Thoth team: ")
          await this.setNewState(ui_state);
          return

        }
    }

    async lock() {

      var current_state = this.state
      console.log("before locking", current_state)

      if ( current_state.resolution_engine == "thoth" ) {
          await this.lock_using_thoth()
      }

      else if ( current_state.resolution_engine == "pipenv" ) {
        await this.lock_using_pipenv()
      }

      else {
          console.error("This resolution engine is not supported: ", current_state.resolution_engine)
      }

    }

    async lock_using_thoth() {

      // Prepare inputs for advise
      var ui_state = this.state

      _.set(ui_state, "status", "locking_requirements")
      await this.setNewState(ui_state);

      const notebook_content = await take_notebook_content( this.props.panel )

      var thoth_config: ThothConfig = await create_config( this.state.kernel_name );

      if ( this.props.loaded_resolution_engine == "pipenv" ) {
        console.debug("thoth previously failed!")

        const result = await _handle_thoth_config(
          this.props.loaded_config_file,
          this.state.kernel_name,
          ui_state.thoth_config,
          ui_state.recommendation_type,
          "thoth"
        )
        var thoth_config: ThothConfig = _.get(result, "thoth_config")
      }

      // Run adviser to lock dependencies
      try {

        var advise: Advise | undefined = await lock_requirements_with_thoth(
          this.state.kernel_name,
          this.state.thoth_timeout,
          this.state.thoth_force,
          this.state.thoth_debug,
          this.state.python_version,
          this.state.os_name,
          this.state.os_version,
          this.state.recommendation_type,
          this.state.labels,
          notebook_content,
          JSON.stringify(thoth_config),
          JSON.stringify(this.state.requirements)
        );
        console.debug("Advise received", advise);

      } catch ( error ) {

        // Error in the code
        console.debug("Error locking requirements with Thoth", error)
        _.set(ui_state, "status", "failed_re_thoth")
        _.set(ui_state, "thoth_resolution_error_msg", "Error trying to lock dependencies with Thoth" )
        _.set(
          ui_state,
          "error_msg",
          error
        )
        await this.setNewState(ui_state);
        return
      }

      console.log(advise)

      // Error in the resolution process
      if ( advise == undefined ) {
        var error_msg = "Thoth resolution engine was not able to lock dependencies, try Pipenv or please contact Thoth team: "
        _.set(ui_state, "status", "failed_re_thoth")
        _.set(
          ui_state,
          "error_msg",
          error_msg
        )
        await this.setNewState(ui_state);
        return
      }

      if ( advise.error != true && advise.error != false && advise.error ) {
          var error_msg = "Check error and try again."
          console.log("Thoth resolution engine error:", advise.error)
          _.set(ui_state, "thoth_resolution_error_msg", advise.error )
          _.set(ui_state, "status", "failed_re_thoth")
          _.set(
            ui_state,
            "error_msg",
            error_msg
          )
          await this.setNewState(ui_state);
          return
      }

      if ( advise.error == true ) {
          var error_msg = "Thoth resolution engine was not able to lock dependencies, try Pipenv or please contact Thoth team: "
          console.log("Thoth resolution engine error:", advise.error_msg)
          _.set(ui_state, "thoth_resolution_error_msg", advise.error_msg )
        _.set(ui_state, "status", "failed_re_thoth")
        _.set(
          ui_state,
          "error_msg",
          error_msg
        )
        await this.setNewState(ui_state);
        return
      }

      // Resolution process succeeded, saving all data.
      try {

        await set_notebook_metadata(
          this.props.panel,
          "thoth",
          advise.requirements,
          advise.requirements_lock,
          this.state.thoth_config,
          advise.thoth_analysis_id
        )

      } catch ( error ) {
        console.debug("Error updating notebook metadata", error)
      }

      console.log(advise)
      try {
        await store_dependencies_on_disk(
          this.state.kernel_name,
          advise.requirements,
          advise.requirements_lock,
          'overlays',
          this.state.root_directory
        )
      } catch ( error ) {

        console.debug("Error storing dependencies in overlays", error)

      }

      try {
        await update_thoth_config_on_disk(
          this.state.thoth_config.runtime_environments[0],
          true,
          this.state.root_directory
          )
        } catch ( error ) {
        console.debug("Error updating thoth config on disk", error)
      }

      _.set(ui_state, "status", "installing_requirements" )
      _.set(ui_state, "packages", {} )
      _.set(ui_state, "deleted_packages", {} )
      _.set(ui_state, "requirements", advise.requirements )
      _.set(ui_state, "resolution_engine", "thoth" )

      await this.setNewState(ui_state);
      return
    }


    async lock_using_pipenv () {

      var ui_state = this.state

      _.set(ui_state, "status", "locking_requirements_using_pipenv")
      await this.setNewState(ui_state);

      const notebookMetadataRequirements = this.state.requirements;
      console.debug("Requirements for pipenv", JSON.stringify(notebookMetadataRequirements));

      // Run Pipenv to lock dependencies
      try {

        var result = await lock_requirements_with_pipenv(
          this.state.kernel_name,
          JSON.stringify(notebookMetadataRequirements)
        )
        console.debug("Result received", result);

      } catch ( error ) {

        console.log("Error locking requirements with pipenv", error)

        // Error in JH on cluster
        if ( error.message == "Gateway error while locking dependencies with pipenv.") {
            INotification.warning("Task was cancelled due to gateway error, try again please.")
            _.set(ui_state, "status", "failed")
            _.set(ui_state, "error_msg", "Gateway error, please try again!")
            await this.setNewState(ui_state);
            return
        }

        // Error in code
        _.set(ui_state, "status", "failed_re_pipenv")
        _.set(ui_state, "error_msg", "Error locking requirements, check logs and please contact Thoth team: ")
        await this.setNewState(ui_state);
        return
      }

      // Error in Pipenv resolution process
      if ( result == undefined || result.error == true ) {

        var error_msg = `Pipenv resolution engine was not able to lock dependencies, try Thoth or please contact Thoth team: `

        if ( result != undefined ) {
          console.debug("Pipenv resolution engine error:", result.error_msg)
          _.set(ui_state, "pipenv_resolution_error_msg", result.error_msg.toString())
        }
        _.set(ui_state, "status", "failed_re_pipenv")
        _.set(
          ui_state,
          "error_msg",
          error_msg
        )
        await this.setNewState(ui_state);
        return
      }

      // Resolution process succeeded, saving all data.
      try {
          await set_notebook_metadata(
            this.props.panel,
            "pipenv",
            notebookMetadataRequirements,
            result.requirements_lock
          )
          await delete_key_from_notebook_metadata( this.props.panel, "thoth_analysis_id" )

      } catch ( error ) {
        console.debug("Error storing metadata in notebook", error)
      }

      try {
        await store_dependencies_on_disk(
          this.state.kernel_name,
          notebookMetadataRequirements,
          result.requirements_lock,
          'overlays',
          this.state.root_directory
        )

      } catch ( error ) {
        console.debug("Error storing dependencies in overlays", error)
      }

      _.set(ui_state, "status", "installing_requirements" )
      _.set(ui_state, "packages", {} )
      _.set(ui_state, "deleted_packages", {} )
      _.set(ui_state, "requirements", notebookMetadataRequirements )
      _.set(ui_state, "resolution_engine", "pipenv" )

      await this.setNewState(ui_state);
      return
    }

    async onStart() {

      // const script = `
      // print("This is jupyterlab-requirements")
      // `
      // await this.execute_code_in_kernel(script)

      const root_directory = await discover_root_directory()

      var ui_on_start_state = await parse_inputs_from_metadata(
        this.state,
        this.props.panel,
        this.props.loaded_config_file,
        this.props.loaded_requirements,
        this.props.loaded_requirements_lock,
        this.props.loaded_resolution_engine
      )

      if ( _.has(ui_on_start_state.thoth_config, "runtime_environments") ) {
        _.set(ui_on_start_state, "os_name", ui_on_start_state.thoth_config.runtime_environments[0].operating_system.name)
        _.set(ui_on_start_state, "os_version", ui_on_start_state.thoth_config.runtime_environments[0].operating_system.version)
        _.set(ui_on_start_state, "python_version", ui_on_start_state.thoth_config.runtime_environments[0].python_version)
      }

      _.set(ui_on_start_state, "root_directory", root_directory)

      await this.setNewState(ui_on_start_state);

      const warnings = await this.verifyPackages()
      this.setState({warnings: warnings})

      return
    }

    async verifyPyPI(package_name: string) {
      const url = `https://pypi.org/pypi/${package_name}/json`;
      return axios
        .get(url)
        .then(({ data }) => {
          return true
        })
        .catch(() => {
          return false
        })
    }

    async verifyPackages() {
      const pkgs: {
        unknown: Array<string>;
        inPyPI: Array<string>;
      } = {
        unknown: [],
        inPyPI: []
      }
      for (const pkg of Object.keys(this.state.requirements.packages)) {
        await axios
          .get("https://khemenu.thoth-station.ninja/api/v1/python/package/versions", {
            params: {
              name: pkg,
              page: 0,
              per_page: 1
            }
          })
          .then(async ({ data }) => {
            if (data.versions.length === 0) {
              const isInPyPI = await this.verifyPyPI(pkg);
              if(isInPyPI) {
                pkgs.inPyPI.push(pkg)
              }
              else {
                pkgs.unknown.push(pkg)
              }
            }
          })
          .catch(async () => {
            const isInPyPI = await this.verifyPyPI(pkg);
            if(isInPyPI) {
              pkgs.inPyPI.push(pkg)
            }
            else {
              pkgs.unknown.push(pkg)
            }
          });
      }

      return pkgs;
    }

    render(): React.ReactNode {
      let dependencyManagementform = <div>
                                        <DependencyManagementForm
                                          loaded_packages={this.state.loaded_packages}
                                          installed_packages={this.state.installed_packages}
                                          packages={this.state.packages}
                                          editRow={this.editRow}
                                          storeRow={this.storeRow}
                                          deleteRow={this.deleteRow}
                                          editSavedRow={this.editSavedRow}
                                          deleteSavedRow={this.deleteSavedRow}
                                        />
                                      </div>

      let addPlusInstallContainers = <div>
                                        <div className={CONTAINER_BUTTON}>
                                          <div className={CONTAINER_BUTTON_CENTRE}>
                                          <DependencyManagementNewPackageButton addNewRow={this.addNewRow} />
                                          </div>
                                        </div>
                                        <div className={CONTAINER_BUTTON}>
                                          <div className={CONTAINER_BUTTON_CENTRE}>
                                            <DependencyManagementInstallButton
                                            install={this.lock} />
                                          </div>
                                        </div>
                                      </div>

      let addPlusSaveContainers = <div>
                                      <div className={CONTAINER_BUTTON}>
                                        <div className={CONTAINER_BUTTON_CENTRE}>
                                        <DependencyManagementNewPackageButton addNewRow={this.addNewRow} />
                                        </div>
                                      </div>
                                      <div className={CONTAINER_BUTTON}>
                                        <div className={CONTAINER_BUTTON_CENTRE}>
                                          <DependencyManagementSaveButton
                                            onSave={this.onSave}/>
                                        </div>
                                      </div>
                                    </div>

      let resolutionEngineInput = <StylizedDropdown label="Resolution Engine"
                                                    value={this.state.resolution_engine}
                                                    options={["thoth", "pipenv"]}
                                                    onChange={this.setResolutionEngine}
                                                    isRequired={true}
                                                    style={{gridColumn: "span 4"}} />

      let kernelNameInput = <StylizedTextInput label="Kernel Name"
                                               value={this.state.kernel_name}
                                               onChange={this.setKernelName}
                                               style={{gridColumn: "span 4"}} />

      let pathRootProjectInput =  <StylizedTextInput label="Path root project"
                                                     value={this.state.root_directory}
                                                     onChange={this.setRootDirectoryPath}
                                                     style={{gridColumn: "span 4"}} />

      let recommendationTypeInput = <StylizedDropdown label="Thoth Recommendation type"
                                                      value={this.state.recommendation_type}
                                                      options={["latest", "performance", "security", "stable"]}
                                                      onChange={this.changeRecommendationType}
                                                      style={{gridColumn: "span 2"}}/>

      let baseImageInput;
      if ( this.state.thoth_config ) {
          if ( this.state.thoth_config.runtime_environments[0].base_image ) {
            baseImageInput = <StylizedTextInput label="Thoth base image"
                                                value={this.state.thoth_config.runtime_environments[0].base_image}
                                                onChange={this.setBaseImage}
                                                style={{gridColumn: "span 2"}}/>
          }
      }

      let timeoutInput = <StylizedTextInput label="Thoth timeout"
                                            value={this.state.thoth_timeout}
                                            onChange={this.setTimeout}
                                            suffix="seconds"
                                            helperText="0 - 300 seconds"
                                            style={{gridColumn: "span 2"}} />

      let pythonVersionInput = <StylizedTextInput label="Thoth Python Version"
                                                  value={this.state.python_version}
                                                  onChange={this.setPythonVersion}
                                                  style={{gridColumn: "span 2"}}/>

      let OSNameInput = <StylizedTextInput label="Thoth Operating System Name"
                                           value={this.state.os_name}
                                           onChange={this.setOSName}
                                           style={{gridColumn: "span 2"}}/>

      let OSVersionInput = <StylizedTextInput label="Thoth Operating System Version"
                                              value={this.state.os_version}
                                              onChange={this.setOSVersion}
                                              style={{gridColumn: "span 2"}}/>

      let forceInput =  <div className={INPUT_OPTIONS} style={{gridColumn: "span 1"}}>
                          <label>
                            Thoth force
                            <input type="checkbox"
                                   title="Thoth force parameter."
                                   name="thoth_force"
                                   id="thoth_force"
                                   onChange={this.setForceParameter}
                                   checked={this.state.thoth_force} />
                            </label>
                          <br />
                        </div>

      let debugInput =  <div className={INPUT_OPTIONS} style={{gridColumn: "span 1"}}>
                          <label>
                            Thoth debug
                            <input type="checkbox"
                                   title="Thoth debug parameter."
                                   name="thoth_debug"
                                   id="thoth_debug"
                                   onChange={this.setDebugParameter}
                                   checked={this.state.thoth_debug} />
                          </label>
                          <br />
                        </div>

      let labelsInput =  <StylizedTextInput label="Labels"
                                            value={this.state.labels}
                                            onChange={this.setThothLabels}
                                            helperText="comma separated labels"
                                            style={{gridColumn: "span 4"}}/>

      let unknownWarnings = this.state.warnings.unknown.map(pkg => {
        return (
          <StylizedBanner key={pkg}
                          label={<div>The package <b>{pkg}</b> does not exist on any index monitored by Thoth. If this is a mistake, open an issue with the Thoth team on GitHub.</div>}
                          link="https://github.com/thoth-station/support/issues/new?assignees=&labels=bug%2Ctriage&template=package_request.yaml"
                          linkLabel="open issue"
                          severity="error"
          />
        )
      })

      let PyPIWarnings = this.state.warnings.inPyPI.map(pkg => {
        return (
          <StylizedBanner key={pkg}
                          label={<div>The package <b>{pkg}</b> is not in Thoth's knowledge graph. Open a GitHub issue to request it be added.</div>}
                          link="https://github.com/thoth-station/support/issues/new?assignees=&labels=bug%2Ctriage&template=package_request.yaml"
                          linkLabel="open issue"
                          severity="warning"
          />
        )
      })


      if ( this.state.resolution_engine == "thoth" ) {
        var optionsForm = <div>
                            <section>
                              <h2>OPTIONS</h2>
                            </section>
                            {unknownWarnings}
                            {PyPIWarnings}
                            <div className={INPUT_FORM_BOX}>
                              <form className={FORM_GRID}>
                                {resolutionEngineInput}
                                {kernelNameInput}
                                {pathRootProjectInput}
                                <div style={{gridColumn: "span 2"}}>
                                  <p>Python Settings</p>
                                  <div className="form-stack">
                                    {recommendationTypeInput}
                                    {pythonVersionInput}
                                  </div>
                                </div>

                                <div style={{gridColumn: "span 2"}}>
                                  <p>Operating System Settings</p>
                                  <div className="form-stack">
                                    {OSNameInput}
                                    {OSVersionInput}
                                  </div>
                                </div>

                                <div style={{gridColumn: "span 4"}}>
                                  <p>Thoth Advise Settings</p>
                                  <div className="form-grid">
                                    {timeoutInput}
                                    {debugInput}
                                    {forceInput}
                                    {labelsInput}
                                    {baseImageInput}
                                  </div>
                                </div>
                              </form>
                            </div>
                          </div>

      }

      else {

        var optionsForm = <div>
                          <section>
                            <h2>OPTIONS</h2>
                          </section>
                          {unknownWarnings}
                          <div className={INPUT_FORM_BOX}>
                          <form className={FORM_GRID}>
                            {resolutionEngineInput}
                            {kernelNameInput}
                            {pathRootProjectInput}
                          </form>
                          </div>
                        </div>

      }

      var ui_status = this.state.status

      switch(ui_status) {

        case "loading":

          this.onStart()

          return (
            <div>
              Loading...
            </div>
          )

        case "initial":
          return (
            <div>
              <div className={CONTAINER_BUTTON}>
                <div className={CONTAINER_BUTTON_CENTRE}>
                <DependencyManagementNewPackageButton addNewRow={this.addNewRow} />
                </div>
              </div>
              <div>
                <fieldset>
                  <p> No dependencies found! Click New to add package. </p>
                </fieldset>
              </div>

            </div>
          );

        case "no_reqs_to_save":
          return (
            <div>
                {dependencyManagementform}
                {addPlusSaveContainers}
              <div>
                <fieldset>
                  <p> Dependencies missing! Click New to add package. </p>
                </fieldset>
              </div>
            </div>
          );

        case "only_install":
          return (
            <div>
              {dependencyManagementform}
              {addPlusInstallContainers}

              <div>
                <fieldset>
                  <p>Dependencies found in notebook metadata but lock file is missing. </p>
                </fieldset>
              </div>
              {optionsForm}
            </div>
          );

        case "only_install_kernel":
          return (
            <div>
              {dependencyManagementform}
              {addPlusInstallContainers}
              <div>
                <fieldset>
                  <p>Pinned down software stack found in notebook metadata!<br></br>
                  The kernel selected does not match the dependencies found for the notebook. <br></br>
                  Please install them.</p>
                </fieldset>
              </div>
              {optionsForm}
            </div>
          );

        case "only_install_kernel_runenv":
          return (
            <div>
              {dependencyManagementform}
              {addPlusInstallContainers}
              <div>
                <fieldset>
                  <p>Pinned down software stack found in notebook metadata!<br></br>
                  The runtime environment found in the notebook does not match the environment in system. <br></br>
                  Use install button.</p>
                </fieldset>
              </div>
              {optionsForm}
            </div>
          );

        case "only_install_from_imports":

          return (
            <div>
              {dependencyManagementform}
              {addPlusInstallContainers}
              <div>
                <fieldset>
                  <p>No dependencies found in notebook metadata!<br></br>
                  Thoth identified the packages that are required to run this notebook from your code. <br></br>
                  (Names of the packages identified from Thoth database). <br></br>
                  Please use install button to install dependencies identified.</p>
                </fieldset>
              </div>
              {optionsForm}
            </div>
          );

        case "editing":
          return (
            <div>
              {dependencyManagementform}
              {addPlusSaveContainers}
            </div>
          );

        case "saved":
          return (
            <div>
              {dependencyManagementform}
              {addPlusInstallContainers}
              {optionsForm}
            </div>
          );

        case"locking_requirements":
          return (
            <div>
              {dependencyManagementform}
              <fieldset>
                <p>Contacting thoth for advise... please be patient!</p>
              </fieldset>
            </div>
          );

        case "installing_requirements":

          this.install()

          return (
            <div>
              {dependencyManagementform}
              <fieldset>
                <p>Requirements locked and saved!<br></br>
                Installing new requirements...
                </p>
              </fieldset>
            </div>
          );

      case "setting_kernel":

          this.setKernel()

          return (
            <div>
              {dependencyManagementform}
              <fieldset>
                <p>Requirements locked and saved!<br></br>
                Requirements installed!<br></br>
                Setting new kernel for your notebook...
                </p>
              </fieldset>
            </div>
          );


        case "failed_no_reqs":

          return (
            <div>
              <div>
                <button
                  title='Add requirements.'
                  className={OK_BUTTON_CLASS}
                  onClick={() => this.changeUIstate(
                    "loading",
                    this.state.packages,
                    this.state.loaded_packages,
                    this.state.installed_packages,
                    this.state.deleted_packages,
                    this.state.requirements,
                    this.state.kernel_name,
                    this.state.thoth_config,
                  )
                  }
                  >
                  Ok
                </button>
              </div>
              <div>
                <fieldset>
                  <p>No requirements have been added please click add from actions after inserting a package!</p>
                </fieldset>
              </div>
            </div>
        );

        case "locking_requirements_using_pipenv":

          return (
            <div>
              <fieldset>
                <p>Using Pipenv to lock dependencies...</p>
              </fieldset>
            </div>
        );

        case "failed_re_thoth":

          let paragrah_failure = <p>
            Thoth resolution engine failed because of: {this.state.thoth_resolution_error_msg} <br></br> <br></br>
              {this.state.error_msg} <br></br>
          </p>

          return (
            <div>
              <div>
                <div className={CONTAINER_BUTTON}>
                  <div className={CONTAINER_BUTTON_CENTRE}>
                    <button
                      title='Finish.'
                      className={OK_BUTTON_CLASS}
                      onClick={() => this.changeUIstate(
                        "loading",
                        this.state.packages,
                        this.state.loaded_packages,
                        this.state.installed_packages,
                        this.state.deleted_packages,
                        this.state.requirements,
                        this.state.kernel_name,
                        this.state.thoth_config,
                      )
                      }
                      >
                      Ok
                    </button>
                  </div>
                </div>
              </div>
              <div>
                    {paragrah_failure}
              </div>
              <a href={"https://github.com/thoth-station/jupyterlab-requirements/issues/new?assignees=&labels=bug&template=bug_report.md"} target="_blank"> Open Issue </a>
            </div>
        );

        case "failed_re_pipenv":

          let paragrah_failure_pipenv = <p>
              Pipenv resolution engine failed because of: {this.state.pipenv_resolution_error_msg}<br></br> <br></br>
              {this.state.error_msg} <br></br>
          </p>

          return (
            <div>
              <div>
                <div className={CONTAINER_BUTTON}>
                  <div className={CONTAINER_BUTTON_CENTRE}>
                    <button
                      title='Finish.'
                      className={OK_BUTTON_CLASS}
                      onClick={() => this.changeUIstate(
                        "loading",
                        this.state.packages,
                        this.state.loaded_packages,
                        this.state.installed_packages,
                        this.state.deleted_packages,
                        this.state.requirements,
                        this.state.kernel_name,
                        this.state.thoth_config,
                      )
                      }
                      >
                      Ok
                    </button>
                  </div>
                </div>
              </div>
              <div>
                    {paragrah_failure_pipenv}
              </div>
              <a href={"https://github.com/thoth-station/jupyterlab-requirements/issues/new?assignees=&labels=bug&template=bug_report.md"} target="_blank"> Open Issue </a>
            </div>
        );

        case "failed":

          return (
            <div>
              <div>
                <div className={CONTAINER_BUTTON}>
                  <div className={CONTAINER_BUTTON_CENTRE}>
                    <button
                      title='Finish.'
                      className={OK_BUTTON_CLASS}
                      onClick={() => this.changeUIstate(
                        "loading",
                        this.state.packages,
                        this.state.loaded_packages,
                        this.state.installed_packages,
                        this.state.deleted_packages,
                        this.state.requirements,
                        this.state.kernel_name,
                        this.state.thoth_config,
                      )
                      }
                      >
                      Ok
                    </button>
                  </div>
                </div>
              </div>
              <div>
                {this.state.error_msg}
              </div>
              <a href={"https://github.com/thoth-station/jupyterlab-requirements/issues/new?assignees=&labels=bug&template=bug_report.md"} target="_blank"> Open Issue </a>
            </div>
        );

        case "stable":

          return (
            <div>
              {dependencyManagementform}
              <div className={CONTAINER_BUTTON}>
                <div className={CONTAINER_BUTTON_CENTRE}>
                <DependencyManagementNewPackageButton addNewRow={this.addNewRow} />
                </div>
              </div>
              <div>
                <fieldset>
                  <p> Everything installed and ready to use!</p>
                </fieldset>
              </div>
            </div>
          );

        case "stable_no_runenv":
            // TODO: Provide relock button option if the resolution engine is different from thoth
            return (
              <div>
              {dependencyManagementform}
              <div className={CONTAINER_BUTTON}>
                <div className={CONTAINER_BUTTON_CENTRE}>
                <DependencyManagementNewPackageButton addNewRow={this.addNewRow} />
                </div>
              </div>
              <div>
                <fieldset>
                <p>Everything installed and ready to use!<br></br>
                    Keep in mind no runtime environment is present in the notebook metadata. <br></br>
                    Therefore your software stack might not be optimized for your environment. <br></br>
                    </p>
                </fieldset>
              </div>
              {addPlusInstallContainers}
              {optionsForm}
            </div>
            );

        case "ready":

          // Check if kernel name is already assigned to notebook and if yes, do nothing
          const current_kernel = get_kernel_name( this.props.panel, true )
          if ( current_kernel == this.state.kernel_name ) {
            INotification.info("kernel name to be assigned " + this.state.kernel_name + " already set for the current notebook (" + current_kernel + "). Kernel won't be restarted.")
          }
          else {
            this.props.panel.sessionContext.session.changeKernel({"name": this.state.kernel_name})
          }

          return (
            <div>
              {dependencyManagementform}
              <div>
                <div className={CONTAINER_BUTTON}>
                    <div className={CONTAINER_BUTTON_CENTRE}>
                      <button
                        title='Reload Page and assign kernel.'
                        className={OK_BUTTON_CLASS}
                        onClick={() => this.changeUIstate(
                          "stable",
                          this.state.packages,
                          this.state.loaded_packages,
                          this.state.installed_packages,
                          this.state.deleted_packages,
                          this.state.requirements,
                          this.state.kernel_name,
                          this.state.thoth_config,
                        )
                        }
                        >
                        Ok
                      </button>
                    </div>
                </div>
              </div>
              <div>
                  <fieldset>
                    <p>Requirements locked and saved!<br></br>
                    Requirements installed!<br></br>
                    New kernel created!<br></br>
                    Click ok to start working on your notebook.<br></br>
                    </p>
                  </fieldset>
              </div>
            </div>
        );

    }
  }

  private _model: KernelModel;
}
