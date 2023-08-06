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
    Authentication as _Authentication_0a484e20,
    CIATriad as _CIATriad_013dde99,
    DataAsset as _DataAsset_e63154c8,
    Scope as _Scope_ef169782,
    TechnicalAsset as _TechnicalAsset_9e546017,
    TrustBoundary as _TrustBoundary_bc2215aa,
)


class Browser(
    _TechnicalAsset_9e546017,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdktg.plus.Browser",
):
    def __init__(
        self,
        scope_: constructs.Construct,
        id: builtins.str,
        *,
        cia_triad: _CIATriad_013dde99,
        scope: _Scope_ef169782,
        description: typing.Optional[builtins.str] = None,
        owner: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope_: -
        :param id: -
        :param cia_triad: 
        :param scope: 
        :param description: 
        :param owner: 
        '''
        props = BrowserProps(
            cia_triad=cia_triad, scope=scope, description=description, owner=owner
        )

        jsii.create(self.__class__, self, [scope_, id, props])


@jsii.data_type(
    jsii_type="cdktg.plus.BrowserProps",
    jsii_struct_bases=[],
    name_mapping={
        "cia_triad": "ciaTriad",
        "scope": "scope",
        "description": "description",
        "owner": "owner",
    },
)
class BrowserProps:
    def __init__(
        self,
        *,
        cia_triad: _CIATriad_013dde99,
        scope: _Scope_ef169782,
        description: typing.Optional[builtins.str] = None,
        owner: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param cia_triad: 
        :param scope: 
        :param description: 
        :param owner: 
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "cia_triad": cia_triad,
            "scope": scope,
        }
        if description is not None:
            self._values["description"] = description
        if owner is not None:
            self._values["owner"] = owner

    @builtins.property
    def cia_triad(self) -> _CIATriad_013dde99:
        result = self._values.get("cia_triad")
        assert result is not None, "Required property 'cia_triad' is missing"
        return typing.cast(_CIATriad_013dde99, result)

    @builtins.property
    def scope(self) -> _Scope_ef169782:
        result = self._values.get("scope")
        assert result is not None, "Required property 'scope' is missing"
        return typing.cast(_Scope_ef169782, result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def owner(self) -> typing.Optional[builtins.str]:
        result = self._values.get("owner")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BrowserProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="cdktg.plus.StorageType")
class StorageType(enum.Enum):
    CLOUD_PROVIDER = "CLOUD_PROVIDER"
    '''Cloud Provider (storage buckets or similar).'''
    CONTAINER_PLATFORM = "CONTAINER_PLATFORM"
    '''Container Platform (orchestration platform managed storage).'''
    DATABASE = "DATABASE"
    '''Database (SQL-DB, NoSQL-DB, object store or similar).'''
    FILESYSTEM = "FILESYSTEM"
    '''Filesystem (local or remote).'''
    IN_MEMORY = "IN_MEMORY"
    '''In-Memory (no persistent storage of secrets).'''
    SERVICE_REGISTRY = "SERVICE_REGISTRY"
    '''Service Registry.'''


class Vault(
    _TechnicalAsset_9e546017,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdktg.plus.Vault",
):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        authtentication: _Authentication_0a484e20,
        multi_tenant: builtins.bool,
        storage_type: StorageType,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
        trust_boundary: typing.Optional[_TrustBoundary_bc2215aa] = None,
        vendor: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param authtentication: 
        :param multi_tenant: 
        :param storage_type: 
        :param tags: 
        :param trust_boundary: 
        :param vendor: 
        '''
        props = VaultProps(
            authtentication=authtentication,
            multi_tenant=multi_tenant,
            storage_type=storage_type,
            tags=tags,
            trust_boundary=trust_boundary,
            vendor=vendor,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="isUsedBy")
    def is_used_by(self, client: _TechnicalAsset_9e546017) -> None:
        '''
        :param client: -
        '''
        return typing.cast(None, jsii.invoke(self, "isUsedBy", [client]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="configurationSecrets")
    def configuration_secrets(self) -> _DataAsset_e63154c8:
        return typing.cast(_DataAsset_e63154c8, jsii.get(self, "configurationSecrets"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vaultStorage")
    def vault_storage(self) -> typing.Optional[_TechnicalAsset_9e546017]:
        return typing.cast(typing.Optional[_TechnicalAsset_9e546017], jsii.get(self, "vaultStorage"))


@jsii.data_type(
    jsii_type="cdktg.plus.VaultProps",
    jsii_struct_bases=[],
    name_mapping={
        "authtentication": "authtentication",
        "multi_tenant": "multiTenant",
        "storage_type": "storageType",
        "tags": "tags",
        "trust_boundary": "trustBoundary",
        "vendor": "vendor",
    },
)
class VaultProps:
    def __init__(
        self,
        *,
        authtentication: _Authentication_0a484e20,
        multi_tenant: builtins.bool,
        storage_type: StorageType,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
        trust_boundary: typing.Optional[_TrustBoundary_bc2215aa] = None,
        vendor: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param authtentication: 
        :param multi_tenant: 
        :param storage_type: 
        :param tags: 
        :param trust_boundary: 
        :param vendor: 
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "authtentication": authtentication,
            "multi_tenant": multi_tenant,
            "storage_type": storage_type,
        }
        if tags is not None:
            self._values["tags"] = tags
        if trust_boundary is not None:
            self._values["trust_boundary"] = trust_boundary
        if vendor is not None:
            self._values["vendor"] = vendor

    @builtins.property
    def authtentication(self) -> _Authentication_0a484e20:
        result = self._values.get("authtentication")
        assert result is not None, "Required property 'authtentication' is missing"
        return typing.cast(_Authentication_0a484e20, result)

    @builtins.property
    def multi_tenant(self) -> builtins.bool:
        result = self._values.get("multi_tenant")
        assert result is not None, "Required property 'multi_tenant' is missing"
        return typing.cast(builtins.bool, result)

    @builtins.property
    def storage_type(self) -> StorageType:
        result = self._values.get("storage_type")
        assert result is not None, "Required property 'storage_type' is missing"
        return typing.cast(StorageType, result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[builtins.str]]:
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def trust_boundary(self) -> typing.Optional[_TrustBoundary_bc2215aa]:
        result = self._values.get("trust_boundary")
        return typing.cast(typing.Optional[_TrustBoundary_bc2215aa], result)

    @builtins.property
    def vendor(self) -> typing.Optional[builtins.str]:
        result = self._values.get("vendor")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VaultProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "Browser",
    "BrowserProps",
    "StorageType",
    "Vault",
    "VaultProps",
]

publication.publish()
