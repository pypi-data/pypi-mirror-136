# Copyright 2017 Biomedical Imaging Group Rotterdam, Departments of
# Medical Informatics and Radiology, Erasmus MC, Rotterdam, The Netherlands
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
import os
import textwrap
import yaml
from pathlib import Path

from flask_security import SQLAlchemyUserDatastore, current_user
from flask_security.utils import hash_password

from .. import models
from .. import exceptions


def load_config_file(app, file_path, silent=False):
    file_path = str(file_path)

    with app.app_context():
        db = models.db

        user_datastore = SQLAlchemyUserDatastore(db, models.User, models.Role)
        if not os.path.isfile(file_path):
            db.session.rollback()
            raise ValueError(f"The file ({file_path}) does not exist")

        with open(file_path) as fh:
            config = yaml.safe_load(fh)

        if 'roles' in config:
            if not silent:
                print("\n Adding Roles:")
            roles = {}
            for role in config["roles"]:
                if models.Role.query.filter(models.Role.name == role['name']).count() == 0:
                    roles[role['name']] = user_datastore.create_role(**role)
                    if not silent:
                        print(f"{roles[role['name']]} {role}")
                else:
                    print(f"[WARNING] Skipping Role {role['name']}, already exists!")
            db.session.commit()

        if 'users' in config:
            if not silent:
                print("\nAdding users:")
            for user in config['users']:
                # Make sure user is confirmed
                user['confirmed_at'] = datetime.datetime.now()
                if models.User.query.filter((models.User.username == user['username']) | (models.User.email == user['email'])).count() == 0:
                    user['password'] = hash_password(user['password'])
                    db_user = user_datastore.create_user(**user)
                    if not silent:
                        print(f"Adding {db_user}")
                else:
                    print(f"[WARNING] Skipping User {user['username']} / {user['email']}, user and/or username already used!")
            db.session.commit()

        print("\nAdding external_systems:")
        for external_system in config.get('external_systems', []):
            if models.ExternalSystem.query.filter(models.ExternalSystem.system_name == external_system['system_name']).count() == 0:
                db.session.add(models.ExternalSystem(system_name=external_system['system_name'], url=external_system['url']))
                if not silent:
                    print(f"Adding {external_system['system_name']}")
            else:
                print(f"[WARNING] Skipping ExternalSystem {external_system['system_name']}, already exists!")

        print("\nAdding scantypes:")
        for scan_type in config.get('scantypes', []):
            if models.Scantype.query.filter(models.Scantype.protocol == scan_type['protocol']).count() == 0:
                db.session.add(models.Scantype(modality=scan_type['modality'], protocol=scan_type['protocol']))
                if not silent:
                    print(f"Adding {scan_type['modality']} {scan_type['protocol']}")
            else:
                print(f"[WARNING] Skipping ScanType {scan_type['protocol']}, already exists!")

        if not silent:
            print("\nCommitting to the database ...")
        db.session.commit()
        if not silent:
            print("[ DONE ]")


def get_object_from_arg(id, model, model_name=None, skip_id=False, allow_none=False, filters=None):
    # Set initial return data to None already
    data = None

    # Check if id is already a valid instance of model
    if isinstance(id, model):
        return id

    if id is not None:
        # If we have a URI/path we just want the last part
        if isinstance(id, str) and '/' in id:
            id = id.rsplit('/', 1)[1]

        # For id try to cast to an int
        if not skip_id:
            try:
                id = int(id)
            except (TypeError, ValueError) as e:
                pass

        # Create base query
        if isinstance(id, int):
            query = model.query.filter(model.id == id)
        elif model_name is not None:
            query = model.query.filter(model_name == id)
        else:
            query = None
        
        # If there is a query, add filters and run query
        if query is not None:
            if filters is not None:
                for key, value in filters.items():
                    query = query.filter(key == value)
                
            data = query.one_or_none()
        
    # Check if there is data or None is allowed
    if data is None and not allow_none:
        raise exceptions.CouldNotFindResourceError(id, model)

    return data


