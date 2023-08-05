import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from .._jsii import *

import constructs


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
    @jsii.member(jsii_name="urlSafeName")
    @abc.abstractmethod
    def url_safe_name(self) -> builtins.str:
        '''Return a name for this input handler that is safe for use in the path of a URL.'''
        ...


class _BaseInputHandlerProxy(BaseInputHandler):
    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="urlSafeName")
    def url_safe_name(self) -> builtins.str:
        '''Return a name for this input handler that is safe for use in the path of a URL.'''
        return typing.cast(builtins.str, jsii.get(self, "urlSafeName"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, BaseInputHandler).__jsii_proxy_class__ = lambda : _BaseInputHandlerProxy


class CloudFormationInputHandler(
    BaseInputHandler,
    metaclass=jsii.JSIIMeta,
    jsii_type="control-broker.inputHandlers.CloudFormationInputHandler",
):
    def __init__(self, scope: constructs.Construct, id: builtins.str) -> None:
        '''Creates a new construct node.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings. If the ID includes a path separator (``/``), then it will be replaced by double dash ``--``.
        '''
        jsii.create(self.__class__, self, [scope, id])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="urlSafeName")
    def url_safe_name(self) -> builtins.str:
        '''Return a name for this input handler that is safe for use in the path of a URL.'''
        return typing.cast(builtins.str, jsii.get(self, "urlSafeName"))


__all__ = [
    "BaseInputHandler",
    "CloudFormationInputHandler",
]

publication.publish()
