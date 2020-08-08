from libs.aws import Resource


def get_table_instance(table_name: str, prefix=''):
    if prefix:
        prefix += '_'

    dynamodb = Resource.get('dynamodb')
    return dynamodb.Table(f'{prefix}{table_name}')
