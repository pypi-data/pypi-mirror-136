from typing import Dict, Any

import docker

from studyclient import Experiment, Action

# "image": "bigr/fastr:develop",
# "volumes": {
#     "/Users/adriaan/Projects/2018_HACKATHON/pipelines/iris": {"bind": "/Users/adriaan/Projects/2018_HACKATHON/pipelines/iris", "mode": "rw"},
#     "/Users/adriaan/Projects/2018_HACKATHON/pipelines/fastr-tmp": {"bind": "/Users/adriaan/Projects/2018_HACKATHON/pipelines/fastr-tmp", "mode": "rw"},
#     "/Users/adriaan/Projects/2018_HACKATHON/pipelines/fastr-out": {"bind": "/Users/adriaan/Projects/2018_HACKATHON/pipelines/fastr-out", "mode": "rw"}
# },
# "cmd": ["python", "qa-script.py", "--experiment"],
# "arguments": {
#     "--xnat": "http://xnat.bigr.infra",
#     "--project" : "sandbox",
#     "--pipeline_succes" : "/api/v1/states/create_inspection_task",
#     "--pipeline_failed" : "/api/v1/states/dcm2niix_failed"
# }


def docker_run(experiment: Experiment,
               action: Action,
               config: Dict[str, Any],
               image: str,
               progress_state=None,
               args=None,
               volumes=None,
               environment=None,
               cmd=None,
               xnat_external_system_name: str='XNAT',
               **ignore):
    """
    Run docker container task

    :param experiment_url: str
    :param action_url: str
    :param image: str
    :param progress_state: None
    :param args: None
    :param volumes: None
    :param environment: None
    :param cmd: None
    :param xnat_external_system_name: name of the external xnat [XNAT]

    The items in args that contain certain VARS will be replaced. Accepted VARS:

    - $EXPERIMENT - will be substituted with the experiment URL.
    - $XNAT - will be substituted with the xnat URL.

    Example:

    .. code-block:: JSON

       {
         "function": "create_task",
         "image": "bigr/fastr:develop",
         "volumes": {
             "pipelines/atlas": {"bind": "pipelines/atlas", "mode": "rw"},
             "pipelines/params": {"bind": "pipelines/params", "mode": "rw"}
         },
         "cmd": ["python", "qa-script.py"],
         "args": {
             "--experiment": "$EXPERIMENT",
             "--xnat": "$XNAT",
             "--project" : "sandbox",
             "--pipeline_succes" : "/api/v1/states/create_inspection_task",
             "--pipeline_failed" : "/api/v1/states/QA_failed"
         }
       }

    """

    # Get XNAT address from database
    xnat = experiment.session.external_systems[xnat_external_system_name]
    xnat_uri = xnat.url.rstrip('/')
    args = [x.replace("$XNAT", xnat_uri) for x in args]

    # Get XNAT address from Database
    args = [x.replace("$EXPERIMENT", experiment.external_uri) for x in args]

    command = [str(x) for x in cmd] + [str(experiment.external_uri())] + [str(x) for x in args]
    print('[CALLBACK docker-run] experiment:{}'.format(experiment.external_uri()))
    print('[CALLBACK docker-run] action_url:{}'.format(action.external_uri()))
    print('[CALLBACK docker-run] image:{}'.format(image))
    print('[CALLBACK docker-run] cmd:{}'.format(command))
    print('[CALLBACK docker-run] progress_state:{}'.format(progress_state))

    #client = docker.APIClient(base_url='unix://var/run/docker.sock')
    client = docker.from_env()
    output = client.containers.run(image, command, environment=environment, volumes=volumes)
    print('[CALLBACK docker-run] outout: {}'.format(output))