def initialize_workflow(workflow, app, verbose=False, force=True, upgrade=False):
    if isinstance(workflow, (str, Path)):
        try:
            with open(workflow) as fh:
                workflow_definition = yaml.safe_load(fh)
        except IOError as experiment:
            print("IOError: {}".format(experiment))
            print("Please specify a valid YAML file.")
            return
    else:
        workflow_definition = workflow

    if verbose:
        def do_print(message):
            print(message)
    else:
        def do_print(message):
            pass

    with app.app_context():
        db = models.db

        try:
            workflow_label = workflow_definition['label']
        except KeyError:
            print(f'[ERROR] Workflow definition should contain a label to manage multiple version!')
            return

        workflow = models.Workflow.query.filter(models.Workflow.label == workflow_label).one_or_none()

        if workflow is None:
            workflow = models.Workflow(label=workflow_label)

            do_print("\n * Importing states:")
            states = dict()
            for state in workflow_definition['states']:
                callback = state['callback']

                # Allow callback to be defined as nested JSON rather than a string containing escaped JSON
                if not isinstance(callback, str) and callback is not None:
                    callback = yaml.safe_dump(callback)

                states[state['label']] = models.State(label=state['label'],
                                                      lifespan=state['lifespan'],
                                                      callback=callback,
                                                      freetext=state['freetext'],
                                                      workflow=workflow)
                db.session.add(states[state['label']])
                do_print("\t - {}".format(state['label']))

            do_print("\n * Importing transitions:")
            for transition in workflow_definition['transitions']:
                #TODO add conditions
                db.session.add(models.Transition(source_state=states[transition['source']],
                                                 destination_state=states[transition['destination']]))
                do_print("\t - {} -> {}".format(states[transition['source']],
                                                states[transition['destination']]))
        else:
            if upgrade:
                upgrade_result = upgrade_workflow(workflow=workflow,
                                                  workflow_definition=workflow_definition,
                                                  db=db,
                                                  verbose=verbose)

                if not upgrade_result:
                    print("[ERROR] Cannot perform workflow upgrade")
                    return
            else:
                print(f'[ERROR] Workflow with label {workflow_label} already exists, use the upgrade flag to upgrade!')
                return

        if 'external_systems' in workflow_definition:
            print("[WARNING] External systems are no longer defined as part of a workflow, "
                  "but as part of the config! Ignoring external_systems section")

        if 'scantypes' in workflow_definition:
            print("[WARNING] Scantypes are no longer defined as part of a workflow, "
                  "but as part of the config! Ignoring scantypes section")

        doit = False
        if not force:
            doit = input("Are you sure you want to commit this to '{}' [yes/no]: ".format(app.config['SQLALCHEMY_DATABASE_URI'].rsplit('/', 1)[1])) == 'yes'

        if doit or force:
            db.session.commit()
            do_print("\n * Committed to the database.")
        else:
            db.session.rollback()
            do_print("\n * Cancelled the initialisation of the workflows.")


