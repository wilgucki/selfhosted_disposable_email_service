import json
import os
import sys

import boto3
import click
import requests
from tabulate import tabulate


CONFIG_PATH = os.path.expanduser(os.path.join('~', '.sheds', 'config.json'))


# TODO use some better name
@click.group()
def shdes():
    pass


@shdes.command()
@click.argument('email')
@click.option('-f', '--forward-to', required=True)
def add_email(email, forward_to):
    # TODO move this to a separate reusable function
    with open(CONFIG_PATH, 'r') as f:
        config = json.load(f)

    response = requests.post(
        f'{config["api_url"]}/emails',
        data={'email': email, 'forward_to': forward_to},
        headers={'Auth': config.get('id_token')}
    )

    # TODO move this to a separate reusable function
    if response.status_code == 401:
        click.echo('You are not logged in or your token has expired.', err=True)
        sys.exit(1)

    click.echo('Email has been added. You need to verify it before you can use it. Verification code has been sent to '
               'forward to address.')

    verification_code = click.prompt('Verification code')

    verification_response = requests.post(
        f'{config["api_url"]}/verify',
        data={'email_address': email, 'verification_code': verification_code},
        headers={'Auth': config.get('id_token')}
    )

    if verification_response.status_code == 200:
        click.echo('Forward to address has been confirmed.')
    else:
        click.echo(f'Something went wrong, {verification_response.json()["message"]}')


@shdes.command()
def list_emails():
    with open(CONFIG_PATH, 'r') as f:
        config = json.load(f)

    response = requests.get(
        f'{config["api_url"]}/emails',
        headers={'Auth': config.get('id_token')}
    )

    # TODO move this to a separate reusable function
    if response.status_code == 401:
        click.echo('You are not logged in or your token has expired.', err=True)
        sys.exit(1)

    if response.status_code != 200:
        click.echo(f'Oops: {response.text}', err=True)
        sys.exit(1)

    emails_json = response.json()
    if 'emails' not in emails_json:
        click.echo('No emails found')
    else:
        header = ['Email Address', 'Forward To', 'Verified']
        rows = sorted([list(email.values()) for email in emails_json['emails']], key=lambda item: item[0])
        click.echo('\n')
        click.echo(tabulate(rows, header))
        click.echo('\n')


@shdes.command()
@click.argument('email')
def delete_email(email):
    with open(CONFIG_PATH, 'r') as f:
        config = json.load(f)

    response = requests.delete(
        f'{config["api_url"]}/emails/{email}',
        headers={'Auth': config.get('id_token')}
    )

    # TODO move this to a separate reusable function
    if response.status_code == 401:
        click.echo('You are not logged in or your token has expired.', err=True)
        sys.exit(1)

    # TODO check response status

    click.echo('Email has been removed')


@shdes.command()
def init():
    if os.path.exists(CONFIG_PATH):
        click.echo('Already initialized')
        sys.exit()

    region = click.prompt('AWS Region')
    userpool_id = click.prompt('User pool ID')
    client_id = click.prompt('Client ID')
    api_url = click.prompt('API url')

    os.makedirs(os.path.dirname(CONFIG_PATH))

    with open(CONFIG_PATH, 'w') as f:
        json.dump({
            'aws_region': region,
            'userpool_id': userpool_id,
            'client_id': client_id,
            'api_url': api_url
        }, f, indent=4)

    click.echo(f'Config saved into {CONFIG_PATH}')


@shdes.command()
def login():
    if not os.path.exists(CONFIG_PATH):
        init()

    username = click.prompt('Login')
    password = click.prompt('Password', hide_input=True)

    with open(CONFIG_PATH, 'r') as f:
        config = json.load(f)

    cognito = boto3.client('cognito-idp', region_name=config['aws_region'])

    try:
        response = cognito.admin_initiate_auth(
            UserPoolId=config['userpool_id'],
            ClientId=config['client_id'],
            AuthFlow='ADMIN_USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': username,
                'PASSWORD': password
            }
        )
    except:
        # TODO catch specific exceptions and display better error message
        click.echo('Invalid username or password', err=True)
        sys.exit(1)
    else:
        with open(CONFIG_PATH, 'w') as f:
            # TODO make sure response contains expected data
            config['id_token'] = response['AuthenticationResult']['IdToken']
            json.dump(config, f, indent=4)
            click.echo('Logged in successfully')


@shdes.command()
@click.option('-e', '--email', required=True)
@click.option('-c', '--verification-code', required=True)
def verify(email, verification_code):
    with open(CONFIG_PATH, 'r') as f:
        config = json.load(f)

    # TODO this is duplicated in the add_email function
    response = requests.post(
        f'{config["api_url"]}/verify',
        data={'email_address': email, 'verification_code': verification_code},
        headers={'Auth': config.get('id_token')}
    )

    if response.status_code == 200:
        click.echo('Forward to address has been confirmed.')
    else:
        click.echo(f'Something went wrong, {response.json()["message"]}')


if __name__ == '__main__':
    shdes()
