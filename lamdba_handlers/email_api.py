from urllib.parse import parse_qsl

from libs.response import response
from libs.services import ServiceException
from libs.services.email import delete_email, list_emails, add_email, verify_email
from libs.validators import is_email_address_valid


def emails(event, context):
    return response(status_code=200, body={'emails': list_emails()})


def add(event, context):
    post = dict(parse_qsl(event['body']))
    email_address = post.get('email')
    forward_to = post.get('forward_to')

    if not is_email_address_valid(email_address):
        return response(status_code=400, headers={'X-Status-Reason': 'Validation failed'},
                        body={'status': 'error', 'message': 'Invalid email address'})

    if not is_email_address_valid(forward_to):
        return response(status_code=400, headers={'X-Status-Reason': 'Validation failed'},
                        body={'status': 'error', 'message': 'Invalid forward to address'})

    try:
        add_email(email_address, forward_to)
    except ServiceException as ex:
        return response(status_code=400, headers={'X-Status-Reason': 'Validation failed'},
                        body={'status': 'error', 'message': str(ex)})

    return response(status_code=201,
                    body={'status': 'ok', 'message': 'Email address added. Please confirm forward to address.'})


def delete(event, context):
    if 'email' not in event['pathParameters']:
        return response(status_code=400, headers={'X-Status-Reason': 'Validation failed'},
                        body={'status': 'error', 'message': 'Email address is missing'})

    if not is_email_address_valid(event['pathParameters']['email']):
        return response(status_code=400, headers={'X-Status-Reason': 'Validation failed'},
                        body={'status': 'error', 'message': 'Invalid email address'})

    delete_email(event['pathParameters']['email'])

    return response(status_code=204)


def verify_forward_to_address(event, context):
    post = dict(parse_qsl(event['body']))
    email_address = post['email_address']
    verification_code = post['verification__code']

    if not is_email_address_valid(email_address):
        return response(status_code=400, headers={'X-Status-Reason': 'Validation failed'},
                        body={'status': 'error', 'message': 'Invalid email address'})

    if not verification_code:
        return response(status_code=400, headers={'X-Status-Reason': 'Validation failed'},
                        body={'status': 'error', 'message': 'Verification code is missing'})

    try:
        verify_email(email_address, verification_code)
        return response(status_code=200, body={'status': 'ok'})
    except ServiceException as ex:
        return response(status_code=400, headers={'X-Status-Reason': 'Validation failed'},
                        body={'status': 'error', 'message': str(ex)})
    except Exception as ex:
        return response(status_code=500, headers={'X-Status-Reason': 'Internal error'},
                        body={'status': 'error', 'message': str(ex)})
