# AWS Setup for Fluencybox

This document describes the AWS infrastructrue and the process of configuring it. The infrastructure consists of these AWS services: S3, ECR, ECS, SQS and Lambda. Each is described in detail in the sections below.

## Overview
The AWS Console login page is: [https://307571006414.signin.aws.amazon.com/console](https://307571006414.signin.aws.amazon.com/console). AWS IAM (Identity and Access Management) currently has 2 groups defined: Admin and Developer. Users in the Admin group will have full access while users in the Developer group will have only S3 full access.

### S3
AWS S3 is used to store all assets such as images, videos, and audio files. An IAM user with only programmatic access is created with full S3 access. These credentials are used by the backend to access the S3 bucket in the us-west-1 region (N. California).

## ECR
AWS ECR is used to manager container images. The Gentle docker image is managed in one of the repos in the us-west-1 region. ECR works well with ECS which is described below.

## ECS
AWS ECS is used to deploy services on EC2 machines. These are the actual running apps in the us-west-1 region. A Gentle ECS cluster is defined with a task definition that points to the Gentle repo in ECR. This setup tells AWS how to launch new instances of the service. A separate ECS cluster will be defined with the Flask app later.

## SQS
AWS SQS is a queueing service which is configured with a `fluencybox-reports-queue` standard queue. The backend will enqueue jobs here in this queue. Each new job which trigger an invocation of Lambda function which is described below.

## Lambda
AWS Lambda is a service that can be configured to run background jobs. An IAM role is created for the Lambda function that creates images for the report that has the default `AWSLambdaExecute` policy to access S3 and an inline policy to give it `s3:PutObjectAcl` action permission.

Lambda functions can be setup to run by certain trigger events. An SQS queue trigger can be added to invoke a Lambda function so that when the backend adds a new record in the queue, the Lambda function will be called.
Lambda can be configured with environment variables and a timeout value. Lambda can also be configured with a reserve concurrency. This limits how many times the function can be called at once. Since, the Gentle API takes some time and is a bottleneck, the number of Lambda functions needs to be throttled.
