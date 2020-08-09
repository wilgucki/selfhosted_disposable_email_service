import os
import random
import string
from datetime import datetime, timezone
from typing import List

import boto3
import botocore.exceptions

from libs.aws.dynamodb import get_table_instance
from libs.services import ServiceException
from libs.settings import EMAILS_TABLE_NAME, TABLE_PREFIX


def add_email(email_address: str, forward_to: str):
    table = get_table_instance(EMAILS_TABLE_NAME, TABLE_PREFIX)

    try:
        response = table.get_item(Key={'email_address': email_address})
        if 'Item' in response:
            raise ServiceException('Email address already taken')
    except botocore.exceptions.ClientError as ex:
        if ex.response['Error']['Code'] != 'ResourceNotFoundException':
            raise ex

    verification_code = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(50))

    table.put_item(
        Item={
            'email_address': email_address,
            'forward_to': forward_to,
            'verified': False,
            'verification_code': verification_code,
            'created_at': datetime.now(tz=timezone.utc).isoformat()
        }
    )

    # TODO send verification link
    # TODO change message body to be more user friendly
    ses = boto3.client('ses')
    ses.send_email(
        Source=f'no-reply@{os.environ["EMAIL_DOMAIN"]}',
        Destination={
            'ToAddresses': [forward_to]
        },
        Message={
            'Subject': 'Verify forward to email address',
            'Body': {
                'Text': {
                    'Data': f'Verification code: {verification_code}'
                }
            }
        }
    )


def delete_email(email_address: str):
    table = get_table_instance(EMAILS_TABLE_NAME, TABLE_PREFIX)
    table.delete_item(Key={'email_address': email_address})


def list_emails() -> List:
    table = get_table_instance(EMAILS_TABLE_NAME, TABLE_PREFIX)
    response = table.scan()
    emails = []

    if response['Count'] > 0:
        for item in response['Items']:
            emails.append({
                'email_address': item['email_address'],
                'forward_to': item['forward_to'],
                'verified': item['verified']
            })

    return emails


def verify_email(email_address: str, verification_code: str):
    if not verification_code:
        raise ServiceException('Verification code is missing')

    table = get_table_instance(EMAILS_TABLE_NAME, TABLE_PREFIX)
    response = table.get_item(Key={'email_address': email_address})
    item = response['Item']

    if item['verification_code'] != verification_code:
        raise ServiceException('Invalid verification code')

    table.update_item(
        Key={'email_address': email_address},
        UpdateExpression='SET verification_code=:verification_code, verified=:verified',
        ExpressionAttributeValues={':verification_code': {'NULL': True}, ':verified': {'BOOL': True}}
    )
