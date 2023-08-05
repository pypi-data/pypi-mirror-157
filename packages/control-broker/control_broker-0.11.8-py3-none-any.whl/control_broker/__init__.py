'''
# Control Broker

*Give everyone in your organization subsecond security and compliance decisions based on the organization's latest policies.*

## Contributing

Please see [CONTRIBUTING.md](./CONTRIBUTING.md).

## Features

* Runs a Policy as Code service as a serverless AWS application - you bring the policies, and Control Broker helps you store, organize, and use them - plus it helps you monitor, and analyze their usage.
* Defined in the AWS Python CDK for push-button, repeatable deployment.
* Can be invoked from anywhere in your environment that can invoke an API Gateway API.
* Supports policies written for Open Policy Agent (CloudFormation Guard planned).
* Also helps with notifications, auditing, and analysis of discovered compliance issues.

## Example use cases

* [Using the Control Broker from a CodePipeline application pipeline to block deployment of non-compliant CDK resources](https://github.com/VerticalRelevance/control-broker-codepipeline-example)
* [Using the Control Broker to detect non-compliant changes to deployed resources with AWS Config](https://github.com/VerticalRelevance/control-broker-consumer-example-config)
* [Using the Control Broker from a development machine to evaluate IaC against the organization's latest security policies as it is being written](https://github.com/VerticalRelevance/control-broker-consumer-example-local-dev)

## Deploying Your Own Control Broker

<!--### Upload your secret config file--><!--The Control Broker needs some secret values to be available in its environment. These are stored in a Secrets Manager Secret as a JSON--><!--blob, and the Control Broker's deployment mechanisms grab these values as they need to.--><!--Before proceeding, you'll have to copy [our example secrets file](./supplementary_files/) to a secure location on your machine and replace--><!--the values in it with your own. Then, [create a Secret--><!--in Secrets--><!--Manager](https://docs.aws.amazon.com/secretsmanager/latest/userguide/tutorials_basic.html#tutorial-basic-step1)--><!--called "control-broker/secret-config" with this JSON text as its value.--><!--![Using the SecretsManager console to create the secret value](docs/diagrams/images/secretsmanager-console-secret-config.png)--><!--![Using the SecretsManager console to name the secret and give it a description](docs/diagrams/images/secretsmanager-console-secret-config-name-page.png)--><!--Here are some helpful hints about what to put in these values:--><!--> Note: You can change the name of the secret that Control Broker uses by changing the value of the "control-broker/secret-config/secrets-manager-secret-id" context variable.-->

### Deploy the CDK app

Install the [AWS CDK Toolkit
v2](https://docs.aws.amazon.com/cdk/v2/guide/cli.html) CLI tool.

If you encounter issues running the `cdk` commands below, check the version of
`aws-cdk-lib` from [./requirements.txt](./requirements.txt) for the exact
version of the CDK library used in this repo. The latest v2 version of the CDK
Toolkit should be compatible, but try installing the CDK Toolkit version
matching `requirements.txt` before trying other things to resolve your issues.

Clone this repo to your machine before proceeding.

Follow the setup steps below to properly configure the environment and first
deployment of the infrastructure.

To manually create a virtualenv on MacOS and Linux:

`$ python3 -m venv .venv`

After the init process completes and the virtualenv is created, you can use the
following step to activate your virtualenv.

`$ source .venv/bin/activate`

If you are on a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

`$ pip install -r requirements.txt`

[Bootstrap](https://docs.aws.amazon.com/cdk/v2/guide/cli.html#cli-bootstrap) the
cdk app:

`cdk bootstrap`

At this point you can
[deploy](https://docs.aws.amazon.com/cdk/v2/guide/cli.html#cli-deploy) the CDK
app for this blueprint:

`$ cdk deploy`

After running `cdk deploy`, the Control Broker will be set up.

## Next Steps

Try launching one of the [Example use cases](./README.md#example-use-cases)!
'''
import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from ._jsii import *

import aws_cdk.aws_apigateway
import aws_cdk.aws_apigatewayv2_alpha
import aws_cdk.aws_logs
import constructs
from .input_handlers import BaseInputHandler as _BaseInputHandler_53a5a2b8


