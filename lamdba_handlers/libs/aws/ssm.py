import boto3


def get_param(name, secure=True):
    ssm_client = boto3.client('ssm')
    return ssm_client.get_parameter(Name=name, WithDecryption=secure)['Parameter']['Value']
