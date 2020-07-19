import boto3


def get_table_instance(table_name: str, prefix=''):
    if prefix:
        prefix += '_'

    # TODO move this to a separate function/class to avoid multiple calls to resource function
    dynamodb = boto3.resource('dynamodb')
    return dynamodb.Table(f'{prefix}{table_name}')
