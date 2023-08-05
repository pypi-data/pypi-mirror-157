import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from .._jsii import *

import aws_cdk.aws_lambda
import constructs
from .. import (
    IIntegrationTarget as _IIntegrationTarget_51639b90,
    ILambdaIntegrationTarget as _ILambdaIntegrationTarget_098612cb,
    IntegrationTargetType as _IntegrationTargetType_253153a8,
)


@jsii.implements(_IIntegrationTarget_51639b90)
class BaseInputHandler(
    constructs.Construct,
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="control-broker.inputHandlers.BaseInputHandler",
):
    def __init__(self, scope: constructs.Construct, id: builtins.str) -> None:
        '''Creates a new construct node.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings. If the ID includes a path separator (``/``), then it will be replaced by double dash ``--``.
        '''
        jsii.create(self.__class__, self, [scope, id])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="evalEngineCallerPrincipalArn")
    @abc.abstractmethod
    def eval_engine_caller_principal_arn(self) -> builtins.str:
        '''ARN of the principal that will call the EvalEngine endpoint.'''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="integrationTargetType")
    @abc.abstractmethod
    def integration_target_type(self) -> _IntegrationTargetType_253153a8:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="urlSafeName")
    @abc.abstractmethod
    def url_safe_name(self) -> builtins.str:
        '''Return a name for this input handler that is safe for use in the path of a URL.'''
        ...


class _BaseInputHandlerProxy(BaseInputHandler):
    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="evalEngineCallerPrincipalArn")
    def eval_engine_caller_principal_arn(self) -> builtins.str:
        '''ARN of the principal that will call the EvalEngine endpoint.'''
        return typing.cast(builtins.str, jsii.get(self, "evalEngineCallerPrincipalArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="integrationTargetType")
    def integration_target_type(self) -> _IntegrationTargetType_253153a8:
        return typing.cast(_IntegrationTargetType_253153a8, jsii.get(self, "integrationTargetType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="urlSafeName")
    def url_safe_name(self) -> builtins.str:
        '''Return a name for this input handler that is safe for use in the path of a URL.'''
        return typing.cast(builtins.str, jsii.get(self, "urlSafeName"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, BaseInputHandler).__jsii_proxy_class__ = lambda : _BaseInputHandlerProxy


@jsii.implements(_ILambdaIntegrationTarget_098612cb)
class CloudFormationInputHandler(
    BaseInputHandler,
    metaclass=jsii.JSIIMeta,
    jsii_type="control-broker.inputHandlers.CloudFormationInputHandler",
):
    def __init__(self, scope: constructs.Construct, id: builtins.str) -> None:
        '''
        :param scope: -
        :param id: -
        '''
        jsii.create(self.__class__, self, [scope, id])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="evalEngineCallerPrincipalArn")
    def eval_engine_caller_principal_arn(self) -> builtins.str:
        '''ARN of the principal that will call the EvalEngine endpoint.'''
        return typing.cast(builtins.str, jsii.get(self, "evalEngineCallerPrincipalArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="handler")
    def handler(self) -> aws_cdk.aws_lambda.Function:
        return typing.cast(aws_cdk.aws_lambda.Function, jsii.get(self, "handler"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="integrationTargetType")
    def integration_target_type(self) -> _IntegrationTargetType_253153a8:
        return typing.cast(_IntegrationTargetType_253153a8, jsii.get(self, "integrationTargetType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="urlSafeName")
    def url_safe_name(self) -> builtins.str:
        '''Return a name for this input handler that is safe for use in the path of a URL.'''
        return typing.cast(builtins.str, jsii.get(self, "urlSafeName"))


@jsii.data_type(
    jsii_type="control-broker.inputHandlers.InputHandlerIntegrationContext",
    jsii_struct_bases=[],
    name_mapping={"external_url": "externalUrl"},
)
class InputHandlerIntegrationContext:
    def __init__(self, *, external_url: builtins.str) -> None:
        '''
        :param external_url: 
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "external_url": external_url,
        }

    @builtins.property
    def external_url(self) -> builtins.str:
        result = self._values.get("external_url")
        assert result is not None, "Required property 'external_url' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "InputHandlerIntegrationContext(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "BaseInputHandler",
    "CloudFormationInputHandler",
    "InputHandlerIntegrationContext",
]

publication.publish()
