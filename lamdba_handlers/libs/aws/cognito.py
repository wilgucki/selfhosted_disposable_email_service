import base64
import hashlib
import hmac
import os

import boto3

from libs.aws.ssm import get_param


def get_cognito_secret_hash(username, client_secret, client_id):
    dig = hmac.new(
        key=client_secret.encode(),
        msg=f'{username}{client_id}'.encode(),
        digestmod=hashlib.sha256
    ).digest()
    return base64.b64encode(dig).decode()


def login(email, password, pool_id):
    client_secret = get_param(f'/{os.environ["SERVICE_NAME_PREFIX"]}/userpool/client-secret', secure=True)
    client_id = os.environ['USER_POLL_CLIENT_ID']
    secret_hash = get_cognito_secret_hash(email, client_secret, client_id)

    cognito_client = boto3.client('cognito-idp')
    # TODO fetch exceptions and display proper error message
    return cognito_client.admin_initiate_auth(
        UserPoolId=pool_id,
        ClientId=client_id,
        AuthFlow='ADMIN_NO_SRP_AUTH',
        AuthParameters={
            'USERNAME': email,
            'PASSWORD': password,
            'SECRET_HASH': secret_hash
        }
    )