class Api(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="control-broker.Api",
):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        eval_engine: "EvalEngine",
        access_log_retention: typing.Optional[aws_cdk.aws_logs.RetentionDays] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param eval_engine: 
        :param access_log_retention: 
        '''
        props = ApiProps(
            eval_engine=eval_engine, access_log_retention=access_log_retention
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accessLogRetention")
    def access_log_retention(self) -> aws_cdk.aws_logs.RetentionDays:
        return typing.cast(aws_cdk.aws_logs.RetentionDays, jsii.get(self, "accessLogRetention"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="awsApiGatewayHTTPApi")
    def aws_api_gateway_http_api(self) -> aws_cdk.aws_apigatewayv2_alpha.HttpApi:
        return typing.cast(aws_cdk.aws_apigatewayv2_alpha.HttpApi, jsii.get(self, "awsApiGatewayHTTPApi"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="awsApiGatewayRestApi")
    def aws_api_gateway_rest_api(self) -> aws_cdk.aws_apigateway.RestApi:
        return typing.cast(aws_cdk.aws_apigateway.RestApi, jsii.get(self, "awsApiGatewayRestApi"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="externalBaseUrl")
    def external_base_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "externalBaseUrl"))


@jsii.data_type(
    jsii_type="control-broker.ApiProps",
    jsii_struct_bases=[],
    name_mapping={
        "eval_engine": "evalEngine",
        "access_log_retention": "accessLogRetention",
    },
)
class ApiProps:
    def __init__(
        self,
        *,
        eval_engine: "EvalEngine",
        access_log_retention: typing.Optional[aws_cdk.aws_logs.RetentionDays] = None,
    ) -> None:
        '''
        :param eval_engine: 
        :param access_log_retention: 
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "eval_engine": eval_engine,
        }
        if access_log_retention is not None:
            self._values["access_log_retention"] = access_log_retention

    @builtins.property
    def eval_engine(self) -> "EvalEngine":
        result = self._values.get("eval_engine")
        assert result is not None, "Required property 'eval_engine' is missing"
        return typing.cast("EvalEngine", result)

    @builtins.property
    def access_log_retention(self) -> typing.Optional[aws_cdk.aws_logs.RetentionDays]:
        result = self._values.get("access_log_retention")
        return typing.cast(typing.Optional[aws_cdk.aws_logs.RetentionDays], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApiProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ControlBroker(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="control-broker.ControlBroker",
):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        api: typing.Optional[Api] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param api: 
        '''
        props = ControlBrokerProps(api=api)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="getUrlForInputHandler")
    def get_url_for_input_handler(
        self,
        input_handler: _BaseInputHandler_53a5a2b8,
    ) -> builtins.str:
        '''
        :param input_handler: -
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "getUrlForInputHandler", [input_handler]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="api")
    def api(self) -> Api:
        return typing.cast(Api, jsii.get(self, "api"))


@jsii.data_type(
    jsii_type="control-broker.ControlBrokerProps",
    jsii_struct_bases=[],
    name_mapping={"api": "api"},
)
class ControlBrokerProps:
    def __init__(self, *, api: typing.Optional[Api] = None) -> None:
        '''
        :param api: 
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if api is not None:
            self._values["api"] = api

    @builtins.property
    def api(self) -> typing.Optional[Api]:
        result = self._values.get("api")
        return typing.cast(typing.Optional[Api], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ControlBrokerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class EvalEngine(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="control-broker.EvalEngine",
):
    def __init__(self, scope: constructs.Construct, id: builtins.str) -> None:
        '''Creates a new construct node.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings. If the ID includes a path separator (``/``), then it will be replaced by double dash ``--``.
        '''
        jsii.create(self.__class__, self, [scope, id])


__all__ = [
    "Api",
    "ApiProps",
    "ControlBroker",
    "ControlBrokerProps",
    "EvalEngine",
    "input_handlers",
]

publication.publish()

# Loading modules to ensure their types are registered with the jsii runtime library
from . import input_handlers
