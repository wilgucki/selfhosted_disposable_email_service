import os
from functools import wraps

from flask import Flask, g, redirect, render_template, request, session, url_for

from libs.aws.cognito import login as sign_in
from libs.aws.ssm import get_param
from libs.services.email import list_emails as list_emails_service, add_email as add_email_service, \
    delete_email as delete_email_service, verify_email as verify_email_service


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not g.user['logged_in']:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


app = Flask(__name__)
app.secret_key = get_param(f'/{os.environ["SERVICE_NAME_PREFIX"]}/webclient/secret-key').encode()


@app.before_request
def before_request():
    g.user = {
        'email': session.get('user_email'),
        'access_token': session.get('user_access_token'),
        'logged_in': session.get('logged_in', False)
    }


@app.route('/')
def index():
    return 'index'


@app.route('/login', methods=['GET', 'POST'])
def login():
    message = None
    if request.method == 'POST':
        try:
            result = sign_in(email=request.form['email'], password=request.form['password'],
                             pool_id=os.environ['USER_POOL_ID'])
            session['logged_in'] = True
            session['user_email'] = request.form['email']
            session['user_access_token'] = result['AuthenticationResult']['AccessToken']
            return redirect(url_for('list_emails'))
        except Exception as ex:
            # TODO handle various exceptions
            message = 'Invalid login or password'

    return render_template('login.html', message=message)


@app.route('/logout')
def logout():
    session.pop('user_email', None)
    session.pop('user_access_token', None)
    session['logged_in'] = False
    return redirect(url_for('index'))


@app.route('/emails')
@login_required
def list_emails():
    emails = list_emails_service()
    return render_template('email_list.html', emails=emails)


@app.route('/emails/add', methods=['GET', 'POST'])
@login_required
def add_email():
    if request.method == 'POST':
        # TODO handle exceptions
        add_email_service(request.form['email'], request.form['forward_to'])
        return redirect(url_for('list_emails'))

    return render_template('add_email.html')


@app.route('/emails/delete/<email>')
@login_required
def delete_email(email):
    # TODO confirm email deletion
    delete_email_service(email)
    return redirect(url_for('list_emails'))


@app.route('/emails/verify/<email>', defaults={'code': None}, methods=['GET', 'POST'])
@app.route('/emails/verify/<email>/<code>')
def verify_email_address(email, code):
    if code is None and request.method == 'GET':
        return render_template('verify_code.html')

    if request.method == 'POST':
        # TODO validate this
        code = request.form['code']

    if code is not None:
        verify_email_service(email, code)
        return redirect(url_for('list_emails'))
