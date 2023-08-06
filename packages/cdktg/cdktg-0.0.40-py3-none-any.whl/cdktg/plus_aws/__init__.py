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
from .. import (
    CIATriad as _CIATriad_013dde99,
    TechnicalAsset as _TechnicalAsset_9e546017,
    TrustBoundary as _TrustBoundary_bc2215aa,
)


class ApplicationLoadBalancer(
    _TechnicalAsset_9e546017,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdktg.plus_aws.ApplicationLoadBalancer",
):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        cia_triad: _CIATriad_013dde99,
        description: typing.Optional[builtins.str] = None,
        security_group: typing.Optional["SecurityGroup"] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
        waf: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param cia_triad: 
        :param description: 
        :param security_group: 
        :param tags: 
        :param waf: 
        '''
        props = ApplicationLoadBalancerProps(
            cia_triad=cia_triad,
            description=description,
            security_group=security_group,
            tags=tags,
            waf=waf,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityGroup")
    def security_group(self) -> "SecurityGroup":
        return typing.cast("SecurityGroup", jsii.get(self, "securityGroup"))


@jsii.data_type(
    jsii_type="cdktg.plus_aws.ApplicationLoadBalancerProps",
    jsii_struct_bases=[],
    name_mapping={
        "cia_triad": "ciaTriad",
        "description": "description",
        "security_group": "securityGroup",
        "tags": "tags",
        "waf": "waf",
    },
)
class ApplicationLoadBalancerProps:
    def __init__(
        self,
        *,
        cia_triad: _CIATriad_013dde99,
        description: typing.Optional[builtins.str] = None,
        security_group: typing.Optional["SecurityGroup"] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
        waf: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param cia_triad: 
        :param description: 
        :param security_group: 
        :param tags: 
        :param waf: 
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "cia_triad": cia_triad,
        }
        if description is not None:
            self._values["description"] = description
        if security_group is not None:
            self._values["security_group"] = security_group
        if tags is not None:
            self._values["tags"] = tags
        if waf is not None:
            self._values["waf"] = waf

    @builtins.property
    def cia_triad(self) -> _CIATriad_013dde99:
        result = self._values.get("cia_triad")
        assert result is not None, "Required property 'cia_triad' is missing"
        return typing.cast(_CIATriad_013dde99, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def security_group(self) -> typing.Optional["SecurityGroup"]:
        result = self._values.get("security_group")
        return typing.cast(typing.Optional["SecurityGroup"], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[builtins.str]]:
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def waf(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("waf")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ApplicationLoadBalancerProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Cloud(
    _TrustBoundary_bc2215aa,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdktg.plus_aws.Cloud",
):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param description: 
        :param tags: 
        '''
        props = CloudProps(description=description, tags=tags)

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="cdktg.plus_aws.CloudProps",
    jsii_struct_bases=[],
    name_mapping={"description": "description", "tags": "tags"},
)
class CloudProps:
    def __init__(
        self,
        *,
        description: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param description: 
        :param tags: 
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if description is not None:
            self._values["description"] = description
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[builtins.str]]:
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SecurityGroup(
    _TrustBoundary_bc2215aa,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdktg.plus_aws.SecurityGroup",
):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param description: 
        :param tags: 
        '''
        props = SecurityGroupProps(description=description, tags=tags)

        jsii.create(self.__class__, self, [scope, id, props])


@jsii.data_type(
    jsii_type="cdktg.plus_aws.SecurityGroupProps",
    jsii_struct_bases=[],
    name_mapping={"description": "description", "tags": "tags"},
)
class SecurityGroupProps:
    def __init__(
        self,
        *,
        description: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param description: 
        :param tags: 
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if description is not None:
            self._values["description"] = description
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[builtins.str]]:
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityGroupProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "ApplicationLoadBalancer",
    "ApplicationLoadBalancerProps",
    "Cloud",
    "CloudProps",
    "SecurityGroup",
    "SecurityGroupProps",
]

publication.publish()
