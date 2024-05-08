import boto3
import logging
import json
from application_config.document_config import AWS_CONFIG


class SnsWrapper:

    def __init__(self):
        self.client = None
        self.get_sns_client()

    def get_sns_client(self):
        if self.client is None:
            self.client = boto3.client(
                'sns',
                aws_access_key_id=AWS_CONFIG.get("access_key"),
                aws_secret_access_key=AWS_CONFIG.get("secret_key"),
                region_name=AWS_CONFIG.get("region")
            )

    def push_to_sns(self, msg, topic=None):
        try:
            response = self.client.publish(
                TargetArn=topic or AWS_CONFIG.get("document_processor_sns_arn"),
                Message=json.dumps({'default': json.dumps(msg)}),
                MessageStructure='json'
            )
        except Exception as e :
            logging.error(f"failed to push to sns as {e}, log_key:push_to_sns")
            response = None
        return response







