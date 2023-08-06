import boto3


class Aws:
    def __init__(self, region):
        self.region = region
        self.client = boto3.client("ec2", region)
        self.resource = boto3.resource("ec2", region)
        self.inference_client = boto3.client("elastic-inference", region)
        self.kms_client = boto3.client("kms", region)
