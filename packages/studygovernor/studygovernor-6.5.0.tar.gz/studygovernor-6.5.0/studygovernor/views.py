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

from flask import abort, render_template, Blueprint, request
from flask_restx import reqparse, inputs
from flask_security import current_user
from flask_security import login_required
from flask_security import permissions_required
from flask_security import permissions_accepted
from flask_wtf import FlaskForm
from wtforms import TextField, TextAreaField, SubmitField, SelectMultipleField
from wtforms.validators import DataRequired


from collections import defaultdict

from . import control, models
from .util.mail import send_bulk_mail
from .util.helpers import get_object_from_arg

ITEMS_PER_PAGE = 15

# Get app and db
bp = Blueprint('web', __name__)


# Web resources
@bp.app_errorhandler(404)
def page_not_found_error(error):
    title = f'Taskmanager: 404 Not Found'
    return render_template('error/notfound.html', title=title), 404


@bp.errorhandler(403)
def forbidden_error(error):
    title = f'Taskmanager: 403 Forbidden'
    return render_template('error/forbidden.html', title=title), 404


@bp.route('/')
@bp.route('/index')
def index():
    return render_template('index.html')


@bp.route('/states/workflow/<int:id>')
@login_required
def web_state_workflow(id):
    page = request.args.get('page', 1, type=int)
    workflows = models.Workflow.query.order_by(models.Workflow.id.asc()).all()
    states = models.State.query.filter(models.State.workflow_id == id).paginate(page=page, per_page=ITEMS_PER_PAGE)
    current_workflow = models.Workflow.query.get(id)
    return render_template('state_workflow.html', current_workflow=current_workflow, states=states, workflows=workflows)


@bp.route('/states')
@login_required
def web_states():
    workflows = models.Workflow.query.order_by(models.Workflow.id.asc()).all()
    all_states = models.State.query.join(models.Workflow).order_by(models.State.id).add_column(models.Workflow.label).all()
    states_grouped_by_label = defaultdict(list)
    for state, workflow_label in all_states:
        states_grouped_by_label[state.label].append((state, workflow_label))
    return render_template('states.html', states_grouped_by_label=states_grouped_by_label, workflows=workflows)

@bp.route('/states/<int:id>')
@login_required
def web_state(id):
    state = models.State.query.filter(models.State.id == id).one_or_none()
    return render_template('state.html', state=state)


@bp.route('/workflows')
@login_required
def web_workflows():
    page = request.args.get('page', 1, type=int)
    workflows = models.Workflow.query.order_by(models.Workflow.id.asc()).paginate(page=page, per_page=ITEMS_PER_PAGE)
    return render_template('workflows.html', workflows=workflows)


@bp.route('/workflows/<int:id>')
@login_required
def web_workflow(id):
    workflow = models.Workflow.query.filter(models.Workflow.id == id).one_or_none()
    return render_template('workflows.html', workflow=workflow)


@bp.route('/transitions/workflow/<int:id>')
@login_required
def web_transition_workflow(id):
    page = request.args.get('page', 1, type=int)
    workflows = models.Workflow.query.order_by(models.Workflow.id.asc()).all()
    transitions = models.Transition.query.join(models.State, models.Transition.source_state_id == models.State.id)\
        .filter(models.State.workflow_id == id).paginate(page=page, per_page=ITEMS_PER_PAGE)
    return render_template('transition_workflow.html', workflow_id=id, transitions=transitions, workflows=workflows)


@bp.route('/transitions')
@login_required
def web_transitions():
    page = request.args.get('page', 1, type=int)
    workflows = models.Workflow.query.order_by(models.Workflow.id.asc()).all()
    transitions = models.Transition.query.paginate(page=page, per_page=ITEMS_PER_PAGE)
    return render_template('transitions.html', transitions=transitions, workflows=workflows)


@bp.route('/transitions/<int:id>')
@login_required
def web_transition(id):
    transition = models.Transition.query.filter(models.Transition.id == id).one_or_none()
    if transition is None:
        abort(404)
    return render_template('transition.html', transition=transition)


@bp.route('/subjects')
@login_required
def web_subjects():
    page = request.args.get('page', 1, type=int)
    subjects = models.Subject.query.paginate(page=page, per_page=ITEMS_PER_PAGE)
    return render_template('subjects.html', subjects=subjects)


@bp.route('/subjects/<int:id>')
@login_required
def web_subject(id):
    subject = models.Subject.query.filter(models.Subject.id == id).one_or_none()
    if subject is None:
        abort(404)
    return render_template('subject.html', subject=subject)


@bp.route('/experiments')
@login_required
def web_experiments():
    page = request.args.get('page', 1, type=int)
    experiments = models.Experiment.query.paginate(page=page, per_page=ITEMS_PER_PAGE)
    return render_template('experiments.html', experiments=experiments)


@bp.route('/experiments/<int:id>')
@login_required
def web_experiment(id):
    experiment = models.Experiment.query.filter(models.Experiment.id == id).one_or_none()
    if experiment is None:
        abort(404)
    return render_template('experiment.html', experiment=experiment)


@bp.route('/actions/<int:id>')
@login_required
def web_action(id):
    action = models.Action.query.filter(models.Action.id == id).one_or_none()
    if action is None:
        abort(404)
    return render_template('action.html', action=action)


@bp.route('/users')
@login_required
@permissions_accepted('roles_manage')
def users():
    page = request.args.get('page', 1, type=int)
    data = models.User.query.paginate(page=page, per_page=ITEMS_PER_PAGE)
    roles = models.Role.query.order_by(models.Role.id).all()
    return render_template('userroles.html', data=data, roles=roles)


@bp.route('/users/<int:id>')
@login_required
def user(id):
    data = models.User.query.filter(models.User.id == id).one_or_none()
    if data is None:
        abort(404)

    if not current_user.has_permission('user_read_all'):
        # This is a normal user, so may only see own user information.
        if current_user != data:
            abort(403)

    return render_template('user.html', data=data)


class MailForm(FlaskForm):
    recipients = SelectMultipleField('Recipients')
    subject = TextField('Subject', validators=[DataRequired()])
    body = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Send')

    @bp.route("/mail", methods=['GET', 'POST'])
    @login_required
    @permissions_accepted('user_read_all')
    def mail():
        form = MailForm(request.form)

        form.recipients.choices = ((u.username, f'{u.name} <{u.email}>') for u in models.User.query.all())

        if form.validate_on_submit():
            recipients = form.recipients.data
            subject = form.subject.data
            body = form.body.data

            if recipients:
                recipients = [get_object_from_arg(x, models.User, models.User.username, skip_id=True) for x in recipients]
            else:
                recipients = models.User.query.all()

            send_bulk_mail(
                recipients=recipients,
                subject=subject,
                body=body,
            )
            return render_template('mail_sent.html',
                                   recipients=recipients,
                                   subject=subject,
                                   body=body)

        return render_template('mail.html', mail_form=form)
