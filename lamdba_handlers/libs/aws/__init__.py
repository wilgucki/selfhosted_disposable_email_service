import boto3


class Resource:
    _resources = {}

    @staticmethod
    def get(name: str, **kwargs):
        if name not in Resource._resources:
            Resource._resources[name] = boto3.resource(name, **kwargs)

        return Resource._resources[name]
