from datetime import datetime, timezone
from typing import List

import botocore.exceptions

from libs.aws.dynamodb import get_table_instance
from libs.services import ServiceException
from libs.settings import EMAILS_TABLE_NAME, TABLE_PREFIX


def add_email(email_address: str, forward_to: str):
    table = get_table_instance(EMAILS_TABLE_NAME, TABLE_PREFIX)

    # TODO there must be a better way of checking if item exists
    try:
        response = table.get_item(Key={'email_address': email_address})
        if 'Item' in response:
            raise ServiceException('Email address already taken')
    except botocore.exceptions.ClientError as ex:
        if ex.response['Error']['Code'] != 'ResourceNotFoundException':
            raise ex

    table.put_item(
        Item={
            'email_address': email_address,
            'forward_to': forward_to,
            'verified': False,
            'verification_code': '',  # TODO generate verification code
            'created_at': datetime.now(tz=timezone.utc).isoformat()
        }
    )

    # TODO verify forward to email address


def delete_email(email_address: str):
    table = get_table_instance(EMAILS_TABLE_NAME, TABLE_PREFIX)
    table.delete_item(Key={'email_address': email_address})


def list_emails() -> List:
    table = get_table_instance(EMAILS_TABLE_NAME, TABLE_PREFIX)
    response = table.scan()
    emails = []
    if response['Count'] > 0:
        emails = [item['email_address'] for item in response['Items']]

    return emails
