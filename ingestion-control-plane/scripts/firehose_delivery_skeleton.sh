#!/usr/bin/env bash

# SentinelForge Amazon Data Firehose skeleton.
#
# This is a study and portfolio artifact. Do not run this blindly.
# Replace placeholder values before using in a real AWS account.
#
# Purpose:
# Demonstrate the AWS CLI shape for creating a delivery stream that sends
# streaming cybersecurity events into an S3 raw zone.

set -euo pipefail

AWS_REGION="us-west-2"
DELIVERY_STREAM_NAME="sentinelforge-firewall-events"
S3_BUCKET_NAME="sentinelforge-ml-data"
S3_PREFIX="raw/firewall/year=!{timestamp:yyyy}/month=!{timestamp:MM}/day=!{timestamp:dd}/"
ERROR_OUTPUT_PREFIX="errors/firehose/!{firehose:error-output-type}/year=!{timestamp:yyyy}/month=!{timestamp:MM}/day=!{timestamp:dd}/"

# Replace this with the IAM role ARN that allows Firehose to write to S3.
FIREHOSE_ROLE_ARN="arn:aws:iam::280480953008:role/SentinelForgeFirehoseDeliveryRole"

aws firehose create-delivery-stream \
  --region "${AWS_REGION}" \
  --delivery-stream-name "${DELIVERY_STREAM_NAME}" \
  --delivery-stream-type DirectPut \
  --s3-destination-configuration "RoleARN=${FIREHOSE_ROLE_ARN},BucketARN=arn:aws:s3:::${S3_BUCKET_NAME},Prefix=${S3_PREFIX},ErrorOutputPrefix=${ERROR_OUTPUT_PREFIX},BufferingHints={SizeInMBs=128,IntervalInSeconds=60},CompressionFormat=GZIP"

echo "Created Firehose delivery stream skeleton: ${DELIVERY_STREAM_NAME}"