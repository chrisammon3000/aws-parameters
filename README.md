# aws-parameters
<!-- [![Build](https://github.com/abk7777/aws-json-dataset/actions/workflows/run_tests.yml/badge.svg)](https://github.com/abk7777/aws-json-dataset/actions/workflows/run_tests.yml) [![codecov](https://codecov.io/github/abk7777/aws-json-dataset/branch/main/graph/badge.svg?token=QSZLP51RWJ)](https://codecov.io/github/abk7777/aws-json-dataset)  -->
[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/release/python-3100/) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Streamlined, efficient access to configuration values in AWS SSM Parameter Store and SecretsManager.

## Description
When building Python applications in AWS, it is common to use SSM Parameter Store and SecretsManager to store configuration values. This library provides a simple interface to access these values in a way that is fast, efficient, and secure. It will perform lazy loading for all available parameters or secrets, meaning it will only make API calls when a value is requested:
- When parameter or secret property is accessed, it first checks if the value has been computed before (cached). If it has, it immediately returns that cached value.
- If the value hasn't been computed before, it fetches the value and then returns it. This means that your Python app is only calling the AWS API when it needs to.

### Advantages
* Fast, simple interface to configuration values that can reduce development overhead when working with SSM Parameter Store and SecretsManager
* Immediate access to available parameters and secrets through intellisense, `map` or `list` methods
* Maintain least-privileged permissions to parameters and secrets using path-based access control

## Quickstart
Install the library using pip.
```bash
pip install -i https://test.pypi.org/simple/ aws-parameters
```

## Environment Setup

### Methods of Access
There are 3 methods of accessing SSM Parameters and SecretsManager Secrets values using `aws-parameters.`
1. From JSON file or object (fastest, does not make additional API calls)
2. From API Methods `describe-parameters` or `list-secrets` (second fastest)
3. From deployed SSM Parameter mapping (slowest but least error prone, makes two additional API calls and parses responses)

#### JSON File or Object

### AWS API Methods

### SSM Parameter Mapping

## Usage
See [Methods of Access](#methods-of-access) for the different ways to setup the environment and access SSM Parameters and SecretsManager Secrets values.

### SSM Parameter Mapping
```python
from awsparameters import AppConfig

# (optional) Create a boto3 session
session = boto3.Session(region_name=AWS_REGION)

# Define the parameter mappings path
config_path = f"/{APP_NAME}/{STAGE}/{AWS_REGION}/GfedbInfrastructureParamMappings"

# Create the AppConfig object from the mappings path
app = AppConfig(
    mapping_path=infra_config_path, 
    boto3_session=session)
```

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