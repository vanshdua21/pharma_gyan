import codecs
import csv

import boto3
import botocore
from urllib.parse import urlparse
import logging
from botocore.client import Config
from django.conf import settings


class S3Wrapper:

    def __init__(self):
        self.client = None
        self.get_s3_client()

    def get_s3_client(self):
        if self.client is None:
            self.client = boto3.client(
        's3',
        aws_access_key_id="AKIAQUFLP6LRNCUHZSNH",
        aws_secret_access_key="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",
        region_name="ap-south-1"
    )

    def get_s3_bucket_key(self, path):
        #     return s3 bucket and key from s3 url
        parse_object = urlparse(path, allow_fragments=False)
        bucket = parse_object.netloc
        key = parse_object.path
        return {"bucket": bucket, "key": key}

    def get_s3_object_from_url(self, path=None):
        if path is None:
            return {"success": False, "info": "No Pat provided"}
        url_params = self.get_s3_bucket_key(path)
        bucket = url_params.get("bucket", None)
        key = url_params.get("key", None)
        key = key[1:] if key is not None and len(key) > 0 else key
        return self.get_s3_object(bucket, key)

    def get_s3_object(self, bucket, key):
        s3_object = self.client.get_object(Bucket=bucket, Key=key)
        if s3_object is not None:
            s3_data = s3_object["Body"].read()
            return {"success": True, "data": s3_data}
        else:
            return {"success": False, "data": None}

    def upload_and_return_s3_url(self, bucket, file):
        try:
            self.client.upload_fileobj(file, bucket, file.name)
        except Exception as e:
            logging.error(f"log_key: upload_object_from_string, err: {e}")
            return None
        s3_url = f"https://{bucket}.s3.ap-south-1.amazonaws.com/{file.name}"
        return s3_url

    def upload_object_from_string(self, bucket, key, data, params={}):
        try:
            self.get_s3_client()
            if self.client is None:
                logging.error(f"unable to make S3 connection, BUCKET : {bucket}, KEY: {key}")
            result = self.client.put_object(Bucket=bucket, Key=key, Body=data,
                                            ContentType=params.get('Content-Type', 'text/plain'),
                                            ACL=params.get('ACL', 'bucket-owner-full-control'))
            res = result.get('ResponseMetadata')

            if res.get('HTTPStatusCode') == 200:
                logging.info('File Uploaded Successfully')
            else:
                logging.info('File Not Uploaded')
        except Exception as uploadExp:
            logging.error(f"log_key: upload_object_from_string, err: {uploadExp}")
            raise uploadExp
