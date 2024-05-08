import boto3
from botocore.exceptions import ClientError
from application_config.document_config import AWS_CONFIG
from pharma_gyan_proj.utils.logging_utils import Logger

logger = Logger()

class SecretManager:

    def __init__(self):
        self.session = boto3.session.Session()
        self.client = self.session.client(
            service_name='secretsmanager',
            aws_access_key_id=AWS_CONFIG.get("access_key"),
            aws_secret_access_key=AWS_CONFIG.get("secret_key"),
            region_name=AWS_CONFIG.get("region")
        )

    def get_secret(self, secret_name):
        logger.info(f'secret_name : {secret_name}')
        try:
            get_secret_value_response = self.client.get_secret_value(
                SecretId=secret_name
            )
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                logger.info("The requested secret " + secret_name + " was not found")
            elif e.response['Error']['Code'] == 'InvalidRequestException':
                logger.info("The request was invalid due to:", e)
            elif e.response['Error']['Code'] == 'InvalidParameterException':
                logger.info("The request had invalid params:", e)
            elif e.response['Error']['Code'] == 'DecryptionFailure':
                logger.info("The requested secret can't be decrypted using the provided KMS key:", e)
            elif e.response['Error']['Code'] == 'InternalServiceError':
                logger.info("An error occurred on service side:", e)
        else:
            # Secrets Manager decrypts the secret value using the associated KMS CMK
            # Depending on whether the secret was a string or binary, only one of these fields will be populated
            if 'SecretString' in get_secret_value_response:
                text_secret_data = get_secret_value_response['SecretString']
                return text_secret_data
            else:
                binary_secret_data = get_secret_value_response['SecretBinary']
                return binary_secret_data
