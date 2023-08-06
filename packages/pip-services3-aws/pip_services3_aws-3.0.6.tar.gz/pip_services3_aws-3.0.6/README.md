# <img src="https://uploads-ssl.webflow.com/5ea5d3315186cf5ec60c3ee4/5edf1c94ce4c859f2b188094_logo.svg" alt="Pip.Services Logo" width="200"> <br/> AWS specific components for Python

This module is a part of the [Pip.Services](http://pipservices.org) polyglot microservices toolkit.

This module contains components for supporting work with the AWS cloud platform.

The module contains the following packages:
- **Build** - factories for constructing module components
- **Clients** - client components for working with Lambda AWS
- **Connect** - components of installation and connection settings
- **Container** - components for creating containers for Lambda server-side AWS functions
- **Count** - components of working with counters (metrics) with saving data in the CloudWatch AWS service
- **Log** - logging components with saving data in the CloudWatch AWS service


<a name="links"></a> Quick links:

* [Configuration](https://www.pipservices.org/recipies/configuration)
* [API Reference](https://pip-services3-python.github.io/pip-services3-aws-python/index.html)
* [Change Log](CHANGELOG.md)
* [Get Help](https://www.pipservices.org/community/help)
* [Contribute](https://www.pipservices.org/community/contribute)

## Use

Install the Python package as
```bash
pip install pip-services3-aws
```

## Develop

For development you shall install the following prerequisites:
* Python 3.7+
* Visual Studio Code or another IDE of your choice
* Docker

Install dependencies:
```bash
pip install -r requirements.txt
```

Run automated tests:
```bash
python test.py
```

Generate API documentation:
```bash
./docgen.ps1
```

Before committing changes run dockerized build and test as:
```bash
./build.ps1
./test.ps1
./clear.ps1
```

## Contacts

The Python version of Pip.Services is created and maintained by
- **Sergey Seroukhov**
- **Danil Prisiazhnyi**
