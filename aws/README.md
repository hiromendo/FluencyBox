# AWS Setup for Fluencybox

This document describes the AWS infrastructrue and the process of configuring it. The infrastructure consists of these AWS services: S3, ECR, ECS, SQS and Lambda. Each is described in detail in the sections below.

## Overview
The AWS Console login page is: [https://307571006414.signin.aws.amazon.com/console](https://307571006414.signin.aws.amazon.com/console). AWS IAM (Identity and Access Management) currently has 2 groups defined: Admin and Developer. Users in the Admin group will have full access while users in the Developer group will have only S3 full access.

### S3
AWS S3 is used to store all assets such as images, videos, and audio files. An IAM user with only programmatic access is created with full S3 access. These credentials are used by the backend to access the S3 bucket in the us-west-1 region (N. California).

## ECR
AWS ECR is used to manager container images. The `generate-report-images` docker image is managed in one of the repos in the us-west-1 region. ECR works well with ECS which is described below.

## ECS
AWS ECS is used to deploy services on EC2 machines. These are the actual running apps in the us-west-1 region. A `generate-report-images` ECS cluster is defined with a task definition that points to the `generate-report-images` repo in ECR. This setup tells AWS how to launch new instances of the service. 

## Setting up the Generate Report Images Task
All the files used to create the Docker image for generate report images is located in the `generate-report-images` subdirectory.

The Dockerfile is used to create a new Docker image starting with the public Gentle image. A few Python dependencies are installed and the font and Python script are added to the image. The entrypoint defines the command that will run when container runs. Additional arguments can be added if needed.

The script is written to be self-contained and expects a report url as an argument. The report URL should return a JSON object in the format of `sample.json` that is included in this repo. The script also expects `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` environment variables to be defined to give the script access to uploading the images to S3.
These environment variables have already been set in the task definition via the AWS console.

To test the script in local development, just add a `.env` file with the required environment variables. To run the container locally and test the script first build the image and then run a container with the image as such:

```console
$ docker build -t generate-report-images
$ docker run --env-file .env -it generate-report-images https://www.example.com
```

To deploy a new version of the image, run the following steps.
*Ensure you have installed the latest version of the AWS CLI and Docker. For more information, see the* [ECR documentation](https://docs.aws.amazon.com/AmazonECR/latest/userguide/ECR_GetStarted.html).

1. Retrieve the login command to use to authenticate your Docker client to your registry. Use the AWS CLI:
```
$(aws ecr get-login --no-include-email --region us-west-1)
```

2. Build your Docker image using the following command. You can skip this step if your image is already built:
```
docker build -t generate-report-images .
```

3. After the build completes, tag your image so you can push the image to this repository:
```
docker tag generate-report-images:latest 307571006414.dkr.ecr.us-west-1.amazonaws.com/generate-report-images:latest
```

4. Run the following command to push this image to your newly created AWS repository:
```
docker push 307571006414.dkr.ecr.us-west-1.amazonaws.com/generate-report-images:latest
```
