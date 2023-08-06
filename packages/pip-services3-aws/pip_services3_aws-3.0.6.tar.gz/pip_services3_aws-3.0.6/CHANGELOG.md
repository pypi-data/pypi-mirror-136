# <img src="https://uploads-ssl.webflow.com/5ea5d3315186cf5ec60c3ee4/5edf1c94ce4c859f2b188094_logo.svg" alt="Pip.Services Logo" width="200">
<br/> AWS specific components for Python Changelog

## <a name="3.0.6"></a> 3.0.6 (2022-26-01)

# Bug fixes
* Optimize imports
* Fixed dependencies

## <a name="3.0.3-3.0.5"></a> 3.0.3-3.0.5 (2021-09-03)

# Bug fixes
* Fixed json conversion in _invoke
* Fixed signal event for Container on Linux
* Fixed base name for CommandableLambda

## <a name="3.0.2"></a> 3.0.2 (2021-08-28)

# Bug fixes
* Fixed boto3 requirement

## <a name="3.0.1"></a> 3.0.1 (2021-08-28)

### Features
Rename _register to register method

## <a name="3.0.0"></a> 3.0.0 (2021-07-30)

### Features
* *build** - factories for constructing module components
* *clients** - client components for working with Lambda AWS
* *connect** - components of installation and connection settings
* *container** - components for creating containers for Lambda server-side AWS functions
* *count** - components of working with counters (metrics) with saving data in the CloudWatch AWS service
* *log** - logging components with saving data in the CloudWatch AWS service