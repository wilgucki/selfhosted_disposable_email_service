import os
from urllib.parse import parse_qs

import boto3

from libs.aws.dynamodb import get_table_instance
from libs.template import render_template


def login(event, context):
    data = {}
    if event['httpMethod'] == 'POST':
        post = {field: value[0] for field, value in parse_qs(event['body']).items()}
        email = post['email']
        password = post['password']

        client_id = os.environ['USER_POOL_CLIENT_ID']

        # TODO region shouldn't be hardcoded
        cognito = boto3.client('cognito-idp', region_name='us-east-1')
        try:
            r = cognito.admin_initiate_auth(
                UserPoolId=os.environ['USER_POOL_ID'],
                ClientId=client_id,
                AuthFlow='ADMIN_USER_PASSWORD_AUTH',
                AuthParameters={
                    'USERNAME': email,
                    'PASSWORD': password
                }
            )
        except Exception as ex:  # TODO catch specific exception
            data['message'] = 'Invalid username or password'
        else:
            table = get_table_instance(os.environ['TOKENS_TABLE'])
            table.put_item(
                Item={
                    'user_email': email,
                    'id_token': r['AuthenticationResult']['IdToken'],
                    'access_token': r['AuthenticationResult']['AccessToken'],
                    'refresh_token': r['AuthenticationResult']['RefreshToken']
                }
            )

            data['message'] = 'ok'  # TODO return something more meaningful

    return render_template('login.html', data=data)