def upgrade_workflow(workflow, workflow_definition, db, verbose: bool = False):
    # print(f"Upgrading workflow {workflow_label} with new data")
    new_states = []
    edit_states = []
    old_states = {x.label: x for x in workflow.states}
    old_transitions = models.Transition.query.filter(
        models.Transition.source_state.has(models.State.workflow == workflow) |
        models.Transition.destination_state.has(models.State.workflow == workflow)
    ).all()

    new_transitions = []
    edit_transitions = []
    old_transitions = {(x.source_state.label, x.destination_state.label): x for x in old_transitions}

    # Check what to do with states
    for new_state in workflow_definition['states']:
        old_state = old_states.pop(new_state['label'], None)
        if old_state is not None:
            edit_states.append(new_state)
        else:
            new_states.append(new_state)

    # Check what to do with transitions
    for new_transition in workflow_definition['transitions']:
        old_transition = old_transitions.pop((new_transition['source'], new_transition['destination']), None)

        if old_transition is not None:
            edit_transitions.append(new_transition)
        else:
            new_transitions.append(new_transition)

    old_transitions = list(old_transitions.values())
    old_states = list(old_states.values())

    safe_delete = True
    # Check if transitions can be deleted
    for old_transition in old_transitions:
        action_count = len(old_transition.actions)
        if action_count > 0:
            print(f"[WARNING] Transition {old_transition} should be deleted but"
                  f" cannot be due to related {action_count} actions")
            safe_delete = False

    # Check if states can be deleted
    for old_state in old_states:
        action_count = models.Action.query.filter(models.Action.transition.has(
            (models.Transition.source_state == old_state) |
            (models.Transition.destination_state == old_state)
        )).count()
        if action_count > 0:
            print(f"[WARNING] State {old_state.label} should be deleted but"
                  f" cannot be due to {action_count} related actions")
            safe_delete = False

        for old_transition in old_state.transition_sources:
            if old_transition not in old_transitions:
                print(f"[WARNING] State {old_state.label} should be deleted but "
                      f"cannot because transition {old_transition} is not to be "
                      f"deleted!")
                safe_delete = False

        for old_transition in old_state.transition_destinations:
            if old_transition not in old_transitions:
                print(f"[WARNING] State {old_state.label} should be deleted but "
                      f"cannot because transition {old_transition} is not to be "
                      f"deleted!")
                safe_delete = False

    if not safe_delete:
        print(f"[ERROR] Not all resources that should be deleted can be deleted, aborting!")
        return False

    print(f"[INFO] Ready to start applying changes")
    print("\n * Importing new states:")
    states = {}
    for state in new_states:
        callback = state['callback']

        # Allow callback to be defined as nested JSON rather than a string containing escaped JSON
        if not isinstance(callback, str) and callback is not None:
            callback = yaml.safe_dump(callback)

        state_obj = models.State(label=state['label'],
                                 lifespan=state['lifespan'],
                                 callback=callback,
                                 freetext=state['freetext'],
                                 workflow=workflow)
        states[state['label']] = state_obj
        db.session.add(state_obj)
        print("\t - {}".format(state['label']))

    print("\n * Updating existing states:")
    for state in edit_states:
        callback = state['callback']

        # Allow callback to be defined as nested YAML/JSON rather than a string containing escaped YAML/JSON
        if callback is None:
            callback_data = None
            callback_str = None
        elif not isinstance(callback, str):
            callback_str = yaml.safe_dump(callback)
            callback_data = callback
        else:
            callback_str = callback
            callback_data = yaml.safe_load(callback)

        # Get current state
        current_state = models.State.query.filter(
            (models.State.label == state['label']) &
            (models.State.workflow == workflow)
        ).one()

        if current_state.callback is None:
            current_callback_data = None
        else:
            current_callback_data = yaml.safe_load(current_state.callback)

        # Update fields
        changes = {}
        if current_state.lifespan != state['lifespan']:
            changes['lifespan'] = state['lifespan']
            current_state.lifespan = state['lifespan']
        if current_callback_data != callback_data:
            changes['callback'] = "\n" + textwrap.indent(f"FROM:\n{current_state.callback}\nTO:\n{callback_str}", "\t\t | ")
            current_state.callback = callback_str
        if current_state.lifespan != state['lifespan']:
            changes['freetext'] = state['freetext']
            current_state.freetext = state['freetext']

        states[state['label']] = current_state

        if changes:
            print(f"\t - {state['label']}")
            for key, value in changes.items():
                print(f"\t\t - set {key}={value}")

    print("\n * Deleting old states:")
    for state in old_states:
        db.session.delete(state)
        print(f"\t - {state.label}")

    print("\n * Importing new transitions:")
    for transition in new_transitions:
        db.session.add(models.Transition(source_state=states[transition['source']],
                                         destination_state=states[transition['destination']]))
        print(f"\t - {transition['source']} -> {transition['destination']}")

    print("\n * Keeping existing transitions transitions:")
    for transition in edit_transitions:
        print(f"\t - {transition['source']} -> {transition['destination']}")

    print("\n * Deleting old transitions:")
    for transition in old_transitions:
        db.session.delete(transition)
        print(f"\t - {transition.source_state.label} -> {transition.destination_state.label}")

    return True


def has_permission_any(*args):
    return any(current_user.has_permission(perm) for perm in args)


def has_permission_all(*args):
    return all(current_user.has_permission(perm) for perm in args)

