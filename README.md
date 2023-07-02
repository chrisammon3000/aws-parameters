# aws-parameters
<!-- [![Build](https://github.com/abk7777/aws-json-dataset/actions/workflows/run_tests.yml/badge.svg)](https://github.com/abk7777/aws-json-dataset/actions/workflows/run_tests.yml) [![codecov](https://codecov.io/github/abk7777/aws-json-dataset/branch/main/graph/badge.svg?token=QSZLP51RWJ)](https://codecov.io/github/abk7777/aws-json-dataset)  -->
[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/release/python-3100/) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Streamlined, efficient access to configuration values in AWS SSM Parameter Store and SecretsManager.

## Description
* Immediate access to available parameters and secrets 
* Reduce development overhead for Python applications running on AWS
* Maintain least-privileged permissions to parameters and secrets

## Quickstart
Install the library using pip.
```bash
pip install -i https://test.pypi.org/simple/ aws-parameters
```

<!-- Export the AWS region to the environment.
```bash
export AWS_REGION=<region>
```

Send JSON data to various AWS services.
```python
from awsjsondataset import AwsJsonDataset

# create a list of JSON objects
data = [ {"id": idx, "data": "<data>"} for idx in range(100) ]

# Wrap using AwsJsonDataset
dataset = AwsJsonDataset(data=data)

# Send to SQS queue
dataset.sqs("<sqs_queue_url>").send_messages()

# Send to SNS topic
dataset.sns("<sns_topic_arn>").publish_messages()

# Send to Kinesis Firehose stream
dataset.firehose("<delivery_stream_name>").put_records()
``` -->

## Local Development
Follow the steps to set up the deployment environment.

### Prerequisites
* Python 3.10
* AWS credentials

### Creating a Python Virtual Environment
When developing locally, create a Python virtual environment to manage dependencies:
```bash
python3.10 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install .[dev,test]
```

### Environment Variables
Create a `.env` file in the project root.
```bash
AWS_REGION=<region>
```

***Important:*** *Always use a `.env` file or AWS SSM Parameter Store or Secrets Manager for sensitive variables like credentials and API keys. Never hard-code them, including when developing. AWS will quarantine an account if any credentials get accidentally exposed and this will cause problems.* &rarr; ***Make sure that `.env` is listed in `.gitignore`***

### AWS Credentials
Valid AWS credentials must be available to AWS CLI and SAM CLI. The easiest way to do this is running `aws configure`, or by adding them to `~/.aws/credentials` and exporting the `AWS_PROFILE` variable to the environment.

For more information visit the documentation page:
[Configuration and credential file settings](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html)

## Unit Tests
Follow the steps above to create a Python virtual environment. Run tests with the following command.
```bash
coverage run -m pytest
```

## Troubleshooting
* Check your AWS credentials in `~/.aws/credentials`
* Check that the environment variables are available to the services that need them
* Check that the correct environment or interpreter is being used for Python

<!-- ## References & Links -->

## Authors
**Primary Contact:** @chrisammon3000

## License
This library is licensed under the MIT-0 License. See the LICENSE file.