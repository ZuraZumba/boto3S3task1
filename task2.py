import boto3
from os import getenv
from dotenv import load_dotenv
import logging
from botocore.exceptions import ClientError
import json
import argparse



load_dotenv()

def init_client():
    try:
        client = boto3.client("s3",
                              aws_access_key_id = getenv("aws_access_key_id"),
                              aws_secret_access_key = getenv("aws_secret_access_key"),
                              aws_session_token = getenv("aws_session_token"),
                              region_name = getenv("aws_region_name"))
        client.list_buckets()
        return client
    except ClientError as e:
        logging.error(e)
    except:
        logging.error(("Unexpected error"))



def bucket_exists(aws_s3_client, bucket_name):
    try:
        response = aws_s3_client.head_bucket(Bucket=bucket_name)
    except ClientError as e:
        logging.error(e)
        return False

    status_code = response["ResponseMetadata"]["HTTPStatusCode"]
    if status_code == 200:
        return True
    return False

def policy_exists(aws_s3_client,bucket_name):
    try:
        response = aws_s3_client.get_bucket_policy(Bucket=bucket_name)
    except ClientError as e:
        logging.error(e)
        return False

    status = response["ResponseMetadata"]["HTTPStatusCode"]
    if status == 200:
        return response
    return False

def create_policy(aws_s3_client, bucket_name):
    try:
        bucket_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "AllowListingOfUserFolder",
                    "Principal": "*",
                    "Action": ["s3:ListBucket"],
                    "Effect": "Allow",
                    "Resource": [f"arn:aws:s3:::{bucket_name}"],
                    "Condition": {
                        "StringLike": {
                            "s3:prefix": ["dev/*", "test/*"]
                        }
                    }
                },
            ]
        }
        policy_string = json.dumps(bucket_policy)
        print("იქმნება...")

        aws_s3_client.put_bucket_policy(
            Bucket=bucket_name, Policy=policy_string
        )
        print("შეიქმნა")
    except ClientError as e:
        logging.error(e)
        return False
    return True


def Main():
  parser = argparse.ArgumentParser()
  parser.add_argument("vedro")
  args = parser.parse_args()
  bucket_name = args.vedro

  s3_client = init_client()

  if bucket_exists(s3_client, bucket_name):
      pol = policy_exists(s3_client,bucket_name)
      if not pol:
          create_policy(s3_client,bucket_name)
      else:
          inp=input(f"ამ ვედროს პოლისი უკვე აქვს... გინდა ნახო? (y/n): ")
          if inp=='y' or inp=='Y':
              print(pol)
          elif inp=='n' or inp=='N':
              print('OK')
          else:
              print('invalid input')

  else:
      print(f"{args.vedro} სახელით არაფერი მოიძებნა")

if __name__=='__main__':
    Main()

