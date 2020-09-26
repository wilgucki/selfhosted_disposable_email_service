import os
from functools import wraps

from flask import Flask, g, redirect, render_template, request, session, url_for

from libs.aws.cognito import login as signin
from libs.aws.ssm import get_param


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
            result = signin(email=request.form['email'], password=request.form['password'],
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


@app.route('/emails/list')
@login_required
def list_emails():
    return 'list emails'


@app.route('/emails/add', methods=['GET', 'POST'])
@login_required
def add_email():
    return 'add email'


@app.route('/emails/delete/<email>')
@login_required
def delete_email(email):
    return 'delete email'
