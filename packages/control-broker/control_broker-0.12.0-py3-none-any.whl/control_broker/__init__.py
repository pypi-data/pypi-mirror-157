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
import aws_cdk.aws_lambda
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
        api_access_log_group: typing.Optional[aws_cdk.aws_logs.LogGroup] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param api_access_log_group: 
        '''
        props = ApiProps(api_access_log_group=api_access_log_group)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="addInputHandler")
    def add_input_handler(
        self,
        input_handler: _BaseInputHandler_53a5a2b8,
        binding: "BaseApiBinding",
    ) -> None:
        '''
        :param input_handler: -
        :param binding: -
        '''
        return typing.cast(None, jsii.invoke(self, "addInputHandler", [input_handler, binding]))

    @jsii.member(jsii_name="configureAwsApiGatewayHTTPApiLogging")
    def _configure_aws_api_gateway_http_api_logging(self) -> None:
        return typing.cast(None, jsii.invoke(self, "configureAwsApiGatewayHTTPApiLogging", []))

    @jsii.member(jsii_name="getUrlForInputHandler")
    def get_url_for_input_handler(
        self,
        input_handler: _BaseInputHandler_53a5a2b8,
    ) -> builtins.str:
        '''
        :param input_handler: -
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "getUrlForInputHandler", [input_handler]))

    @jsii.member(jsii_name="setEvalEngine")
    def set_eval_engine(
        self,
        eval_engine: "BaseEvalEngine",
        binding: "BaseApiBinding",
    ) -> None:
        '''
        :param eval_engine: -
        :param binding: -
        '''
        return typing.cast(None, jsii.invoke(self, "setEvalEngine", [eval_engine, binding]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="accessLogRetention")
    def access_log_retention(self) -> aws_cdk.aws_logs.RetentionDays:
        return typing.cast(aws_cdk.aws_logs.RetentionDays, jsii.get(self, "accessLogRetention"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="apiAccessLogGroup")
    def api_access_log_group(self) -> aws_cdk.aws_logs.LogGroup:
        return typing.cast(aws_cdk.aws_logs.LogGroup, jsii.get(self, "apiAccessLogGroup"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="awsApiGatewayHTTPApi")
    def aws_api_gateway_http_api(self) -> aws_cdk.aws_apigatewayv2_alpha.HttpApi:
        return typing.cast(aws_cdk.aws_apigatewayv2_alpha.HttpApi, jsii.get(self, "awsApiGatewayHTTPApi"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="awsApiGatewayRestApi")
    def aws_api_gateway_rest_api(self) -> aws_cdk.aws_apigateway.RestApi:
        return typing.cast(aws_cdk.aws_apigateway.RestApi, jsii.get(self, "awsApiGatewayRestApi"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="evalEngineUrl")
    def _eval_engine_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "evalEngineUrl"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="evalEngineBinding")
    def _eval_engine_binding(self) -> "EvalEngineBindingConfiguration":
        return typing.cast("EvalEngineBindingConfiguration", jsii.get(self, "evalEngineBinding"))

    @_eval_engine_binding.setter
    def _eval_engine_binding(self, value: "EvalEngineBindingConfiguration") -> None:
        jsii.set(self, "evalEngineBinding", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="inputHandlerBindings")
    def _input_handler_bindings(self) -> "InputHandlerBindingConfigurations":
        return typing.cast("InputHandlerBindingConfigurations", jsii.get(self, "inputHandlerBindings"))

    @_input_handler_bindings.setter
    def _input_handler_bindings(
        self,
        value: "InputHandlerBindingConfigurations",
    ) -> None:
        jsii.set(self, "inputHandlerBindings", value)


@jsii.data_type(
    jsii_type="control-broker.ApiProps",
    jsii_struct_bases=[],
    name_mapping={"api_access_log_group": "apiAccessLogGroup"},
)
class ApiProps:
    def __init__(
        self,
        *,
        api_access_log_group: typing.Optional[aws_cdk.aws_logs.LogGroup] = None,
    ) -> None:
        '''
        :param api_access_log_group: 
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if api_access_log_group is not None:
            self._values["api_access_log_group"] = api_access_log_group

    @builtins.property
    def api_access_log_group(self) -> typing.Optional[aws_cdk.aws_logs.LogGroup]:
        result = self._values.get("api_access_log_group")
        return typing.cast(typing.Optional[aws_cdk.aws_logs.LogGroup], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApiProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="control-broker.AwsApiType")
class AwsApiType(enum.Enum):
    HTTP = "HTTP"
    REST = "REST"
    WEBSOCKET = "WEBSOCKET"


class BaseApiBinding(
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="control-broker.BaseApiBinding",
):
    '''Base class for an API Binding, which attaches an integration to an API and authorizes principals to invoke the integration via the API attachment.

    Defined abstractly since there are different types of APIs to attach integrations with
    and different principals to allow.
    '''

    def __init__(
        self,
        url_safe_name: builtins.str,
        api: Api,
        integration_target: "IIntegrationTarget",
    ) -> None:
        '''This should create an invocable URL with the given integration.

        :param url_safe_name: A name suitable for use in an integration's URL. Can contain slashes.
        :param api: The API to bind to.
        :param integration_target: The integration target to bind to the API via an integration.
        '''
        jsii.create(self.__class__, self, [url_safe_name, api, integration_target])

    @jsii.member(jsii_name="authorizePrincipalArn") # type: ignore[misc]
    @abc.abstractmethod
    def authorize_principal_arn(self, principal_arn: builtins.str) -> None:
        '''Give permission to a principal to call this API using this binding.

        This should be called after the binding has been added to all APIs.

        :param principal_arn: Principal to give calling permissions to.
        '''
        ...

    @jsii.member(jsii_name="makeIntegrationForIntegrationTarget") # type: ignore[misc]
    @abc.abstractmethod
    def _make_integration_for_integration_target(self) -> typing.Any:
        '''- Return an integration built for the integration target.'''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="api")
    def api(self) -> Api:
        '''The API to bind to.'''
        return typing.cast(Api, jsii.get(self, "api"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="apiType")
    @abc.abstractmethod
    def api_type(self) -> AwsApiType:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="integrationTarget")
    def integration_target(self) -> "IIntegrationTarget":
        '''The integration target to bind to the API via an integration.'''
        return typing.cast("IIntegrationTarget", jsii.get(self, "integrationTarget"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="method")
    @abc.abstractmethod
    def method(self) -> builtins.str:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="path")
    @abc.abstractmethod
    def path(self) -> builtins.str:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="urlSafeName")
    def url_safe_name(self) -> builtins.str:
        '''A name suitable for use in an integration's URL.

        Can contain slashes.
        '''
        return typing.cast(builtins.str, jsii.get(self, "urlSafeName"))


class _BaseApiBindingProxy(BaseApiBinding):
    @jsii.member(jsii_name="authorizePrincipalArn")
    def authorize_principal_arn(self, principal_arn: builtins.str) -> None:
        '''Give permission to a principal to call this API using this binding.

        This should be called after the binding has been added to all APIs.

        :param principal_arn: Principal to give calling permissions to.
        '''
        return typing.cast(None, jsii.invoke(self, "authorizePrincipalArn", [principal_arn]))

    @jsii.member(jsii_name="makeIntegrationForIntegrationTarget")
    def _make_integration_for_integration_target(self) -> typing.Any:
        '''- Return an integration built for the integration target.'''
        return typing.cast(typing.Any, jsii.invoke(self, "makeIntegrationForIntegrationTarget", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="apiType")
    def api_type(self) -> AwsApiType:
        return typing.cast(AwsApiType, jsii.get(self, "apiType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="method")
    def method(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "method"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="path")
    def path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "path"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, BaseApiBinding).__jsii_proxy_class__ = lambda : _BaseApiBindingProxy


@jsii.data_type(
    jsii_type="control-broker.BaseApiBindingProps",
    jsii_struct_bases=[],
    name_mapping={"integration": "integration"},
)
class BaseApiBindingProps:
    def __init__(self, *, integration: typing.Any) -> None:
        '''
        :param integration: 
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "integration": integration,
        }

    @builtins.property
    def integration(self) -> typing.Any:
        result = self._values.get("integration")
        assert result is not None, "Required property 'integration' is missing"
        return typing.cast(typing.Any, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BaseApiBindingProps(%s)" % ", ".join(
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
        api: Api,
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
    def __init__(self, *, api: Api) -> None:
        '''
        :param api: 
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "api": api,
        }

    @builtins.property
    def api(self) -> Api:
        result = self._values.get("api")
        assert result is not None, "Required property 'api' is missing"
        return typing.cast(Api, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ControlBrokerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="control-broker.EvalEngineBindingConfiguration",
    jsii_struct_bases=[],
    name_mapping={"binding": "binding", "eval_engine": "evalEngine"},
)
class EvalEngineBindingConfiguration:
    def __init__(
        self,
        *,
        binding: typing.Optional[BaseApiBinding] = None,
        eval_engine: typing.Optional["BaseEvalEngine"] = None,
    ) -> None:
        '''
        :param binding: 
        :param eval_engine: 
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if binding is not None:
            self._values["binding"] = binding
        if eval_engine is not None:
            self._values["eval_engine"] = eval_engine

    @builtins.property
    def binding(self) -> typing.Optional[BaseApiBinding]:
        result = self._values.get("binding")
        return typing.cast(typing.Optional[BaseApiBinding], result)

    @builtins.property
    def eval_engine(self) -> typing.Optional["BaseEvalEngine"]:
        result = self._values.get("eval_engine")
        return typing.cast(typing.Optional["BaseEvalEngine"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EvalEngineBindingConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class HttpApiBinding(
    BaseApiBinding,
    metaclass=jsii.JSIIMeta,
    jsii_type="control-broker.HttpApiBinding",
):
    def __init__(
        self,
        url_safe_name: builtins.str,
        api: Api,
        integration_target: "IIntegrationTarget",
    ) -> None:
        '''
        :param url_safe_name: -
        :param api: -
        :param integration_target: -
        '''
        jsii.create(self.__class__, self, [url_safe_name, api, integration_target])

    @jsii.member(jsii_name="authorizePrincipalArn")
    def authorize_principal_arn(self, principal_arn: builtins.str) -> None:
        '''Give permission to a principal to call this API using this binding.

        This should be called after the binding has been added to all APIs.

        :param principal_arn: -
        '''
        return typing.cast(None, jsii.invoke(self, "authorizePrincipalArn", [principal_arn]))

    @jsii.member(jsii_name="makeIntegrationForIntegrationTarget")
    def _make_integration_for_integration_target(self) -> typing.Any:
        '''Note: JSII complains if we make the return type HTTPRouteIntegration, ostensibly because of its restrictions on Generics.'''
        return typing.cast(typing.Any, jsii.invoke(self, "makeIntegrationForIntegrationTarget", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="apiType")
    def api_type(self) -> AwsApiType:
        return typing.cast(AwsApiType, jsii.get(self, "apiType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="method")
    def method(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "method"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="path")
    def path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "path"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="route")
    def route(self) -> aws_cdk.aws_apigatewayv2_alpha.HttpRoute:
        return typing.cast(aws_cdk.aws_apigatewayv2_alpha.HttpRoute, jsii.get(self, "route"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="authorizedPrincipalArns")
    def _authorized_principal_arns(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "authorizedPrincipalArns"))

    @_authorized_principal_arns.setter
    def _authorized_principal_arns(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "authorizedPrincipalArns", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="routes")
    def _routes(self) -> typing.List[aws_cdk.aws_apigatewayv2_alpha.HttpRoute]:
        return typing.cast(typing.List[aws_cdk.aws_apigatewayv2_alpha.HttpRoute], jsii.get(self, "routes"))

    @_routes.setter
    def _routes(
        self,
        value: typing.List[aws_cdk.aws_apigatewayv2_alpha.HttpRoute],
    ) -> None:
        jsii.set(self, "routes", value)


@jsii.data_type(
    jsii_type="control-broker.HttpApiBindingAddToApiOptions",
    jsii_struct_bases=[],
    name_mapping={},
)
class HttpApiBindingAddToApiOptions:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "HttpApiBindingAddToApiOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.interface(jsii_type="control-broker.IIntegrationTarget")
class IIntegrationTarget(typing_extensions.Protocol):
    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="integrationTargetType")
    def integration_target_type(self) -> "IntegrationTargetType":
        ...


class _IIntegrationTargetProxy:
    __jsii_type__: typing.ClassVar[str] = "control-broker.IIntegrationTarget"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="integrationTargetType")
    def integration_target_type(self) -> "IntegrationTargetType":
        return typing.cast("IntegrationTargetType", jsii.get(self, "integrationTargetType"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IIntegrationTarget).__jsii_proxy_class__ = lambda : _IIntegrationTargetProxy


@jsii.interface(jsii_type="control-broker.ILambdaIntegrationTarget")
class ILambdaIntegrationTarget(IIntegrationTarget, typing_extensions.Protocol):
    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="handler")
    def handler(self) -> aws_cdk.aws_lambda.Function:
        ...


class _ILambdaIntegrationTargetProxy(
    jsii.proxy_for(IIntegrationTarget) # type: ignore[misc]
):
    __jsii_type__: typing.ClassVar[str] = "control-broker.ILambdaIntegrationTarget"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="handler")
    def handler(self) -> aws_cdk.aws_lambda.Function:
        return typing.cast(aws_cdk.aws_lambda.Function, jsii.get(self, "handler"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, ILambdaIntegrationTarget).__jsii_proxy_class__ = lambda : _ILambdaIntegrationTargetProxy


@jsii.data_type(
    jsii_type="control-broker.InputHandlerBindingConfiguration",
    jsii_struct_bases=[],
    name_mapping={"binding": "binding", "input_handler": "inputHandler"},
)
class InputHandlerBindingConfiguration:
    def __init__(
        self,
        *,
        binding: BaseApiBinding,
        input_handler: _BaseInputHandler_53a5a2b8,
    ) -> None:
        '''
        :param binding: 
        :param input_handler: 
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "binding": binding,
            "input_handler": input_handler,
        }

    @builtins.property
    def binding(self) -> BaseApiBinding:
        result = self._values.get("binding")
        assert result is not None, "Required property 'binding' is missing"
        return typing.cast(BaseApiBinding, result)

    @builtins.property
    def input_handler(self) -> _BaseInputHandler_53a5a2b8:
        result = self._values.get("input_handler")
        assert result is not None, "Required property 'input_handler' is missing"
        return typing.cast(_BaseInputHandler_53a5a2b8, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "InputHandlerBindingConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="control-broker.InputHandlerBindingConfigurations",
    jsii_struct_bases=[],
    name_mapping={},
)
class InputHandlerBindingConfigurations:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "InputHandlerBindingConfigurations(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="control-broker.IntegrationTargetType")
class IntegrationTargetType(enum.Enum):
    LAMBDA = "LAMBDA"
    STEP_FUNCTION = "STEP_FUNCTION"


@jsii.implements(IIntegrationTarget)
class BaseEvalEngine(
    constructs.Construct,
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="control-broker.BaseEvalEngine",
):
    def __init__(self, scope: constructs.Construct, id: builtins.str) -> None:
        '''Creates a new construct node.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings. If the ID includes a path separator (``/``), then it will be replaced by double dash ``--``.
        '''
        jsii.create(self.__class__, self, [scope, id])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="integrationTargetType")
    @abc.abstractmethod
    def integration_target_type(self) -> IntegrationTargetType:
        ...


class _BaseEvalEngineProxy(BaseEvalEngine):
    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="integrationTargetType")
    def integration_target_type(self) -> IntegrationTargetType:
        return typing.cast(IntegrationTargetType, jsii.get(self, "integrationTargetType"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, BaseEvalEngine).__jsii_proxy_class__ = lambda : _BaseEvalEngineProxy


@jsii.implements(ILambdaIntegrationTarget)
class OpaEvalEngine(
    BaseEvalEngine,
    metaclass=jsii.JSIIMeta,
    jsii_type="control-broker.OpaEvalEngine",
):
    def __init__(self, scope: constructs.Construct, id: builtins.str) -> None:
        '''
        :param scope: -
        :param id: -
        '''
        jsii.create(self.__class__, self, [scope, id])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="handler")
    def handler(self) -> aws_cdk.aws_lambda.Function:
        return typing.cast(aws_cdk.aws_lambda.Function, jsii.get(self, "handler"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="integrationTargetType")
    def integration_target_type(self) -> IntegrationTargetType:
        return typing.cast(IntegrationTargetType, jsii.get(self, "integrationTargetType"))


__all__ = [
    "Api",
    "ApiProps",
    "AwsApiType",
    "BaseApiBinding",
    "BaseApiBindingProps",
    "BaseEvalEngine",
    "ControlBroker",
    "ControlBrokerProps",
    "EvalEngineBindingConfiguration",
    "HttpApiBinding",
    "HttpApiBindingAddToApiOptions",
    "IIntegrationTarget",
    "ILambdaIntegrationTarget",
    "InputHandlerBindingConfiguration",
    "InputHandlerBindingConfigurations",
    "IntegrationTargetType",
    "OpaEvalEngine",
    "input_handlers",
]

publication.publish()

# Loading modules to ensure their types are registered with the jsii runtime library
from . import input_handlers
