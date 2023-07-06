# aws-parameters ⚙️
<!-- [![Build](https://github.com/abk7777/aws-json-dataset/actions/workflows/run_tests.yml/badge.svg)](https://github.com/abk7777/aws-json-dataset/actions/workflows/run_tests.yml) [![codecov](https://codecov.io/github/abk7777/aws-json-dataset/branch/main/graph/badge.svg?token=QSZLP51RWJ)](https://codecov.io/github/abk7777/aws-json-dataset)  -->
[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/release/python-3100/) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Streamlined, efficient access to configuration values in AWS SSM Parameter Store and SecretsManager.

## Description
When building applications in AWS, it is common to use SSM Parameter Store and SecretsManager to store configuration values. The `aws-parameters` library provides a simple, easy interface to access these values in a way that is fast, efficient, and secure. It is quick to setup and will perform lazy loading for all available parameters or secrets, meaning it will only call the API the first time the value is requested.

### How it Works
There are 3 basics steps involved in using `aws-parameters`:
1. Create a JSON object with service-to-parameter mappings
2. Pass this JSON object to the `AppConfig` class
3. Access parameters and secrets through the `params` and `secrets` attributes of the `AppConfig` instance

 First, you will need to create a Parameter Mappings object looking something like this:
```json
// param-mappings.json
{
    "ssm": [
        "/dev/myapp/MyParam1",
        "/dev/myapp/MyParam2"
    ],
    "secretsmanager": [
        "/dev/myapp/MySecret1",
        "/dev/myapp/MySecret2"
    ]
}
```
Next, you can pass this object to the `AppConfig` class using several methods to create an instance. See [Configuration Methods](#configuration-methods) for more details.
```python
from awsparameters import AppConfig

# load the above JSON object from a file
with open("param-config.json", "r") as f:
    param_config = json.load(f)

app = AppConfig(mappings_path=param_config)
```
Lastly, you can access parameters and secrets like this:
```python
# access a parameter
MyParam1 = app.params.MyParam1

# access a secret
MySecret1 = app.secrets.MySecret1
```

### Advantages
- Fast, simple interface to configuration values that can reduce development overhead when working with SSM Parameter Store and SecretsManager
- Immediate access to available parameters and secrets through intellisense, `map` or `list` methods
- Maintain least-privileged permissions to parameters and secrets using path-based access control
- Lazy loading for all available parameters or secrets, meaning it will only make API calls when a value is requested:
    - When parameter or secret property is accessed, it first checks if the value has been computed before (cached). If it has, it immediately returns that cached value.
    - If the value hasn't been computed before, it fetches the value and then returns it. This means that your Python app is only calling the AWS API when it needs to.

### Considerations
* You must use the path convention for naming parameters, but you can choose any separator you want by setting the `path_separator` parameter when creating an instance of `AppConfig`. The default is `/`.
* Only the latest parameter versions can be fetched.

## Quickstart
Install the library using pip.
```bash
pip install -i https://test.pypi.org/simple/ aws-parameters
```

## Environment Configuration

### Parameter Mappings
The `AppConfig` class requires a JSON object with service to parameter mappings in order to know which values it needs to access:
```json
// Parameter Mappings JSON Schema
{
    "ssm": [
        "parameter_path_and_identifier",
        ...
    ],
    "secretsmanager": [
        "secret_path_and_identifier",
        ...
    ]
}
```

For example:
```json
{
    "ssm": [
        "/dev/myapp/MyParam1",
        "/dev/myapp/MyParam2"
    ],
    "secretsmanager": [
        "/dev/myapp/MySecret1",
        "/dev/myapp/MySecret2"
    ]
}
```
In this example, the path is `/dev/myapp` and the identifiers or names are `MyParam1`, `MyParam2`, `MySecret1`, and `MySecret2`.

You can store this in a JSON file or as its own SSM Parameter.

### Configuration Methods

<!-- TODO
There are 3 methods of creating or providing this JSON object to `aws-parameters`:
1. From a local JSON file (fastest)
2. From a parameter path such as `/dev/myapp/*` (second fastest)
3. From deployed SSM Parameter mapping (third fastest) -->

The current method of providing this JSON object to `aws-parameters` is from deployed SSM Parameter mapping (third fastest)

See [Methods of Access](#methods-of-access) for more details.


<!-- #### JSON File or Object
This is the fastest method but it requires that the JSON file is up to date with the latest parameters and secrets.

### Parameter Path
Choose and utilize a path naming convention in your cloud resource definitions for SSM Parameters or SecretsManager Secrets. 

For example you can use the template `/{stage}/{app name}/{parameter or secret name}` when creating SSM Parameters or Secrets. You could then just pass the path `/{stage}/{app name}/*` to `aws-parameters` and it will use AWS SDK methods for Systems Manager and SecretsManager to listor describe and retrieve all available parameters or secrets under that path. -->


#### From SSM Parameter
For this method of configuration you would store the parameter mappings as a JSON string using an SSM Parameter in your AWS account. Here is an example using a CloudFormation template:
```yaml
AWSTemplateFormatVersion: "2010-09-09"
Parameters:
  AppName:
    Type: String
    Description: Name of the application
  Stage:
    Type: String
    Description: Stage of the application
Resources:
  ParamMappingsParameter:
    Type: AWS::SSM::Parameter
    Properties:
      Type: String
      Name: !Sub '/${Stage}/${AppName}/MyParamMappings'
      Description: "Parameter mappings for aws-parameters"
      Tier: Standard
      Value: !Sub |
        {
          "ssm": [
              "/${Stage}/${AppName}/MyParam1",
              "/${Stage}/${AppName}/MyParam2"
          ],
          "secretsmanager": [
              "/${Stage}/${AppName}/MySecret1",
              "/${Stage}/${AppName}/MySecret2"
          ]
        }
```

## Usage
See [Configuration Methods](#configuration-methods) for the different ways to setup the environment and access SSM Parameters and SecretsManager Secrets values.

```python
from awsparameters import AppConfig

# (optional) Create a boto3 session outside the class 
session = boto3.Session(region_name=AWS_REGION)

# Retrieve the Parameter Mappings from SSM Parameter Store
mappings_path = "/dev/myapp/MyParamMappings"

# Create the AppConfig object from the mappings path
app = AppConfig(
    mappings_path=mappings_path, 
    boto3_session=session)
```


To see all the available parameters and secrets by namespace, you can access the `map` attribute:
```python
# print all available parameters
app.map

# output
{
    "ssm": [
        "/dev/myapp/MyParam1",
        "/dev/myapp/MyParam2"
    ],
    "secretsmanager": [
        "/dev/myapp/MySecret1",
        "/dev/myapp/MySecret2"
    ]
}
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

## Unit Tests
Follow the steps above to create a Python virtual environment. Run tests with the following command.
```bash
coverage run -m pytest
```

## Authors
**Primary Contact:** [@chrisammon3000](https://github.com/chrisammon3000)

## License
This library is licensed under the MIT-0 License. See the LICENSE file.