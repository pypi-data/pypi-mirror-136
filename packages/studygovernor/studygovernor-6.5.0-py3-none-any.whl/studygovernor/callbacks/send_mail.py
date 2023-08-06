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

from typing import Dict, Any

from ..util.mail import send_email
from studyclient import Experiment, Action


def send_mail(experiment: Experiment,
              action: Action,
              config: Dict[str, Any],
              subject: str,
              body: str,
              **ignore) -> str:
    """
    Send an email with SUBJECT and BODY.

    :param experiment_url: str, 
    :param action_url: str, 
    :param subject: str, 
    :param body: str):
    
    Substitution fields for SUBJECT and BODY are:

       - ``{experiment}``: experiment id
       - ``{experiment_url}``: full url for an experiment
       - ``{action_url}``: full url for an action.

    """

    subject = subject.format(
        experiment=experiment.label,
        experiment_url=experiment.external_uri(),
        action_url=action.external_uri()
    )

    body = body.format(
        experiment=experiment.label,
        experiment_url=experiment.external_uri(),
        action_url=action.external_uri()
    )

    return send_email(subject, body)
