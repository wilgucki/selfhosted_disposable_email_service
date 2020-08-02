import email
import email.utils
import json
import os

import boto3
import botocore.exceptions

from libs.aws.dynamodb import get_table_instance
from libs.settings import EMAILS_TABLE_NAME, LOGGER, TABLE_PREFIX


def forward(event, context):
    table = get_table_instance(EMAILS_TABLE_NAME, TABLE_PREFIX)

    s3_client = boto3.client('s3')
    ses_client = boto3.client('ses')

    for record in event['Records']:
        body = json.loads(record['body'])
        message = json.loads(body['Message'])

        recipients = message['mail']['destination']
        bucket = message['receipt']['action']['bucketName']
        object_key = message['receipt']['action']['objectKey']

        email_object = s3_client.get_object(Bucket=bucket, Key=object_key)
        raw_email = email_object['Body'].read()
        msg = email.message_from_bytes(raw_email)

        body = ''
        if msg.is_multipart():
            for part in msg.walk():
                # TODO make sure this is the best way of doing this
                if part.get_content_type() != 'text/plain':
                    continue

                # TODO make sure that the message is the first on a list
                body = part.get_payload(decode=True).decode()
                break
        else:
            body = msg.get_payload(decode=True)

        for recipient in recipients:
            try:
                LOGGER.debug(f'Forwarding message to {recipient}')
                item = table.get_item(Key={'email_address': recipient})['Item']

                if not item['verified']:
                    LOGGER.info(f'Email address {recipient} is not verified')
                    continue

                # TODO get message content type and set correct message body type (Text or Html)
                LOGGER.debug('Sending message')
                response = ses_client.send_email(
                    # TODO this email address should not be available for users
                    Source=f'no-reply@{os.environ["EMAIL_DOMAIN"]}',
                    Destination={'ToAddresses': [item['forward_to']]},
                    Message={
                        'Subject': {'Data': msg['Subject']},
                        'Body': {'Text': {'Data': body}}
                    }
                )

                # TODO check response (status code, errors and other stuff that could be useful)
                print(response)

            except botocore.exceptions.ClientError as ex:
                if ex.response['Error']['Code'] == 'ResourceNotFoundException':
                    LOGGER.info(f'Email address {recipient} not found, skipping.')
                else:
                    raise ex
