'''
# cdk-threagile (cdktg)

![Build](https://github.com/hupe1980/cdk-threagile/workflows/build/badge.svg)
![Release](https://github.com/hupe1980/cdk-threagile/workflows/release/badge.svg)

> Agile Threat Modeling as Code

CDK Constructs for [threagile](https://threagile.io/)

## Installation

TypeScript/JavaScript:

```bash
npm i cdktg
```

Python:

```bash
pip install cdktg
```

## How to use

Initialize a project:

```bash
mkdir threagile
cd threagile
cdktg init
```

### Threat Model written in typescript:

```typescript
// threagile.ts

const project = new Project();

const model = new Model(project, 'Model Stub', {
    title: 'Model Stub',
    version: '1.0.0',
    date: '2020-03-31',
    author: new Author({
        name: 'John Doe',
    }),
    businessCriticality: BusinessCriticality.IMPORTANT,
});

const someData = new DataAsset(model, 'Some Data Asset', {
    description: 'Some Description',
    usage: Usage.BUSINESS,
    origin: 'Some Origin',
    owner: 'Some Owner',
    quantity: Quantity.MANY,
    ciaTriad: new CIATriad({
        confidentiality: Confidentiality.CONFIDENTIAL,
        integrity: Integrity.CRITICAL,
        availability: Availability.OPERATIONAL,
    }),
});

const someTrustBoundary = new TrustBoundary(model, 'Some Trust Boundary', {
    description: 'Some Description',
    type: TrustBoundaryType.NETWORK_DEDICATED_HOSTER,
});

const someTechnicalAsset = new TechnicalAsset(model, 'Some Technical Asset', {
    trustBoundary: someTrustBoundary,
    description: 'Some Description',
    type: TechnicalAssetType.PROCESS,
    usage: Usage.BUSINESS,
    humanUse: false,
    size: Size.COMPONENT,
    technology: Technology.WEB_SERVICE_REST,
    internet: false,
    machine: Machine.VIRTUAL,
    encryption: Encryption.NONE,
    owner: 'Some Owner',
    ciaTriad: new CIATriad({
        confidentiality: Confidentiality.CONFIDENTIAL,
        integrity: Integrity.CRITICAL,
        availability: Availability.CRITICAL,
    }),
    multiTenant: false,
    redundant: true,
});

someTechnicalAsset.processes(someData);

const someOtherTechnicalAsset = new TechnicalAsset(model, 'Some Other Technical Asset', {
    description: 'Some Description',
    type: TechnicalAssetType.PROCESS,
    usage: Usage.BUSINESS,
    humanUse: false,
    size: Size.COMPONENT,
    technology: Technology.WEB_SERVICE_REST,
    tags: ['some-tag', 'some-other-tag'],
    internet: false,
    machine: Machine.VIRTUAL,
    encryption: Encryption.NONE,
    owner: 'Some Owner',
    ciaTriad: new CIATriad({
        confidentiality: Confidentiality.CONFIDENTIAL,
        integrity: Integrity.IMPORTANT,
        availability: Availability.IMPORTANT,
    }),
    multiTenant: false,
    redundant: true,
});

someOtherTechnicalAsset.processes(someData);

const someTraffic = someTechnicalAsset.communicatesWith('Some Traffic', someOtherTechnicalAsset, {
    description: 'Some Description',
    protocol: Protocol.HTTPS,
    authentication: Authentication.NONE,
    authorization: Authorization.NONE,
    vpn: false,
    ipFiltered: false,
    readonly: false,
    usage: Usage.BUSINESS,
});

someTraffic.sends(someData);

const someSharedRuntime = new SharedRuntime(model, "Some Shared Runtime", {
    description: "Some Description",
});

someSharedRuntime.runs(someTechnicalAsset, someOtherTechnicalAsset);

project.synth();
```

### High level constructs (cdktg/plus*)

```typescript
import { ApplicationLoadBalancer, Cloud } from "cdktg/plus-aws";

// ...

const alb = new ApplicationLoadBalancer(model, "ALB", {
    waf: true,
    ciaTriad: new CIATriad({
        availability: Availability.CRITICAL,
        integrity: Integrity.IMPORTANT,
        confidentiality: Confidentiality.CONFIDENTIAL,
    }),
});

const cloud = new Cloud(model, "AWS-Cloud");

cloud.addTechnicalAssets(alb);

// ...
```

### cdktg CLI commands:

A running thragile rest api server is required for the CLI. The URL can be passed by parameter `url` or environment variable `CDKTG_THREAGILE_BASE_URL`.

The examples can be used with the [threagile playground](https://run.threagile.io/)

```sh
cdktg [command]

Commands:
  cdktg init              create a new cdk-threagile project
  cdktg synth <filename>  synthesize the models
  cdktg ping              ping the api
  cdktg check             check the models
  cdktg analyze           analyze the models
  cdktg completion        generate completion script

Options:
  --help     Show help                               [boolean]
  --version  Show version number                     [boolean]
```

### Analyze outputs:

```sh
dist
└── ModelStub
    ├── data-asset-diagram.png
    ├── data-flow-diagram.png
    ├── report.pdf
    ├── risks.json
    ├── risks.xlsx
    ├── stats.json
    ├── tags.xlsx
    ├── technical-assets.json
    └── threagile.yaml
```

## Examples

See more complete [examples](https://github.com/hupe1980/cdk-threagile-examples).

## License

[MIT](LICENSE)
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

import constructs


class AbuseCase(metaclass=jsii.JSIIMeta, jsii_type="cdktg.AbuseCase"):
    def __init__(self, *, description: builtins.str, name: builtins.str) -> None:
        '''
        :param description: 
        :param name: 
        '''
        props = AbuseCaseProps(description=description, name=name)

        jsii.create(self.__class__, self, [props])

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="CPU_CYCLE_THEFT")
    def CPU_CYCLE_THEFT(cls) -> "AbuseCase":
        return typing.cast("AbuseCase", jsii.sget(cls, "CPU_CYCLE_THEFT"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="DENIAL_OF_SERVICE")
    def DENIAL_OF_SERVICE(cls) -> "AbuseCase":
        return typing.cast("AbuseCase", jsii.sget(cls, "DENIAL_OF_SERVICE"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="IDENTITY_THEFT")
    def IDENTITY_THEFT(cls) -> "AbuseCase":
        return typing.cast("AbuseCase", jsii.sget(cls, "IDENTITY_THEFT"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="PII_THEFT")
    def PII_THEFT(cls) -> "AbuseCase":
        return typing.cast("AbuseCase", jsii.sget(cls, "PII_THEFT"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="RANSOMWARE")
    def RANSOMWARE(cls) -> "AbuseCase":
        return typing.cast("AbuseCase", jsii.sget(cls, "RANSOMWARE"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))


@jsii.data_type(
    jsii_type="cdktg.AbuseCaseProps",
    jsii_struct_bases=[],
    name_mapping={"description": "description", "name": "name"},
)
class AbuseCaseProps:
    def __init__(self, *, description: builtins.str, name: builtins.str) -> None:
        '''
        :param description: 
        :param name: 
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "description": description,
            "name": name,
        }

    @builtins.property
    def description(self) -> builtins.str:
        result = self._values.get("description")
        assert result is not None, "Required property 'description' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AbuseCaseProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="cdktg.AnnotationMetadataEntryType")
class AnnotationMetadataEntryType(enum.Enum):
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"


class Annotations(metaclass=jsii.JSIIMeta, jsii_type="cdktg.Annotations"):
    '''Includes API for attaching annotations such as warning messages to constructs.'''

    @jsii.member(jsii_name="of") # type: ignore[misc]
    @builtins.classmethod
    def of(cls, scope: constructs.IConstruct) -> "Annotations":
        '''Returns the annotations API for a construct scope.

        :param scope: The scope.
        '''
        return typing.cast("Annotations", jsii.sinvoke(cls, "of", [scope]))

    @jsii.member(jsii_name="addError")
    def add_error(self, message: builtins.str) -> None:
        '''Adds an { "error":  } metadata entry to this construct.

        The toolkit will fail synthesis when errors are reported.

        :param message: The error message.
        '''
        return typing.cast(None, jsii.invoke(self, "addError", [message]))

    @jsii.member(jsii_name="addInfo")
    def add_info(self, message: builtins.str) -> None:
        '''Adds an info metadata entry to this construct.

        The CLI will display the info message when apps are synthesized.

        :param message: The info message.
        '''
        return typing.cast(None, jsii.invoke(self, "addInfo", [message]))

    @jsii.member(jsii_name="addWarning")
    def add_warning(self, message: builtins.str) -> None:
        '''Adds a warning metadata entry to this construct.

        The CLI will display the warning when an app is synthesized.
        In a future release the CLI might introduce a --strict flag which
        will then fail the synthesis if it encounters a warning.

        :param message: The warning message.
        '''
        return typing.cast(None, jsii.invoke(self, "addWarning", [message]))


class Aspects(metaclass=jsii.JSIIMeta, jsii_type="cdktg.Aspects"):
    '''Aspects can be applied to CDK tree scopes and can operate on the tree before synthesis.'''

    @jsii.member(jsii_name="of") # type: ignore[misc]
    @builtins.classmethod
    def of(cls, scope: constructs.IConstruct) -> "Aspects":
        '''Returns the ``Aspects`` object associated with a construct scope.

        :param scope: The scope for which these aspects will apply.
        '''
        return typing.cast("Aspects", jsii.sinvoke(cls, "of", [scope]))

    @jsii.member(jsii_name="add")
    def add(self, aspect: "IAspect") -> None:
        '''Adds an aspect to apply this scope before synthesis.

        :param aspect: The aspect to add.
        '''
        return typing.cast(None, jsii.invoke(self, "add", [aspect]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="all")
    def all(self) -> typing.List["IAspect"]:
        '''The list of aspects which were directly applied on this scope.'''
        return typing.cast(typing.List["IAspect"], jsii.get(self, "all"))


@jsii.enum(jsii_type="cdktg.Authentication")
class Authentication(enum.Enum):
    NONE = "NONE"
    CREDENTIALS = "CREDENTIALS"
    SESSION_ID = "SESSION_ID"
    TOKEN = "TOKEN"
    CLIENT_CERTIFICATE = "CLIENT_CERTIFICATE"
    TWO_FACTOR = "TWO_FACTOR"
    EXTERNALIZED = "EXTERNALIZED"


class Author(metaclass=jsii.JSIIMeta, jsii_type="cdktg.Author"):
    def __init__(
        self,
        *,
        name: builtins.str,
        homepage: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param name: 
        :param homepage: 
        '''
        props = AuthorProps(name=name, homepage=homepage)

        jsii.create(self.__class__, self, [props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="homepage")
    def homepage(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "homepage"))


@jsii.data_type(
    jsii_type="cdktg.AuthorProps",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "homepage": "homepage"},
)
class AuthorProps:
    def __init__(
        self,
        *,
        name: builtins.str,
        homepage: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param name: 
        :param homepage: 
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
        }
        if homepage is not None:
            self._values["homepage"] = homepage

    @builtins.property
    def name(self) -> builtins.str:
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def homepage(self) -> typing.Optional[builtins.str]:
        result = self._values.get("homepage")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AuthorProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="cdktg.Authorization")
class Authorization(enum.Enum):
    NONE = "NONE"
    TECHNICAL_USER = "TECHNICAL_USER"
    ENDUSER_IDENTITY_PROPAGATION = "ENDUSER_IDENTITY_PROPAGATION"


@jsii.enum(jsii_type="cdktg.Availability")
class Availability(enum.Enum):
    ARCHIVE = "ARCHIVE"
    OPERATIONAL = "OPERATIONAL"
    IMPORTANT = "IMPORTANT"
    CRITICAL = "CRITICAL"
    MISSION_CRITICAL = "MISSION_CRITICAL"


@jsii.enum(jsii_type="cdktg.BusinessCriticality")
class BusinessCriticality(enum.Enum):
    ARCHIVE = "ARCHIVE"
    OPERATIONAL = "OPERATIONAL"
    IMPORTANT = "IMPORTANT"
    CRITICAL = "CRITICAL"
    MISSION_CRITICAL = "MISSION_CRITICAL"


class CIATriad(metaclass=jsii.JSIIMeta, jsii_type="cdktg.CIATriad"):
    def __init__(
        self,
        *,
        availability: Availability,
        confidentiality: "Confidentiality",
        integrity: "Integrity",
        justification: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param availability: 
        :param confidentiality: 
        :param integrity: 
        :param justification: 
        '''
        props = CIATriadProps(
            availability=availability,
            confidentiality=confidentiality,
            integrity=integrity,
            justification=justification,
        )

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="hasHigherAvailabilty")
    def has_higher_availabilty(self, availability: Availability) -> builtins.bool:
        '''
        :param availability: -
        '''
        return typing.cast(builtins.bool, jsii.invoke(self, "hasHigherAvailabilty", [availability]))

    @jsii.member(jsii_name="hasHigherConfidentiality")
    def has_higher_confidentiality(
        self,
        confidentiality: "Confidentiality",
    ) -> builtins.bool:
        '''
        :param confidentiality: -
        '''
        return typing.cast(builtins.bool, jsii.invoke(self, "hasHigherConfidentiality", [confidentiality]))

    @jsii.member(jsii_name="hasHigherIntegrity")
    def has_higher_integrity(self, integrity: "Integrity") -> builtins.bool:
        '''
        :param integrity: -
        '''
        return typing.cast(builtins.bool, jsii.invoke(self, "hasHigherIntegrity", [integrity]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="availability")
    def availability(self) -> Availability:
        return typing.cast(Availability, jsii.get(self, "availability"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="confidentiality")
    def confidentiality(self) -> "Confidentiality":
        return typing.cast("Confidentiality", jsii.get(self, "confidentiality"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="integrity")
    def integrity(self) -> "Integrity":
        return typing.cast("Integrity", jsii.get(self, "integrity"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="justification")
    def justification(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "justification"))


@jsii.data_type(
    jsii_type="cdktg.CIATriadProps",
    jsii_struct_bases=[],
    name_mapping={
        "availability": "availability",
        "confidentiality": "confidentiality",
        "integrity": "integrity",
        "justification": "justification",
    },
)
class CIATriadProps:
    def __init__(
        self,
        *,
        availability: Availability,
        confidentiality: "Confidentiality",
        integrity: "Integrity",
        justification: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param availability: 
        :param confidentiality: 
        :param integrity: 
        :param justification: 
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "availability": availability,
            "confidentiality": confidentiality,
            "integrity": integrity,
        }
        if justification is not None:
            self._values["justification"] = justification

    @builtins.property
    def availability(self) -> Availability:
        result = self._values.get("availability")
        assert result is not None, "Required property 'availability' is missing"
        return typing.cast(Availability, result)

    @builtins.property
    def confidentiality(self) -> "Confidentiality":
        result = self._values.get("confidentiality")
        assert result is not None, "Required property 'confidentiality' is missing"
        return typing.cast("Confidentiality", result)

    @builtins.property
    def integrity(self) -> "Integrity":
        result = self._values.get("integrity")
        assert result is not None, "Required property 'integrity' is missing"
        return typing.cast("Integrity", result)

    @builtins.property
    def justification(self) -> typing.Optional[builtins.str]:
        result = self._values.get("justification")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CIATriadProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Communication(metaclass=jsii.JSIIMeta, jsii_type="cdktg.Communication"):
    def __init__(
        self,
        title: builtins.str,
        *,
        source: "TechnicalAsset",
        target: "TechnicalAsset",
        authentication: Authentication,
        authorization: Authorization,
        description: builtins.str,
        ip_filtered: builtins.bool,
        protocol: "Protocol",
        readonly: builtins.bool,
        usage: "Usage",
        vpn: builtins.bool,
    ) -> None:
        '''
        :param title: -
        :param source: 
        :param target: 
        :param authentication: 
        :param authorization: 
        :param description: 
        :param ip_filtered: 
        :param protocol: 
        :param readonly: 
        :param usage: 
        :param vpn: 
        '''
        props = CommunicationProps(
            source=source,
            target=target,
            authentication=authentication,
            authorization=authorization,
            description=description,
            ip_filtered=ip_filtered,
            protocol=protocol,
            readonly=readonly,
            usage=usage,
            vpn=vpn,
        )

        jsii.create(self.__class__, self, [title, props])

    @jsii.member(jsii_name="isEncrypted")
    def is_encrypted(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.invoke(self, "isEncrypted", []))

    @jsii.member(jsii_name="isProcessLocal")
    def is_process_local(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.invoke(self, "isProcessLocal", []))

    @jsii.member(jsii_name="receives")
    def receives(self, *assets: "DataAsset") -> None:
        '''
        :param assets: -
        '''
        return typing.cast(None, jsii.invoke(self, "receives", [*assets]))

    @jsii.member(jsii_name="sends")
    def sends(self, *assets: "DataAsset") -> None:
        '''
        :param assets: -
        '''
        return typing.cast(None, jsii.invoke(self, "sends", [*assets]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="authentication")
    def authentication(self) -> Authentication:
        return typing.cast(Authentication, jsii.get(self, "authentication"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="authorization")
    def authorization(self) -> Authorization:
        return typing.cast(Authorization, jsii.get(self, "authorization"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ipFiltered")
    def ip_filtered(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "ipFiltered"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="protocol")
    def protocol(self) -> "Protocol":
        return typing.cast("Protocol", jsii.get(self, "protocol"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="readonly")
    def readonly(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "readonly"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="source")
    def source(self) -> "TechnicalAsset":
        return typing.cast("TechnicalAsset", jsii.get(self, "source"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="target")
    def target(self) -> "TechnicalAsset":
        return typing.cast("TechnicalAsset", jsii.get(self, "target"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="title")
    def title(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "title"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="usage")
    def usage(self) -> "Usage":
        return typing.cast("Usage", jsii.get(self, "usage"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="vpn")
    def vpn(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "vpn"))


@jsii.data_type(
    jsii_type="cdktg.CommunicationOptions",
    jsii_struct_bases=[],
    name_mapping={
        "authentication": "authentication",
        "authorization": "authorization",
        "description": "description",
        "ip_filtered": "ipFiltered",
        "protocol": "protocol",
        "readonly": "readonly",
        "usage": "usage",
        "vpn": "vpn",
    },
)
class CommunicationOptions:
    def __init__(
        self,
        *,
        authentication: Authentication,
        authorization: Authorization,
        description: builtins.str,
        ip_filtered: builtins.bool,
        protocol: "Protocol",
        readonly: builtins.bool,
        usage: "Usage",
        vpn: builtins.bool,
    ) -> None:
        '''
        :param authentication: 
        :param authorization: 
        :param description: 
        :param ip_filtered: 
        :param protocol: 
        :param readonly: 
        :param usage: 
        :param vpn: 
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "authentication": authentication,
            "authorization": authorization,
            "description": description,
            "ip_filtered": ip_filtered,
            "protocol": protocol,
            "readonly": readonly,
            "usage": usage,
            "vpn": vpn,
        }

    @builtins.property
    def authentication(self) -> Authentication:
        result = self._values.get("authentication")
        assert result is not None, "Required property 'authentication' is missing"
        return typing.cast(Authentication, result)

    @builtins.property
    def authorization(self) -> Authorization:
        result = self._values.get("authorization")
        assert result is not None, "Required property 'authorization' is missing"
        return typing.cast(Authorization, result)

    @builtins.property
    def description(self) -> builtins.str:
        result = self._values.get("description")
        assert result is not None, "Required property 'description' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def ip_filtered(self) -> builtins.bool:
        result = self._values.get("ip_filtered")
        assert result is not None, "Required property 'ip_filtered' is missing"
        return typing.cast(builtins.bool, result)

    @builtins.property
    def protocol(self) -> "Protocol":
        result = self._values.get("protocol")
        assert result is not None, "Required property 'protocol' is missing"
        return typing.cast("Protocol", result)

    @builtins.property
    def readonly(self) -> builtins.bool:
        result = self._values.get("readonly")
        assert result is not None, "Required property 'readonly' is missing"
        return typing.cast(builtins.bool, result)

    @builtins.property
    def usage(self) -> "Usage":
        result = self._values.get("usage")
        assert result is not None, "Required property 'usage' is missing"
        return typing.cast("Usage", result)

    @builtins.property
    def vpn(self) -> builtins.bool:
        result = self._values.get("vpn")
        assert result is not None, "Required property 'vpn' is missing"
        return typing.cast(builtins.bool, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CommunicationOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdktg.CommunicationProps",
    jsii_struct_bases=[CommunicationOptions],
    name_mapping={
        "authentication": "authentication",
        "authorization": "authorization",
        "description": "description",
        "ip_filtered": "ipFiltered",
        "protocol": "protocol",
        "readonly": "readonly",
        "usage": "usage",
        "vpn": "vpn",
        "source": "source",
        "target": "target",
    },
)
class CommunicationProps(CommunicationOptions):
    def __init__(
        self,
        *,
        authentication: Authentication,
        authorization: Authorization,
        description: builtins.str,
        ip_filtered: builtins.bool,
        protocol: "Protocol",
        readonly: builtins.bool,
        usage: "Usage",
        vpn: builtins.bool,
        source: "TechnicalAsset",
        target: "TechnicalAsset",
    ) -> None:
        '''
        :param authentication: 
        :param authorization: 
        :param description: 
        :param ip_filtered: 
        :param protocol: 
        :param readonly: 
        :param usage: 
        :param vpn: 
        :param source: 
        :param target: 
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "authentication": authentication,
            "authorization": authorization,
            "description": description,
            "ip_filtered": ip_filtered,
            "protocol": protocol,
            "readonly": readonly,
            "usage": usage,
            "vpn": vpn,
            "source": source,
            "target": target,
        }

    @builtins.property
    def authentication(self) -> Authentication:
        result = self._values.get("authentication")
        assert result is not None, "Required property 'authentication' is missing"
        return typing.cast(Authentication, result)

    @builtins.property
    def authorization(self) -> Authorization:
        result = self._values.get("authorization")
        assert result is not None, "Required property 'authorization' is missing"
        return typing.cast(Authorization, result)

    @builtins.property
    def description(self) -> builtins.str:
        result = self._values.get("description")
        assert result is not None, "Required property 'description' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def ip_filtered(self) -> builtins.bool:
        result = self._values.get("ip_filtered")
        assert result is not None, "Required property 'ip_filtered' is missing"
        return typing.cast(builtins.bool, result)

    @builtins.property
    def protocol(self) -> "Protocol":
        result = self._values.get("protocol")
        assert result is not None, "Required property 'protocol' is missing"
        return typing.cast("Protocol", result)

    @builtins.property
    def readonly(self) -> builtins.bool:
        result = self._values.get("readonly")
        assert result is not None, "Required property 'readonly' is missing"
        return typing.cast(builtins.bool, result)

    @builtins.property
    def usage(self) -> "Usage":
        result = self._values.get("usage")
        assert result is not None, "Required property 'usage' is missing"
        return typing.cast("Usage", result)

    @builtins.property
    def vpn(self) -> builtins.bool:
        result = self._values.get("vpn")
        assert result is not None, "Required property 'vpn' is missing"
        return typing.cast(builtins.bool, result)

    @builtins.property
    def source(self) -> "TechnicalAsset":
        result = self._values.get("source")
        assert result is not None, "Required property 'source' is missing"
        return typing.cast("TechnicalAsset", result)

    @builtins.property
    def target(self) -> "TechnicalAsset":
        result = self._values.get("target")
        assert result is not None, "Required property 'target' is missing"
        return typing.cast("TechnicalAsset", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CommunicationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="cdktg.Confidentiality")
class Confidentiality(enum.Enum):
    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"
    RESTRICTED = "RESTRICTED"
    CONFIDENTIAL = "CONFIDENTIAL"
    STRICTLY_CONFIDENTIAL = "STRICTLY_CONFIDENTIAL"


@jsii.enum(jsii_type="cdktg.DataBreachProbability")
class DataBreachProbability(enum.Enum):
    IMPROBABLE = "IMPROBABLE"
    POSSIBLE = "POSSIBLE"
    PROBABLE = "PROBABLE"


@jsii.enum(jsii_type="cdktg.DataFormat")
class DataFormat(enum.Enum):
    JSON = "JSON"
    XML = "XML"
    SERIALIZATION = "SERIALIZATION"
    FILE = "FILE"
    CSV = "CSV"


@jsii.enum(jsii_type="cdktg.Encryption")
class Encryption(enum.Enum):
    NONE = "NONE"
    TRANSPARENT = "TRANSPARENT"
    SYMMETRIC_SHARED_KEY = "SYMMETRIC_SHARED_KEY"
    ASYMMETRIC_SHARED_KEY = "ASYMMETRIC_SHARED_KEY"
    ENDUSER_INDIVIDUAL_KEY = "ENDUSER_INDIVIDUAL_KEY"


@jsii.enum(jsii_type="cdktg.ExploitationImpact")
class ExploitationImpact(enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"


@jsii.enum(jsii_type="cdktg.ExploitationLikelihood")
class ExploitationLikelihood(enum.Enum):
    UNLIKELY = "UNLIKELY"
    LIKELY = "LIKELY"
    VERY_LIKELY = "VERY_LIKELY"
    FREQUENT = "FREQUENT"


@jsii.interface(jsii_type="cdktg.IAspect")
class IAspect(typing_extensions.Protocol):
    '''Represents an Aspect.'''

    @jsii.member(jsii_name="visit")
    def visit(self, node: constructs.IConstruct) -> None:
        '''All aspects can visit an IConstruct.

        :param node: -
        '''
        ...


class _IAspectProxy:
    '''Represents an Aspect.'''

    __jsii_type__: typing.ClassVar[str] = "cdktg.IAspect"

    @jsii.member(jsii_name="visit")
    def visit(self, node: constructs.IConstruct) -> None:
        '''All aspects can visit an IConstruct.

        :param node: -
        '''
        return typing.cast(None, jsii.invoke(self, "visit", [node]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IAspect).__jsii_proxy_class__ = lambda : _IAspectProxy


@jsii.interface(jsii_type="cdktg.ICustomSynthesis")
class ICustomSynthesis(typing_extensions.Protocol):
    '''Interface for constructs that want to do something custom during synthesis.

    This feature is intended for use by cdktg only; 3rd party
    library authors and CDK users should not use this function.
    '''

    @jsii.member(jsii_name="onSynthesize")
    def on_synthesize(self, session: "ISynthesisSession") -> None:
        '''Called when the construct is synthesized.

        :param session: -
        '''
        ...


class _ICustomSynthesisProxy:
    '''Interface for constructs that want to do something custom during synthesis.

    This feature is intended for use by cdktg only; 3rd party
    library authors and CDK users should not use this function.
    '''

    __jsii_type__: typing.ClassVar[str] = "cdktg.ICustomSynthesis"

    @jsii.member(jsii_name="onSynthesize")
    def on_synthesize(self, session: "ISynthesisSession") -> None:
        '''Called when the construct is synthesized.

        :param session: -
        '''
        return typing.cast(None, jsii.invoke(self, "onSynthesize", [session]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, ICustomSynthesis).__jsii_proxy_class__ = lambda : _ICustomSynthesisProxy


@jsii.interface(jsii_type="cdktg.IManifest")
class IManifest(typing_extensions.Protocol):
    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="models")
    def models(self) -> typing.Mapping[builtins.str, "ModelManifest"]:
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        ...


class _IManifestProxy:
    __jsii_type__: typing.ClassVar[str] = "cdktg.IManifest"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="models")
    def models(self) -> typing.Mapping[builtins.str, "ModelManifest"]:
        return typing.cast(typing.Mapping[builtins.str, "ModelManifest"], jsii.get(self, "models"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "version"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IManifest).__jsii_proxy_class__ = lambda : _IManifestProxy


@jsii.interface(jsii_type="cdktg.IModelSynthesizer")
class IModelSynthesizer(typing_extensions.Protocol):
    @jsii.member(jsii_name="addFileAsset")
    def add_file_asset(self, file_path: builtins.str) -> None:
        '''
        :param file_path: -
        '''
        ...

    @jsii.member(jsii_name="synthesize")
    def synthesize(self, session: "ISynthesisSession") -> None:
        '''Synthesize the associated model to the session.

        :param session: -
        '''
        ...


class _IModelSynthesizerProxy:
    __jsii_type__: typing.ClassVar[str] = "cdktg.IModelSynthesizer"

    @jsii.member(jsii_name="addFileAsset")
    def add_file_asset(self, file_path: builtins.str) -> None:
        '''
        :param file_path: -
        '''
        return typing.cast(None, jsii.invoke(self, "addFileAsset", [file_path]))

    @jsii.member(jsii_name="synthesize")
    def synthesize(self, session: "ISynthesisSession") -> None:
        '''Synthesize the associated model to the session.

        :param session: -
        '''
        return typing.cast(None, jsii.invoke(self, "synthesize", [session]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, IModelSynthesizer).__jsii_proxy_class__ = lambda : _IModelSynthesizerProxy


@jsii.interface(jsii_type="cdktg.ISynthesisSession")
class ISynthesisSession(typing_extensions.Protocol):
    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="manifest")
    def manifest(self) -> "Manifest":
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="outdir")
    def outdir(self) -> builtins.str:
        '''The output directory for this synthesis session.'''
        ...

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="skipValidation")
    def skip_validation(self) -> typing.Optional[builtins.bool]:
        ...


class _ISynthesisSessionProxy:
    __jsii_type__: typing.ClassVar[str] = "cdktg.ISynthesisSession"

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="manifest")
    def manifest(self) -> "Manifest":
        return typing.cast("Manifest", jsii.get(self, "manifest"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="outdir")
    def outdir(self) -> builtins.str:
        '''The output directory for this synthesis session.'''
        return typing.cast(builtins.str, jsii.get(self, "outdir"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="skipValidation")
    def skip_validation(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "skipValidation"))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, ISynthesisSession).__jsii_proxy_class__ = lambda : _ISynthesisSessionProxy


class Image(metaclass=jsii.JSIIMeta, jsii_type="cdktg.Image"):
    def __init__(self, file_path: builtins.str, title: builtins.str) -> None:
        '''
        :param file_path: -
        :param title: -
        '''
        jsii.create(self.__class__, self, [file_path, title])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="filePath")
    def file_path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "filePath"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="title")
    def title(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "title"))


@jsii.enum(jsii_type="cdktg.Integrity")
class Integrity(enum.Enum):
    ARCHIVE = "ARCHIVE"
    OPERATIONAL = "OPERATIONAL"
    IMPORTANT = "IMPORTANT"
    CRITICAL = "CRITICAL"
    MISSION_CRITICAL = "MISSION_CRITICAL"


@jsii.enum(jsii_type="cdktg.Machine")
class Machine(enum.Enum):
    PHYSICAL = "PHYSICAL"
    VIRTUAL = "VIRTUAL"
    CONTAINER = "CONTAINER"
    SERVERLESS = "SERVERLESS"


@jsii.implements(IManifest)
class Manifest(metaclass=jsii.JSIIMeta, jsii_type="cdktg.Manifest"):
    def __init__(self, version: builtins.str, outdir: builtins.str) -> None:
        '''
        :param version: -
        :param outdir: -
        '''
        jsii.create(self.__class__, self, [version, outdir])

    @jsii.member(jsii_name="fromPath") # type: ignore[misc]
    @builtins.classmethod
    def from_path(cls, dir: builtins.str) -> "Manifest":
        '''
        :param dir: -
        '''
        return typing.cast("Manifest", jsii.sinvoke(cls, "fromPath", [dir]))

    @jsii.member(jsii_name="buildManifest")
    def build_manifest(self) -> IManifest:
        return typing.cast(IManifest, jsii.invoke(self, "buildManifest", []))

    @jsii.member(jsii_name="forModel")
    def for_model(self, model: "Model") -> "ModelManifest":
        '''
        :param model: -
        '''
        return typing.cast("ModelManifest", jsii.invoke(self, "forModel", [model]))

    @jsii.member(jsii_name="writeToFile")
    def write_to_file(self) -> None:
        return typing.cast(None, jsii.invoke(self, "writeToFile", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="fileName")
    def FILE_NAME(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "fileName"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="modelsFolder")
    def MODELS_FOLDER(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "modelsFolder"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="models")
    def models(self) -> typing.Mapping[builtins.str, "ModelManifest"]:
        return typing.cast(typing.Mapping[builtins.str, "ModelManifest"], jsii.get(self, "models"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="outdir")
    def outdir(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "outdir"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "version"))


class Model(constructs.Construct, metaclass=jsii.JSIIMeta, jsii_type="cdktg.Model"):
    def __init__(
        self,
        project: constructs.Construct,
        id: builtins.str,
        *,
        author: Author,
        business_criticality: BusinessCriticality,
        version: builtins.str,
        abuse_cases: typing.Optional[typing.Sequence[AbuseCase]] = None,
        business_overview: typing.Optional["Overview"] = None,
        date: typing.Optional[builtins.str] = None,
        management_summary: typing.Optional[builtins.str] = None,
        questions: typing.Optional[typing.Sequence["Question"]] = None,
        security_requirements: typing.Optional[typing.Sequence["SecurityRequirement"]] = None,
        technical_overview: typing.Optional["Overview"] = None,
        title: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param project: -
        :param id: -
        :param author: Author of the model.
        :param business_criticality: Business criticality of the target.
        :param version: Version of the Threagile toolkit.
        :param abuse_cases: Custom abuse cases for the report.
        :param business_overview: Individual business overview for the report.
        :param date: Date of the model.
        :param management_summary: Individual management summary for the report.
        :param questions: Custom questions for the report.
        :param security_requirements: Custom security requirements for the report.
        :param technical_overview: Individual technical overview for the report.
        :param title: Title of the model.
        '''
        props = ModelProps(
            author=author,
            business_criticality=business_criticality,
            version=version,
            abuse_cases=abuse_cases,
            business_overview=business_overview,
            date=date,
            management_summary=management_summary,
            questions=questions,
            security_requirements=security_requirements,
            technical_overview=technical_overview,
            title=title,
        )

        jsii.create(self.__class__, self, [project, id, props])

    @jsii.member(jsii_name="isModel") # type: ignore[misc]
    @builtins.classmethod
    def is_model(cls, x: typing.Any) -> builtins.bool:
        '''
        :param x: -
        '''
        return typing.cast(builtins.bool, jsii.sinvoke(cls, "isModel", [x]))

    @jsii.member(jsii_name="of") # type: ignore[misc]
    @builtins.classmethod
    def of(cls, construct: constructs.IConstruct) -> "Model":
        '''
        :param construct: -
        '''
        return typing.cast("Model", jsii.sinvoke(cls, "of", [construct]))

    @jsii.member(jsii_name="addAbuseCases")
    def add_abuse_cases(self, *cases: AbuseCase) -> None:
        '''
        :param cases: -
        '''
        return typing.cast(None, jsii.invoke(self, "addAbuseCases", [*cases]))

    @jsii.member(jsii_name="addOverride")
    def add_override(self, path: builtins.str, value: typing.Any) -> None:
        '''
        :param path: -
        :param value: -
        '''
        return typing.cast(None, jsii.invoke(self, "addOverride", [path, value]))

    @jsii.member(jsii_name="addQuestion")
    def add_question(
        self,
        text: builtins.str,
        answer: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param text: -
        :param answer: -
        '''
        return typing.cast(None, jsii.invoke(self, "addQuestion", [text, answer]))

    @jsii.member(jsii_name="addSecurityRequirements")
    def add_security_requirements(self, *requirements: "SecurityRequirement") -> None:
        '''
        :param requirements: -
        '''
        return typing.cast(None, jsii.invoke(self, "addSecurityRequirements", [*requirements]))

    @jsii.member(jsii_name="addTag")
    def add_tag(self, tag: builtins.str) -> None:
        '''
        :param tag: -
        '''
        return typing.cast(None, jsii.invoke(self, "addTag", [tag]))

    @jsii.member(jsii_name="addTags")
    def add_tags(self, *tags: builtins.str) -> None:
        '''
        :param tags: -
        '''
        return typing.cast(None, jsii.invoke(self, "addTags", [*tags]))

    @jsii.member(jsii_name="trackRisk")
    def track_risk(
        self,
        id: builtins.str,
        *,
        checked_by: typing.Optional[builtins.str] = None,
        date: typing.Optional[builtins.str] = None,
        justification: typing.Optional[builtins.str] = None,
        status: typing.Optional["RiskTrackingStatus"] = None,
        ticket: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param id: -
        :param checked_by: 
        :param date: 
        :param justification: 
        :param status: 
        :param ticket: 
        '''
        options = RiskTrackingProps(
            checked_by=checked_by,
            date=date,
            justification=justification,
            status=status,
            ticket=ticket,
        )

        return typing.cast(None, jsii.invoke(self, "trackRisk", [id, options]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="author")
    def author(self) -> Author:
        return typing.cast(Author, jsii.get(self, "author"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="businessCriticality")
    def business_criticality(self) -> BusinessCriticality:
        return typing.cast(BusinessCriticality, jsii.get(self, "businessCriticality"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="title")
    def title(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "title"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "version"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="businessOverview")
    def business_overview(self) -> typing.Optional["Overview"]:
        return typing.cast(typing.Optional["Overview"], jsii.get(self, "businessOverview"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="date")
    def date(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "date"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="managementSummary")
    def management_summary(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "managementSummary"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="technicalOverview")
    def technical_overview(self) -> typing.Optional["Overview"]:
        return typing.cast(typing.Optional["Overview"], jsii.get(self, "technicalOverview"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="synthesizer")
    def synthesizer(self) -> IModelSynthesizer:
        return typing.cast(IModelSynthesizer, jsii.get(self, "synthesizer"))

    @synthesizer.setter
    def synthesizer(self, value: IModelSynthesizer) -> None:
        jsii.set(self, "synthesizer", value)


@jsii.data_type(
    jsii_type="cdktg.ModelAnnotation",
    jsii_struct_bases=[],
    name_mapping={
        "construct_path": "constructPath",
        "level": "level",
        "message": "message",
        "stacktrace": "stacktrace",
    },
)
class ModelAnnotation:
    def __init__(
        self,
        *,
        construct_path: builtins.str,
        level: AnnotationMetadataEntryType,
        message: builtins.str,
        stacktrace: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param construct_path: 
        :param level: 
        :param message: 
        :param stacktrace: 
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "construct_path": construct_path,
            "level": level,
            "message": message,
        }
        if stacktrace is not None:
            self._values["stacktrace"] = stacktrace

    @builtins.property
    def construct_path(self) -> builtins.str:
        result = self._values.get("construct_path")
        assert result is not None, "Required property 'construct_path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def level(self) -> AnnotationMetadataEntryType:
        result = self._values.get("level")
        assert result is not None, "Required property 'level' is missing"
        return typing.cast(AnnotationMetadataEntryType, result)

    @builtins.property
    def message(self) -> builtins.str:
        result = self._values.get("message")
        assert result is not None, "Required property 'message' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def stacktrace(self) -> typing.Optional[typing.List[builtins.str]]:
        result = self._values.get("stacktrace")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ModelAnnotation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdktg.ModelManifest",
    jsii_struct_bases=[],
    name_mapping={
        "annotations": "annotations",
        "construct_path": "constructPath",
        "name": "name",
        "sanitized_name": "sanitizedName",
        "synthesized_model_path": "synthesizedModelPath",
        "working_directory": "workingDirectory",
    },
)
class ModelManifest:
    def __init__(
        self,
        *,
        annotations: typing.Sequence[ModelAnnotation],
        construct_path: builtins.str,
        name: builtins.str,
        sanitized_name: builtins.str,
        synthesized_model_path: builtins.str,
        working_directory: builtins.str,
    ) -> None:
        '''
        :param annotations: 
        :param construct_path: 
        :param name: 
        :param sanitized_name: 
        :param synthesized_model_path: 
        :param working_directory: 
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "annotations": annotations,
            "construct_path": construct_path,
            "name": name,
            "sanitized_name": sanitized_name,
            "synthesized_model_path": synthesized_model_path,
            "working_directory": working_directory,
        }

    @builtins.property
    def annotations(self) -> typing.List[ModelAnnotation]:
        result = self._values.get("annotations")
        assert result is not None, "Required property 'annotations' is missing"
        return typing.cast(typing.List[ModelAnnotation], result)

    @builtins.property
    def construct_path(self) -> builtins.str:
        result = self._values.get("construct_path")
        assert result is not None, "Required property 'construct_path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def sanitized_name(self) -> builtins.str:
        result = self._values.get("sanitized_name")
        assert result is not None, "Required property 'sanitized_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def synthesized_model_path(self) -> builtins.str:
        result = self._values.get("synthesized_model_path")
        assert result is not None, "Required property 'synthesized_model_path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def working_directory(self) -> builtins.str:
        result = self._values.get("working_directory")
        assert result is not None, "Required property 'working_directory' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ModelManifest(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdktg.ModelProps",
    jsii_struct_bases=[],
    name_mapping={
        "author": "author",
        "business_criticality": "businessCriticality",
        "version": "version",
        "abuse_cases": "abuseCases",
        "business_overview": "businessOverview",
        "date": "date",
        "management_summary": "managementSummary",
        "questions": "questions",
        "security_requirements": "securityRequirements",
        "technical_overview": "technicalOverview",
        "title": "title",
    },
)
class ModelProps:
    def __init__(
        self,
        *,
        author: Author,
        business_criticality: BusinessCriticality,
        version: builtins.str,
        abuse_cases: typing.Optional[typing.Sequence[AbuseCase]] = None,
        business_overview: typing.Optional["Overview"] = None,
        date: typing.Optional[builtins.str] = None,
        management_summary: typing.Optional[builtins.str] = None,
        questions: typing.Optional[typing.Sequence["Question"]] = None,
        security_requirements: typing.Optional[typing.Sequence["SecurityRequirement"]] = None,
        technical_overview: typing.Optional["Overview"] = None,
        title: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param author: Author of the model.
        :param business_criticality: Business criticality of the target.
        :param version: Version of the Threagile toolkit.
        :param abuse_cases: Custom abuse cases for the report.
        :param business_overview: Individual business overview for the report.
        :param date: Date of the model.
        :param management_summary: Individual management summary for the report.
        :param questions: Custom questions for the report.
        :param security_requirements: Custom security requirements for the report.
        :param technical_overview: Individual technical overview for the report.
        :param title: Title of the model.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "author": author,
            "business_criticality": business_criticality,
            "version": version,
        }
        if abuse_cases is not None:
            self._values["abuse_cases"] = abuse_cases
        if business_overview is not None:
            self._values["business_overview"] = business_overview
        if date is not None:
            self._values["date"] = date
        if management_summary is not None:
            self._values["management_summary"] = management_summary
        if questions is not None:
            self._values["questions"] = questions
        if security_requirements is not None:
            self._values["security_requirements"] = security_requirements
        if technical_overview is not None:
            self._values["technical_overview"] = technical_overview
        if title is not None:
            self._values["title"] = title

    @builtins.property
    def author(self) -> Author:
        '''Author of the model.'''
        result = self._values.get("author")
        assert result is not None, "Required property 'author' is missing"
        return typing.cast(Author, result)

    @builtins.property
    def business_criticality(self) -> BusinessCriticality:
        '''Business criticality of the target.'''
        result = self._values.get("business_criticality")
        assert result is not None, "Required property 'business_criticality' is missing"
        return typing.cast(BusinessCriticality, result)

    @builtins.property
    def version(self) -> builtins.str:
        '''Version of the Threagile toolkit.'''
        result = self._values.get("version")
        assert result is not None, "Required property 'version' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def abuse_cases(self) -> typing.Optional[typing.List[AbuseCase]]:
        '''Custom abuse cases for the report.'''
        result = self._values.get("abuse_cases")
        return typing.cast(typing.Optional[typing.List[AbuseCase]], result)

    @builtins.property
    def business_overview(self) -> typing.Optional["Overview"]:
        '''Individual business overview for the report.'''
        result = self._values.get("business_overview")
        return typing.cast(typing.Optional["Overview"], result)

    @builtins.property
    def date(self) -> typing.Optional[builtins.str]:
        '''Date of the model.'''
        result = self._values.get("date")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def management_summary(self) -> typing.Optional[builtins.str]:
        '''Individual management summary for the report.'''
        result = self._values.get("management_summary")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def questions(self) -> typing.Optional[typing.List["Question"]]:
        '''Custom questions for the report.'''
        result = self._values.get("questions")
        return typing.cast(typing.Optional[typing.List["Question"]], result)

    @builtins.property
    def security_requirements(
        self,
    ) -> typing.Optional[typing.List["SecurityRequirement"]]:
        '''Custom security requirements for the report.'''
        result = self._values.get("security_requirements")
        return typing.cast(typing.Optional[typing.List["SecurityRequirement"]], result)

    @builtins.property
    def technical_overview(self) -> typing.Optional["Overview"]:
        '''Individual technical overview for the report.'''
        result = self._values.get("technical_overview")
        return typing.cast(typing.Optional["Overview"], result)

    @builtins.property
    def title(self) -> typing.Optional[builtins.str]:
        '''Title of the model.'''
        result = self._values.get("title")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ModelProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IModelSynthesizer)
class ModelSynthesizer(metaclass=jsii.JSIIMeta, jsii_type="cdktg.ModelSynthesizer"):
    def __init__(
        self,
        model: Model,
        continue_on_error_annotations: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param model: -
        :param continue_on_error_annotations: -
        '''
        jsii.create(self.__class__, self, [model, continue_on_error_annotations])

    @jsii.member(jsii_name="addFileAsset")
    def add_file_asset(self, file_path: builtins.str) -> None:
        '''
        :param file_path: -
        '''
        return typing.cast(None, jsii.invoke(self, "addFileAsset", [file_path]))

    @jsii.member(jsii_name="synthesize")
    def synthesize(self, session: ISynthesisSession) -> None:
        '''Synthesize the associated model to the session.

        :param session: -
        '''
        return typing.cast(None, jsii.invoke(self, "synthesize", [session]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="model")
    def _model(self) -> Model:
        return typing.cast(Model, jsii.get(self, "model"))

    @_model.setter
    def _model(self, value: Model) -> None:
        jsii.set(self, "model", value)


@jsii.data_type(
    jsii_type="cdktg.OutOfScopeProps",
    jsii_struct_bases=[],
    name_mapping={"out_of_scope": "outOfScope", "justification": "justification"},
)
class OutOfScopeProps:
    def __init__(
        self,
        *,
        out_of_scope: builtins.bool,
        justification: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param out_of_scope: 
        :param justification: 
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "out_of_scope": out_of_scope,
        }
        if justification is not None:
            self._values["justification"] = justification

    @builtins.property
    def out_of_scope(self) -> builtins.bool:
        result = self._values.get("out_of_scope")
        assert result is not None, "Required property 'out_of_scope' is missing"
        return typing.cast(builtins.bool, result)

    @builtins.property
    def justification(self) -> typing.Optional[builtins.str]:
        result = self._values.get("justification")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OutOfScopeProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Overview(metaclass=jsii.JSIIMeta, jsii_type="cdktg.Overview"):
    def __init__(
        self,
        *,
        description: builtins.str,
        images: typing.Optional[typing.Sequence[Image]] = None,
    ) -> None:
        '''
        :param description: 
        :param images: 
        '''
        props = OverviewProps(description=description, images=images)

        jsii.create(self.__class__, self, [props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="images")
    def images(self) -> typing.Optional[typing.List[Image]]:
        return typing.cast(typing.Optional[typing.List[Image]], jsii.get(self, "images"))


@jsii.data_type(
    jsii_type="cdktg.OverviewProps",
    jsii_struct_bases=[],
    name_mapping={"description": "description", "images": "images"},
)
class OverviewProps:
    def __init__(
        self,
        *,
        description: builtins.str,
        images: typing.Optional[typing.Sequence[Image]] = None,
    ) -> None:
        '''
        :param description: 
        :param images: 
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "description": description,
        }
        if images is not None:
            self._values["images"] = images

    @builtins.property
    def description(self) -> builtins.str:
        result = self._values.get("description")
        assert result is not None, "Required property 'description' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def images(self) -> typing.Optional[typing.List[Image]]:
        result = self._values.get("images")
        return typing.cast(typing.Optional[typing.List[Image]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OverviewProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Project(constructs.Construct, metaclass=jsii.JSIIMeta, jsii_type="cdktg.Project"):
    def __init__(
        self,
        *,
        outdir: typing.Optional[builtins.str] = None,
        skip_validation: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param outdir: The directory to output the threadgile model. Default: - .
        :param skip_validation: Whether to skip the validation during synthesis of the project. Default: - false
        '''
        props = ProjectProps(outdir=outdir, skip_validation=skip_validation)

        jsii.create(self.__class__, self, [props])

    @jsii.member(jsii_name="synth")
    def synth(self) -> None:
        '''Synthesizes the model to the output directory.'''
        return typing.cast(None, jsii.invoke(self, "synth", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="manifest")
    def manifest(self) -> Manifest:
        return typing.cast(Manifest, jsii.get(self, "manifest"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="outdir")
    def outdir(self) -> builtins.str:
        '''The output directory into which models will be synthesized.'''
        return typing.cast(builtins.str, jsii.get(self, "outdir"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="skipValidation")
    def skip_validation(self) -> typing.Optional[builtins.bool]:
        '''Whether to skip the validation during synthesis of the app.'''
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "skipValidation"))


@jsii.data_type(
    jsii_type="cdktg.ProjectProps",
    jsii_struct_bases=[],
    name_mapping={"outdir": "outdir", "skip_validation": "skipValidation"},
)
class ProjectProps:
    def __init__(
        self,
        *,
        outdir: typing.Optional[builtins.str] = None,
        skip_validation: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param outdir: The directory to output the threadgile model. Default: - .
        :param skip_validation: Whether to skip the validation during synthesis of the project. Default: - false
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if outdir is not None:
            self._values["outdir"] = outdir
        if skip_validation is not None:
            self._values["skip_validation"] = skip_validation

    @builtins.property
    def outdir(self) -> typing.Optional[builtins.str]:
        '''The directory to output the threadgile model.

        :default: - .
        '''
        result = self._values.get("outdir")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def skip_validation(self) -> typing.Optional[builtins.bool]:
        '''Whether to skip the validation during synthesis of the project.

        :default: - false
        '''
        result = self._values.get("skip_validation")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ProjectProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="cdktg.Protocol")
class Protocol(enum.Enum):
    UNKNOEN = "UNKNOEN"
    HTTP = "HTTP"
    HTTPS = "HTTPS"
    WS = "WS"
    WSS = "WSS"
    REVERSE_PROXY_WEB_PROTOCOL = "REVERSE_PROXY_WEB_PROTOCOL"
    REVERSE_PROXY_WEB_PROTOCOL_ENCRYPTED = "REVERSE_PROXY_WEB_PROTOCOL_ENCRYPTED"
    MQTT = "MQTT"
    JDBC = "JDBC"
    JDBC_ENCRYPTED = "JDBC_ENCRYPTED"
    ODBC = "ODBC"
    ODBC_ENCRYPTED = "ODBC_ENCRYPTED"
    SQL_ACCESS_PROTOCOL = "SQL_ACCESS_PROTOCOL"
    SQL_ACCESS_PROTOCOL_ENCRYPTED = "SQL_ACCESS_PROTOCOL_ENCRYPTED"
    NOSQL_ACCESS_PROTOCOL = "NOSQL_ACCESS_PROTOCOL"
    NOSQL_ACCESS_PROTOCOL_ENCRYPTED = "NOSQL_ACCESS_PROTOCOL_ENCRYPTED"
    BINARY = "BINARY"
    BINARY_ENCRYPTED = "BINARY_ENCRYPTED"
    TEXT = "TEXT"
    TEXT_ENCRYPTED = "TEXT_ENCRYPTED"
    SSH = "SSH"
    SSH_TUNNEL = "SSH_TUNNEL"
    SMTP = "SMTP"
    SMTP_ENCRYPTED = "SMTP_ENCRYPTED"
    POP3 = "POP3"
    POP3_ENCRYPTED = "POP3_ENCRYPTED"
    IMAP = "IMAP"
    IMAP_ENCRYPTED = "IMAP_ENCRYPTED"
    FTP = "FTP"
    FTPS = "FTPS"
    SFTP = "SFTP"
    SCP = "SCP"
    LDAP = "LDAP"
    LDAPS = "LDAPS"
    JMS = "JMS"
    NFS = "NFS"
    SMB = "SMB"
    SMB_ENCRYPTED = "SMB_ENCRYPTED"
    LOCAL_FILE_ACCESS = "LOCAL_FILE_ACCESS"
    NRPE = "NRPE"
    XMPP = "XMPP"
    IIOP = "IIOP"
    IIOP_ENCRYPTED = "IIOP_ENCRYPTED"
    JRMP = "JRMP"
    JRMP_ENCRYPTED = "JRMP_ENCRYPTED"
    IN_PROCESS_LIBRARY_CALL = "IN_PROCESS_LIBRARY_CALL"
    CONTAINER_SPAWNING = "CONTAINER_SPAWNING"


@jsii.enum(jsii_type="cdktg.Quantity")
class Quantity(enum.Enum):
    VERY_FEW = "VERY_FEW"
    FEW = "FEW"
    MANY = "MANY"
    VERY_MANY = "VERY_MANY"


@jsii.data_type(
    jsii_type="cdktg.Question",
    jsii_struct_bases=[],
    name_mapping={"text": "text", "answer": "answer"},
)
class Question:
    def __init__(
        self,
        *,
        text: builtins.str,
        answer: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param text: 
        :param answer: 
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "text": text,
        }
        if answer is not None:
            self._values["answer"] = answer

    @builtins.property
    def text(self) -> builtins.str:
        result = self._values.get("text")
        assert result is not None, "Required property 'text' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def answer(self) -> typing.Optional[builtins.str]:
        result = self._values.get("answer")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Question(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Resource(
    constructs.Construct,
    metaclass=jsii.JSIIAbstractClass,
    jsii_type="cdktg.Resource",
):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param description: 
        '''
        props = ResourceProps(description=description)

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="title")
    def title(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "title"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "description"))


class _ResourceProxy(Resource):
    pass

# Adding a "__jsii_proxy_class__(): typing.Type" function to the abstract class
typing.cast(typing.Any, Resource).__jsii_proxy_class__ = lambda : _ResourceProxy


@jsii.data_type(
    jsii_type="cdktg.ResourceProps",
    jsii_struct_bases=[],
    name_mapping={"description": "description"},
)
class ResourceProps:
    def __init__(self, *, description: typing.Optional[builtins.str] = None) -> None:
        '''
        :param description: 
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if description is not None:
            self._values["description"] = description

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ResourceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Risk(metaclass=jsii.JSIIMeta, jsii_type="cdktg.Risk"):
    def __init__(
        self,
        id: builtins.str,
        *,
        most_relevant_communication_link: typing.Optional[Communication] = None,
        most_relevant_data_asset: typing.Optional["DataAsset"] = None,
        most_relevant_shared_runtime: typing.Optional["SharedRuntime"] = None,
        most_relevant_technical_asset: typing.Optional["TechnicalAsset"] = None,
        most_relevant_trust_boundary: typing.Optional["TrustBoundary"] = None,
        data_breach_probability: DataBreachProbability,
        data_breach_technical_assets: typing.Sequence["TechnicalAsset"],
        exploitation_impact: ExploitationImpact,
        exploitation_likelihood: ExploitationLikelihood,
        severity: "Severity",
    ) -> None:
        '''
        :param id: -
        :param most_relevant_communication_link: 
        :param most_relevant_data_asset: 
        :param most_relevant_shared_runtime: 
        :param most_relevant_technical_asset: 
        :param most_relevant_trust_boundary: 
        :param data_breach_probability: 
        :param data_breach_technical_assets: 
        :param exploitation_impact: 
        :param exploitation_likelihood: 
        :param severity: 
        '''
        props = RiskProps(
            most_relevant_communication_link=most_relevant_communication_link,
            most_relevant_data_asset=most_relevant_data_asset,
            most_relevant_shared_runtime=most_relevant_shared_runtime,
            most_relevant_technical_asset=most_relevant_technical_asset,
            most_relevant_trust_boundary=most_relevant_trust_boundary,
            data_breach_probability=data_breach_probability,
            data_breach_technical_assets=data_breach_technical_assets,
            exploitation_impact=exploitation_impact,
            exploitation_likelihood=exploitation_likelihood,
            severity=severity,
        )

        jsii.create(self.__class__, self, [id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dataBreachProbability")
    def data_breach_probability(self) -> DataBreachProbability:
        return typing.cast(DataBreachProbability, jsii.get(self, "dataBreachProbability"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dataBreachTechnicalAssets")
    def data_breach_technical_assets(self) -> typing.List["TechnicalAsset"]:
        return typing.cast(typing.List["TechnicalAsset"], jsii.get(self, "dataBreachTechnicalAssets"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="exploitationImpact")
    def exploitation_impact(self) -> ExploitationImpact:
        return typing.cast(ExploitationImpact, jsii.get(self, "exploitationImpact"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="exploitationLikelihood")
    def exploitation_likelihood(self) -> ExploitationLikelihood:
        return typing.cast(ExploitationLikelihood, jsii.get(self, "exploitationLikelihood"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="severity")
    def severity(self) -> "Severity":
        return typing.cast("Severity", jsii.get(self, "severity"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mostRelevantCommunicationLink")
    def most_relevant_communication_link(self) -> typing.Optional[Communication]:
        return typing.cast(typing.Optional[Communication], jsii.get(self, "mostRelevantCommunicationLink"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mostRelevantDataAsset")
    def most_relevant_data_asset(self) -> typing.Optional["DataAsset"]:
        return typing.cast(typing.Optional["DataAsset"], jsii.get(self, "mostRelevantDataAsset"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mostRelevantSharedRuntime")
    def most_relevant_shared_runtime(self) -> typing.Optional["SharedRuntime"]:
        return typing.cast(typing.Optional["SharedRuntime"], jsii.get(self, "mostRelevantSharedRuntime"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mostRelevantTechnicalAsset")
    def most_relevant_technical_asset(self) -> typing.Optional["TechnicalAsset"]:
        return typing.cast(typing.Optional["TechnicalAsset"], jsii.get(self, "mostRelevantTechnicalAsset"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mostRelevantTrustBoundary")
    def most_relevant_trust_boundary(self) -> typing.Optional["TrustBoundary"]:
        return typing.cast(typing.Optional["TrustBoundary"], jsii.get(self, "mostRelevantTrustBoundary"))


class RiskCategory(Resource, metaclass=jsii.JSIIMeta, jsii_type="cdktg.RiskCategory"):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        action: builtins.str,
        asvs: builtins.str,
        cheat_sheet: builtins.str,
        check: builtins.str,
        cwe: jsii.Number,
        detection_logic: builtins.str,
        false_positives: builtins.str,
        function: "RiskFunction",
        impact: builtins.str,
        mitigation: builtins.str,
        risk_assessment: builtins.str,
        stride: "Stride",
        model_failure_possible_reason: typing.Optional[builtins.bool] = None,
        description: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param action: 
        :param asvs: 
        :param cheat_sheet: 
        :param check: 
        :param cwe: 
        :param detection_logic: 
        :param false_positives: 
        :param function: 
        :param impact: 
        :param mitigation: 
        :param risk_assessment: 
        :param stride: 
        :param model_failure_possible_reason: 
        :param description: 
        '''
        props = RiskCategoryProps(
            action=action,
            asvs=asvs,
            cheat_sheet=cheat_sheet,
            check=check,
            cwe=cwe,
            detection_logic=detection_logic,
            false_positives=false_positives,
            function=function,
            impact=impact,
            mitigation=mitigation,
            risk_assessment=risk_assessment,
            stride=stride,
            model_failure_possible_reason=model_failure_possible_reason,
            description=description,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="addIdentifiedRisk")
    def add_identified_risk(self, risk: Risk) -> None:
        '''
        :param risk: -
        '''
        return typing.cast(None, jsii.invoke(self, "addIdentifiedRisk", [risk]))

    @jsii.member(jsii_name="identifiedAtDataAsset")
    def identified_at_data_asset(
        self,
        target: "DataAsset",
        *,
        data_breach_probability: DataBreachProbability,
        data_breach_technical_assets: typing.Sequence["TechnicalAsset"],
        exploitation_impact: ExploitationImpact,
        exploitation_likelihood: ExploitationLikelihood,
        severity: "Severity",
    ) -> None:
        '''
        :param target: -
        :param data_breach_probability: 
        :param data_breach_technical_assets: 
        :param exploitation_impact: 
        :param exploitation_likelihood: 
        :param severity: 
        '''
        options = RiskOptions(
            data_breach_probability=data_breach_probability,
            data_breach_technical_assets=data_breach_technical_assets,
            exploitation_impact=exploitation_impact,
            exploitation_likelihood=exploitation_likelihood,
            severity=severity,
        )

        return typing.cast(None, jsii.invoke(self, "identifiedAtDataAsset", [target, options]))

    @jsii.member(jsii_name="identifiedAtSharedRuntime")
    def identified_at_shared_runtime(
        self,
        target: "SharedRuntime",
        *,
        data_breach_probability: DataBreachProbability,
        data_breach_technical_assets: typing.Sequence["TechnicalAsset"],
        exploitation_impact: ExploitationImpact,
        exploitation_likelihood: ExploitationLikelihood,
        severity: "Severity",
    ) -> None:
        '''
        :param target: -
        :param data_breach_probability: 
        :param data_breach_technical_assets: 
        :param exploitation_impact: 
        :param exploitation_likelihood: 
        :param severity: 
        '''
        options = RiskOptions(
            data_breach_probability=data_breach_probability,
            data_breach_technical_assets=data_breach_technical_assets,
            exploitation_impact=exploitation_impact,
            exploitation_likelihood=exploitation_likelihood,
            severity=severity,
        )

        return typing.cast(None, jsii.invoke(self, "identifiedAtSharedRuntime", [target, options]))

    @jsii.member(jsii_name="identifiedAtTechnicalAsset")
    def identified_at_technical_asset(
        self,
        target: "TechnicalAsset",
        *,
        data_breach_probability: DataBreachProbability,
        data_breach_technical_assets: typing.Sequence["TechnicalAsset"],
        exploitation_impact: ExploitationImpact,
        exploitation_likelihood: ExploitationLikelihood,
        severity: "Severity",
    ) -> None:
        '''
        :param target: -
        :param data_breach_probability: 
        :param data_breach_technical_assets: 
        :param exploitation_impact: 
        :param exploitation_likelihood: 
        :param severity: 
        '''
        options = RiskOptions(
            data_breach_probability=data_breach_probability,
            data_breach_technical_assets=data_breach_technical_assets,
            exploitation_impact=exploitation_impact,
            exploitation_likelihood=exploitation_likelihood,
            severity=severity,
        )

        return typing.cast(None, jsii.invoke(self, "identifiedAtTechnicalAsset", [target, options]))

    @jsii.member(jsii_name="identifiedAtTrustBoundary")
    def identified_at_trust_boundary(
        self,
        target: "SharedRuntime",
        *,
        data_breach_probability: DataBreachProbability,
        data_breach_technical_assets: typing.Sequence["TechnicalAsset"],
        exploitation_impact: ExploitationImpact,
        exploitation_likelihood: ExploitationLikelihood,
        severity: "Severity",
    ) -> None:
        '''
        :param target: -
        :param data_breach_probability: 
        :param data_breach_technical_assets: 
        :param exploitation_impact: 
        :param exploitation_likelihood: 
        :param severity: 
        '''
        options = RiskOptions(
            data_breach_probability=data_breach_probability,
            data_breach_technical_assets=data_breach_technical_assets,
            exploitation_impact=exploitation_impact,
            exploitation_likelihood=exploitation_likelihood,
            severity=severity,
        )

        return typing.cast(None, jsii.invoke(self, "identifiedAtTrustBoundary", [target, options]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="action")
    def action(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "action"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="asvs")
    def asvs(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "asvs"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cheatSheet")
    def cheat_sheet(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cheatSheet"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="check")
    def check(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "check"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cwe")
    def cwe(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "cwe"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="detectionLogic")
    def detection_logic(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "detectionLogic"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="falsePositives")
    def false_positives(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "falsePositives"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="function")
    def function(self) -> "RiskFunction":
        return typing.cast("RiskFunction", jsii.get(self, "function"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="impact")
    def impact(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "impact"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mitigation")
    def mitigation(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mitigation"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="riskAssessment")
    def risk_assessment(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "riskAssessment"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stride")
    def stride(self) -> "Stride":
        return typing.cast("Stride", jsii.get(self, "stride"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="modelFailurePossibleReason")
    def model_failure_possible_reason(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "modelFailurePossibleReason"))


@jsii.data_type(
    jsii_type="cdktg.RiskCategoryProps",
    jsii_struct_bases=[ResourceProps],
    name_mapping={
        "description": "description",
        "action": "action",
        "asvs": "asvs",
        "cheat_sheet": "cheatSheet",
        "check": "check",
        "cwe": "cwe",
        "detection_logic": "detectionLogic",
        "false_positives": "falsePositives",
        "function": "function",
        "impact": "impact",
        "mitigation": "mitigation",
        "risk_assessment": "riskAssessment",
        "stride": "stride",
        "model_failure_possible_reason": "modelFailurePossibleReason",
    },
)
class RiskCategoryProps(ResourceProps):
    def __init__(
        self,
        *,
        description: typing.Optional[builtins.str] = None,
        action: builtins.str,
        asvs: builtins.str,
        cheat_sheet: builtins.str,
        check: builtins.str,
        cwe: jsii.Number,
        detection_logic: builtins.str,
        false_positives: builtins.str,
        function: "RiskFunction",
        impact: builtins.str,
        mitigation: builtins.str,
        risk_assessment: builtins.str,
        stride: "Stride",
        model_failure_possible_reason: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param description: 
        :param action: 
        :param asvs: 
        :param cheat_sheet: 
        :param check: 
        :param cwe: 
        :param detection_logic: 
        :param false_positives: 
        :param function: 
        :param impact: 
        :param mitigation: 
        :param risk_assessment: 
        :param stride: 
        :param model_failure_possible_reason: 
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "action": action,
            "asvs": asvs,
            "cheat_sheet": cheat_sheet,
            "check": check,
            "cwe": cwe,
            "detection_logic": detection_logic,
            "false_positives": false_positives,
            "function": function,
            "impact": impact,
            "mitigation": mitigation,
            "risk_assessment": risk_assessment,
            "stride": stride,
        }
        if description is not None:
            self._values["description"] = description
        if model_failure_possible_reason is not None:
            self._values["model_failure_possible_reason"] = model_failure_possible_reason

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def action(self) -> builtins.str:
        result = self._values.get("action")
        assert result is not None, "Required property 'action' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def asvs(self) -> builtins.str:
        result = self._values.get("asvs")
        assert result is not None, "Required property 'asvs' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def cheat_sheet(self) -> builtins.str:
        result = self._values.get("cheat_sheet")
        assert result is not None, "Required property 'cheat_sheet' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def check(self) -> builtins.str:
        result = self._values.get("check")
        assert result is not None, "Required property 'check' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def cwe(self) -> jsii.Number:
        result = self._values.get("cwe")
        assert result is not None, "Required property 'cwe' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def detection_logic(self) -> builtins.str:
        result = self._values.get("detection_logic")
        assert result is not None, "Required property 'detection_logic' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def false_positives(self) -> builtins.str:
        result = self._values.get("false_positives")
        assert result is not None, "Required property 'false_positives' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def function(self) -> "RiskFunction":
        result = self._values.get("function")
        assert result is not None, "Required property 'function' is missing"
        return typing.cast("RiskFunction", result)

    @builtins.property
    def impact(self) -> builtins.str:
        result = self._values.get("impact")
        assert result is not None, "Required property 'impact' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def mitigation(self) -> builtins.str:
        result = self._values.get("mitigation")
        assert result is not None, "Required property 'mitigation' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def risk_assessment(self) -> builtins.str:
        result = self._values.get("risk_assessment")
        assert result is not None, "Required property 'risk_assessment' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def stride(self) -> "Stride":
        result = self._values.get("stride")
        assert result is not None, "Required property 'stride' is missing"
        return typing.cast("Stride", result)

    @builtins.property
    def model_failure_possible_reason(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("model_failure_possible_reason")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RiskCategoryProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="cdktg.RiskFunction")
class RiskFunction(enum.Enum):
    BUSINESS_SIDE = "BUSINESS_SIDE"
    ARCHITECTURE = "ARCHITECTURE"
    DEVELOPMENT = "DEVELOPMENT"
    OPERATIONS = "OPERATIONS"


@jsii.data_type(
    jsii_type="cdktg.RiskOptions",
    jsii_struct_bases=[],
    name_mapping={
        "data_breach_probability": "dataBreachProbability",
        "data_breach_technical_assets": "dataBreachTechnicalAssets",
        "exploitation_impact": "exploitationImpact",
        "exploitation_likelihood": "exploitationLikelihood",
        "severity": "severity",
    },
)
class RiskOptions:
    def __init__(
        self,
        *,
        data_breach_probability: DataBreachProbability,
        data_breach_technical_assets: typing.Sequence["TechnicalAsset"],
        exploitation_impact: ExploitationImpact,
        exploitation_likelihood: ExploitationLikelihood,
        severity: "Severity",
    ) -> None:
        '''
        :param data_breach_probability: 
        :param data_breach_technical_assets: 
        :param exploitation_impact: 
        :param exploitation_likelihood: 
        :param severity: 
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "data_breach_probability": data_breach_probability,
            "data_breach_technical_assets": data_breach_technical_assets,
            "exploitation_impact": exploitation_impact,
            "exploitation_likelihood": exploitation_likelihood,
            "severity": severity,
        }

    @builtins.property
    def data_breach_probability(self) -> DataBreachProbability:
        result = self._values.get("data_breach_probability")
        assert result is not None, "Required property 'data_breach_probability' is missing"
        return typing.cast(DataBreachProbability, result)

    @builtins.property
    def data_breach_technical_assets(self) -> typing.List["TechnicalAsset"]:
        result = self._values.get("data_breach_technical_assets")
        assert result is not None, "Required property 'data_breach_technical_assets' is missing"
        return typing.cast(typing.List["TechnicalAsset"], result)

    @builtins.property
    def exploitation_impact(self) -> ExploitationImpact:
        result = self._values.get("exploitation_impact")
        assert result is not None, "Required property 'exploitation_impact' is missing"
        return typing.cast(ExploitationImpact, result)

    @builtins.property
    def exploitation_likelihood(self) -> ExploitationLikelihood:
        result = self._values.get("exploitation_likelihood")
        assert result is not None, "Required property 'exploitation_likelihood' is missing"
        return typing.cast(ExploitationLikelihood, result)

    @builtins.property
    def severity(self) -> "Severity":
        result = self._values.get("severity")
        assert result is not None, "Required property 'severity' is missing"
        return typing.cast("Severity", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RiskOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdktg.RiskProps",
    jsii_struct_bases=[RiskOptions],
    name_mapping={
        "data_breach_probability": "dataBreachProbability",
        "data_breach_technical_assets": "dataBreachTechnicalAssets",
        "exploitation_impact": "exploitationImpact",
        "exploitation_likelihood": "exploitationLikelihood",
        "severity": "severity",
        "most_relevant_communication_link": "mostRelevantCommunicationLink",
        "most_relevant_data_asset": "mostRelevantDataAsset",
        "most_relevant_shared_runtime": "mostRelevantSharedRuntime",
        "most_relevant_technical_asset": "mostRelevantTechnicalAsset",
        "most_relevant_trust_boundary": "mostRelevantTrustBoundary",
    },
)
class RiskProps(RiskOptions):
    def __init__(
        self,
        *,
        data_breach_probability: DataBreachProbability,
        data_breach_technical_assets: typing.Sequence["TechnicalAsset"],
        exploitation_impact: ExploitationImpact,
        exploitation_likelihood: ExploitationLikelihood,
        severity: "Severity",
        most_relevant_communication_link: typing.Optional[Communication] = None,
        most_relevant_data_asset: typing.Optional["DataAsset"] = None,
        most_relevant_shared_runtime: typing.Optional["SharedRuntime"] = None,
        most_relevant_technical_asset: typing.Optional["TechnicalAsset"] = None,
        most_relevant_trust_boundary: typing.Optional["TrustBoundary"] = None,
    ) -> None:
        '''
        :param data_breach_probability: 
        :param data_breach_technical_assets: 
        :param exploitation_impact: 
        :param exploitation_likelihood: 
        :param severity: 
        :param most_relevant_communication_link: 
        :param most_relevant_data_asset: 
        :param most_relevant_shared_runtime: 
        :param most_relevant_technical_asset: 
        :param most_relevant_trust_boundary: 
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "data_breach_probability": data_breach_probability,
            "data_breach_technical_assets": data_breach_technical_assets,
            "exploitation_impact": exploitation_impact,
            "exploitation_likelihood": exploitation_likelihood,
            "severity": severity,
        }
        if most_relevant_communication_link is not None:
            self._values["most_relevant_communication_link"] = most_relevant_communication_link
        if most_relevant_data_asset is not None:
            self._values["most_relevant_data_asset"] = most_relevant_data_asset
        if most_relevant_shared_runtime is not None:
            self._values["most_relevant_shared_runtime"] = most_relevant_shared_runtime
        if most_relevant_technical_asset is not None:
            self._values["most_relevant_technical_asset"] = most_relevant_technical_asset
        if most_relevant_trust_boundary is not None:
            self._values["most_relevant_trust_boundary"] = most_relevant_trust_boundary

    @builtins.property
    def data_breach_probability(self) -> DataBreachProbability:
        result = self._values.get("data_breach_probability")
        assert result is not None, "Required property 'data_breach_probability' is missing"
        return typing.cast(DataBreachProbability, result)

    @builtins.property
    def data_breach_technical_assets(self) -> typing.List["TechnicalAsset"]:
        result = self._values.get("data_breach_technical_assets")
        assert result is not None, "Required property 'data_breach_technical_assets' is missing"
        return typing.cast(typing.List["TechnicalAsset"], result)

    @builtins.property
    def exploitation_impact(self) -> ExploitationImpact:
        result = self._values.get("exploitation_impact")
        assert result is not None, "Required property 'exploitation_impact' is missing"
        return typing.cast(ExploitationImpact, result)

    @builtins.property
    def exploitation_likelihood(self) -> ExploitationLikelihood:
        result = self._values.get("exploitation_likelihood")
        assert result is not None, "Required property 'exploitation_likelihood' is missing"
        return typing.cast(ExploitationLikelihood, result)

    @builtins.property
    def severity(self) -> "Severity":
        result = self._values.get("severity")
        assert result is not None, "Required property 'severity' is missing"
        return typing.cast("Severity", result)

    @builtins.property
    def most_relevant_communication_link(self) -> typing.Optional[Communication]:
        result = self._values.get("most_relevant_communication_link")
        return typing.cast(typing.Optional[Communication], result)

    @builtins.property
    def most_relevant_data_asset(self) -> typing.Optional["DataAsset"]:
        result = self._values.get("most_relevant_data_asset")
        return typing.cast(typing.Optional["DataAsset"], result)

    @builtins.property
    def most_relevant_shared_runtime(self) -> typing.Optional["SharedRuntime"]:
        result = self._values.get("most_relevant_shared_runtime")
        return typing.cast(typing.Optional["SharedRuntime"], result)

    @builtins.property
    def most_relevant_technical_asset(self) -> typing.Optional["TechnicalAsset"]:
        result = self._values.get("most_relevant_technical_asset")
        return typing.cast(typing.Optional["TechnicalAsset"], result)

    @builtins.property
    def most_relevant_trust_boundary(self) -> typing.Optional["TrustBoundary"]:
        result = self._values.get("most_relevant_trust_boundary")
        return typing.cast(typing.Optional["TrustBoundary"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RiskProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class RiskTracking(metaclass=jsii.JSIIMeta, jsii_type="cdktg.RiskTracking"):
    def __init__(
        self,
        id: builtins.str,
        *,
        checked_by: typing.Optional[builtins.str] = None,
        date: typing.Optional[builtins.str] = None,
        justification: typing.Optional[builtins.str] = None,
        status: typing.Optional["RiskTrackingStatus"] = None,
        ticket: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param id: -
        :param checked_by: 
        :param date: 
        :param justification: 
        :param status: 
        :param ticket: 
        '''
        props = RiskTrackingProps(
            checked_by=checked_by,
            date=date,
            justification=justification,
            status=status,
            ticket=ticket,
        )

        jsii.create(self.__class__, self, [id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="status")
    def status(self) -> "RiskTrackingStatus":
        return typing.cast("RiskTrackingStatus", jsii.get(self, "status"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="checkedBy")
    def checked_by(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "checkedBy"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="date")
    def date(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "date"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="justification")
    def justification(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "justification"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ticket")
    def ticket(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ticket"))


@jsii.data_type(
    jsii_type="cdktg.RiskTrackingProps",
    jsii_struct_bases=[],
    name_mapping={
        "checked_by": "checkedBy",
        "date": "date",
        "justification": "justification",
        "status": "status",
        "ticket": "ticket",
    },
)
class RiskTrackingProps:
    def __init__(
        self,
        *,
        checked_by: typing.Optional[builtins.str] = None,
        date: typing.Optional[builtins.str] = None,
        justification: typing.Optional[builtins.str] = None,
        status: typing.Optional["RiskTrackingStatus"] = None,
        ticket: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param checked_by: 
        :param date: 
        :param justification: 
        :param status: 
        :param ticket: 
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if checked_by is not None:
            self._values["checked_by"] = checked_by
        if date is not None:
            self._values["date"] = date
        if justification is not None:
            self._values["justification"] = justification
        if status is not None:
            self._values["status"] = status
        if ticket is not None:
            self._values["ticket"] = ticket

    @builtins.property
    def checked_by(self) -> typing.Optional[builtins.str]:
        result = self._values.get("checked_by")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def date(self) -> typing.Optional[builtins.str]:
        result = self._values.get("date")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def justification(self) -> typing.Optional[builtins.str]:
        result = self._values.get("justification")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def status(self) -> typing.Optional["RiskTrackingStatus"]:
        result = self._values.get("status")
        return typing.cast(typing.Optional["RiskTrackingStatus"], result)

    @builtins.property
    def ticket(self) -> typing.Optional[builtins.str]:
        result = self._values.get("ticket")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RiskTrackingProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="cdktg.RiskTrackingStatus")
class RiskTrackingStatus(enum.Enum):
    UNCHECKED = "UNCHECKED"
    IN_DISCUSSION = "IN_DISCUSSION"
    ACCEPTED = "ACCEPTED"
    IN_PROGRESS = "IN_PROGRESS"
    MITIGATED = "MITIGATED"
    FALSE_POSITIVE = "FALSE_POSITIVE"


class Scope(metaclass=jsii.JSIIMeta, jsii_type="cdktg.Scope"):
    def __init__(
        self,
        out: builtins.bool,
        justification: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param out: -
        :param justification: -
        '''
        jsii.create(self.__class__, self, [out, justification])

    @jsii.member(jsii_name="inScope") # type: ignore[misc]
    @builtins.classmethod
    def in_scope(cls, justification: typing.Optional[builtins.str] = None) -> "Scope":
        '''
        :param justification: -
        '''
        return typing.cast("Scope", jsii.sinvoke(cls, "inScope", [justification]))

    @jsii.member(jsii_name="outOfScope") # type: ignore[misc]
    @builtins.classmethod
    def out_of_scope(
        cls,
        justification: typing.Optional[builtins.str] = None,
    ) -> "Scope":
        '''
        :param justification: -
        '''
        return typing.cast("Scope", jsii.sinvoke(cls, "outOfScope", [justification]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="justification")
    def justification(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "justification"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="out")
    def out(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "out"))

    @out.setter
    def out(self, value: builtins.bool) -> None:
        jsii.set(self, "out", value)


class SecurityRequirement(
    metaclass=jsii.JSIIMeta,
    jsii_type="cdktg.SecurityRequirement",
):
    def __init__(self, *, description: builtins.str, name: builtins.str) -> None:
        '''
        :param description: 
        :param name: 
        '''
        props = SecurityRequirementProps(description=description, name=name)

        jsii.create(self.__class__, self, [props])

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="INPUT_VALIDATION")
    def INPUT_VALIDATION(cls) -> "SecurityRequirement":
        return typing.cast("SecurityRequirement", jsii.sget(cls, "INPUT_VALIDATION"))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="SECURING_ADMINISTRATIVE_ACCESS")
    def SECURING_ADMINISTRATIVE_ACCESS(cls) -> "SecurityRequirement":
        return typing.cast("SecurityRequirement", jsii.sget(cls, "SECURING_ADMINISTRATIVE_ACCESS"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))


@jsii.data_type(
    jsii_type="cdktg.SecurityRequirementProps",
    jsii_struct_bases=[],
    name_mapping={"description": "description", "name": "name"},
)
class SecurityRequirementProps:
    def __init__(self, *, description: builtins.str, name: builtins.str) -> None:
        '''
        :param description: 
        :param name: 
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "description": description,
            "name": name,
        }

    @builtins.property
    def description(self) -> builtins.str:
        result = self._values.get("description")
        assert result is not None, "Required property 'description' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecurityRequirementProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="cdktg.Severity")
class Severity(enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    ELEVATED = "ELEVATED"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class SharedRuntime(Resource, metaclass=jsii.JSIIMeta, jsii_type="cdktg.SharedRuntime"):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
        description: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param tags: 
        :param description: 
        '''
        props = SharedRuntimeProps(tags=tags, description=description)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="runs")
    def runs(self, *assets: "TechnicalAsset") -> None:
        '''
        :param assets: -
        '''
        return typing.cast(None, jsii.invoke(self, "runs", [*assets]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "tags"))


@jsii.data_type(
    jsii_type="cdktg.SharedRuntimeProps",
    jsii_struct_bases=[ResourceProps],
    name_mapping={"description": "description", "tags": "tags"},
)
class SharedRuntimeProps(ResourceProps):
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
        return "SharedRuntimeProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="cdktg.Size")
class Size(enum.Enum):
    SYSTEM = "SYSTEM"
    SERVICE = "SERVICE"
    APPLICATION = "APPLICATION"
    COMPONENT = "COMPONENT"


@jsii.enum(jsii_type="cdktg.Stride")
class Stride(enum.Enum):
    SPOOFING = "SPOOFING"
    TAMPERING = "TAMPERING"
    REPUDIATION = "REPUDIATION"
    INFORMATION_DISCLOSURE = "INFORMATION_DISCLOSURE"
    DENIAL_OF_SERVICE = "DENIAL_OF_SERVICE"
    ELEVATION_OF_PRIVILEGE = "ELEVATION_OF_PRIVILEGE"


class TechnicalAsset(
    Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdktg.TechnicalAsset",
):
    def __init__(
        self,
        scope_: constructs.Construct,
        id: builtins.str,
        *,
        cia_triad: CIATriad,
        encryption: Encryption,
        human_use: builtins.bool,
        internet: builtins.bool,
        machine: Machine,
        multi_tenant: builtins.bool,
        redundant: builtins.bool,
        size: Size,
        technology: "Technology",
        type: "TechnicalAssetType",
        usage: "Usage",
        custom_developed_parts: typing.Optional[builtins.bool] = None,
        data_formats_accepted: typing.Optional[typing.Sequence[DataFormat]] = None,
        owner: typing.Optional[builtins.str] = None,
        scope: typing.Optional[Scope] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
        trust_boundary: typing.Optional["TrustBoundary"] = None,
        description: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope_: -
        :param id: -
        :param cia_triad: 
        :param encryption: 
        :param human_use: 
        :param internet: 
        :param machine: 
        :param multi_tenant: 
        :param redundant: 
        :param size: 
        :param technology: 
        :param type: 
        :param usage: 
        :param custom_developed_parts: 
        :param data_formats_accepted: 
        :param owner: 
        :param scope: 
        :param tags: 
        :param trust_boundary: 
        :param description: 
        '''
        props = TechnicalAssetProps(
            cia_triad=cia_triad,
            encryption=encryption,
            human_use=human_use,
            internet=internet,
            machine=machine,
            multi_tenant=multi_tenant,
            redundant=redundant,
            size=size,
            technology=technology,
            type=type,
            usage=usage,
            custom_developed_parts=custom_developed_parts,
            data_formats_accepted=data_formats_accepted,
            owner=owner,
            scope=scope,
            tags=tags,
            trust_boundary=trust_boundary,
            description=description,
        )

        jsii.create(self.__class__, self, [scope_, id, props])

    @jsii.member(jsii_name="communicatesWith")
    def communicates_with(
        self,
        id: builtins.str,
        target: "TechnicalAsset",
        *,
        authentication: Authentication,
        authorization: Authorization,
        description: builtins.str,
        ip_filtered: builtins.bool,
        protocol: Protocol,
        readonly: builtins.bool,
        usage: "Usage",
        vpn: builtins.bool,
    ) -> Communication:
        '''
        :param id: -
        :param target: -
        :param authentication: 
        :param authorization: 
        :param description: 
        :param ip_filtered: 
        :param protocol: 
        :param readonly: 
        :param usage: 
        :param vpn: 
        '''
        options = CommunicationOptions(
            authentication=authentication,
            authorization=authorization,
            description=description,
            ip_filtered=ip_filtered,
            protocol=protocol,
            readonly=readonly,
            usage=usage,
            vpn=vpn,
        )

        return typing.cast(Communication, jsii.invoke(self, "communicatesWith", [id, target, options]))

    @jsii.member(jsii_name="isTrafficForwarding")
    def is_traffic_forwarding(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.invoke(self, "isTrafficForwarding", []))

    @jsii.member(jsii_name="isWebApplication")
    def is_web_application(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.invoke(self, "isWebApplication", []))

    @jsii.member(jsii_name="isWebService")
    def is_web_service(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.invoke(self, "isWebService", []))

    @jsii.member(jsii_name="processes")
    def processes(self, *assets: "DataAsset") -> None:
        '''
        :param assets: -
        '''
        return typing.cast(None, jsii.invoke(self, "processes", [*assets]))

    @jsii.member(jsii_name="stores")
    def stores(self, *assets: "DataAsset") -> None:
        '''
        :param assets: -
        '''
        return typing.cast(None, jsii.invoke(self, "stores", [*assets]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ciaTriad")
    def cia_triad(self) -> CIATriad:
        return typing.cast(CIATriad, jsii.get(self, "ciaTriad"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="customDevelopedParts")
    def custom_developed_parts(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "customDevelopedParts"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encryption")
    def encryption(self) -> Encryption:
        return typing.cast(Encryption, jsii.get(self, "encryption"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="highestAvailability")
    def highest_availability(self) -> Availability:
        return typing.cast(Availability, jsii.get(self, "highestAvailability"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="highestIntegrity")
    def highest_integrity(self) -> Integrity:
        return typing.cast(Integrity, jsii.get(self, "highestIntegrity"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="humanUse")
    def human_use(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "humanUse"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internet")
    def internet(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "internet"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="machine")
    def machine(self) -> Machine:
        return typing.cast(Machine, jsii.get(self, "machine"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="multiTenant")
    def multi_tenant(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "multiTenant"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="redundant")
    def redundant(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "redundant"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="size")
    def size(self) -> Size:
        return typing.cast(Size, jsii.get(self, "size"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="technology")
    def technology(self) -> "Technology":
        return typing.cast("Technology", jsii.get(self, "technology"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> "TechnicalAssetType":
        return typing.cast("TechnicalAssetType", jsii.get(self, "type"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="usage")
    def usage(self) -> "Usage":
        return typing.cast("Usage", jsii.get(self, "usage"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dataFormatsAccepted")
    def data_formats_accepted(self) -> typing.Optional[typing.List[DataFormat]]:
        return typing.cast(typing.Optional[typing.List[DataFormat]], jsii.get(self, "dataFormatsAccepted"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="owner")
    def owner(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "owner"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="scope")
    def scope(self) -> typing.Optional[Scope]:
        return typing.cast(typing.Optional[Scope], jsii.get(self, "scope"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "tags"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="trustBoundary")
    def _trust_boundary(self) -> typing.Optional["TrustBoundary"]:
        return typing.cast(typing.Optional["TrustBoundary"], jsii.get(self, "trustBoundary"))

    @_trust_boundary.setter
    def _trust_boundary(self, value: typing.Optional["TrustBoundary"]) -> None:
        jsii.set(self, "trustBoundary", value)


@jsii.data_type(
    jsii_type="cdktg.TechnicalAssetProps",
    jsii_struct_bases=[ResourceProps],
    name_mapping={
        "description": "description",
        "cia_triad": "ciaTriad",
        "encryption": "encryption",
        "human_use": "humanUse",
        "internet": "internet",
        "machine": "machine",
        "multi_tenant": "multiTenant",
        "redundant": "redundant",
        "size": "size",
        "technology": "technology",
        "type": "type",
        "usage": "usage",
        "custom_developed_parts": "customDevelopedParts",
        "data_formats_accepted": "dataFormatsAccepted",
        "owner": "owner",
        "scope": "scope",
        "tags": "tags",
        "trust_boundary": "trustBoundary",
    },
)
class TechnicalAssetProps(ResourceProps):
    def __init__(
        self,
        *,
        description: typing.Optional[builtins.str] = None,
        cia_triad: CIATriad,
        encryption: Encryption,
        human_use: builtins.bool,
        internet: builtins.bool,
        machine: Machine,
        multi_tenant: builtins.bool,
        redundant: builtins.bool,
        size: Size,
        technology: "Technology",
        type: "TechnicalAssetType",
        usage: "Usage",
        custom_developed_parts: typing.Optional[builtins.bool] = None,
        data_formats_accepted: typing.Optional[typing.Sequence[DataFormat]] = None,
        owner: typing.Optional[builtins.str] = None,
        scope: typing.Optional[Scope] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
        trust_boundary: typing.Optional["TrustBoundary"] = None,
    ) -> None:
        '''
        :param description: 
        :param cia_triad: 
        :param encryption: 
        :param human_use: 
        :param internet: 
        :param machine: 
        :param multi_tenant: 
        :param redundant: 
        :param size: 
        :param technology: 
        :param type: 
        :param usage: 
        :param custom_developed_parts: 
        :param data_formats_accepted: 
        :param owner: 
        :param scope: 
        :param tags: 
        :param trust_boundary: 
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "cia_triad": cia_triad,
            "encryption": encryption,
            "human_use": human_use,
            "internet": internet,
            "machine": machine,
            "multi_tenant": multi_tenant,
            "redundant": redundant,
            "size": size,
            "technology": technology,
            "type": type,
            "usage": usage,
        }
        if description is not None:
            self._values["description"] = description
        if custom_developed_parts is not None:
            self._values["custom_developed_parts"] = custom_developed_parts
        if data_formats_accepted is not None:
            self._values["data_formats_accepted"] = data_formats_accepted
        if owner is not None:
            self._values["owner"] = owner
        if scope is not None:
            self._values["scope"] = scope
        if tags is not None:
            self._values["tags"] = tags
        if trust_boundary is not None:
            self._values["trust_boundary"] = trust_boundary

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cia_triad(self) -> CIATriad:
        result = self._values.get("cia_triad")
        assert result is not None, "Required property 'cia_triad' is missing"
        return typing.cast(CIATriad, result)

    @builtins.property
    def encryption(self) -> Encryption:
        result = self._values.get("encryption")
        assert result is not None, "Required property 'encryption' is missing"
        return typing.cast(Encryption, result)

    @builtins.property
    def human_use(self) -> builtins.bool:
        result = self._values.get("human_use")
        assert result is not None, "Required property 'human_use' is missing"
        return typing.cast(builtins.bool, result)

    @builtins.property
    def internet(self) -> builtins.bool:
        result = self._values.get("internet")
        assert result is not None, "Required property 'internet' is missing"
        return typing.cast(builtins.bool, result)

    @builtins.property
    def machine(self) -> Machine:
        result = self._values.get("machine")
        assert result is not None, "Required property 'machine' is missing"
        return typing.cast(Machine, result)

    @builtins.property
    def multi_tenant(self) -> builtins.bool:
        result = self._values.get("multi_tenant")
        assert result is not None, "Required property 'multi_tenant' is missing"
        return typing.cast(builtins.bool, result)

    @builtins.property
    def redundant(self) -> builtins.bool:
        result = self._values.get("redundant")
        assert result is not None, "Required property 'redundant' is missing"
        return typing.cast(builtins.bool, result)

    @builtins.property
    def size(self) -> Size:
        result = self._values.get("size")
        assert result is not None, "Required property 'size' is missing"
        return typing.cast(Size, result)

    @builtins.property
    def technology(self) -> "Technology":
        result = self._values.get("technology")
        assert result is not None, "Required property 'technology' is missing"
        return typing.cast("Technology", result)

    @builtins.property
    def type(self) -> "TechnicalAssetType":
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast("TechnicalAssetType", result)

    @builtins.property
    def usage(self) -> "Usage":
        result = self._values.get("usage")
        assert result is not None, "Required property 'usage' is missing"
        return typing.cast("Usage", result)

    @builtins.property
    def custom_developed_parts(self) -> typing.Optional[builtins.bool]:
        result = self._values.get("custom_developed_parts")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def data_formats_accepted(self) -> typing.Optional[typing.List[DataFormat]]:
        result = self._values.get("data_formats_accepted")
        return typing.cast(typing.Optional[typing.List[DataFormat]], result)

    @builtins.property
    def owner(self) -> typing.Optional[builtins.str]:
        result = self._values.get("owner")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def scope(self) -> typing.Optional[Scope]:
        result = self._values.get("scope")
        return typing.cast(typing.Optional[Scope], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[builtins.str]]:
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def trust_boundary(self) -> typing.Optional["TrustBoundary"]:
        result = self._values.get("trust_boundary")
        return typing.cast(typing.Optional["TrustBoundary"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TechnicalAssetProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="cdktg.TechnicalAssetType")
class TechnicalAssetType(enum.Enum):
    EXTERNAL_ENTITY = "EXTERNAL_ENTITY"
    PROCESS = "PROCESS"
    DATASTORE = "DATASTORE"


@jsii.enum(jsii_type="cdktg.Technology")
class Technology(enum.Enum):
    UNKNOWN = "UNKNOWN"
    CLIENT_SYSTEM = "CLIENT_SYSTEM"
    BROWSER = "BROWSER"
    DESKTOP = "DESKTOP"
    MOBILE_APP = "MOBILE_APP"
    DEVOPS_CLIENT = "DEVOPS_CLIENT"
    WEB_SERVER = "WEB_SERVER"
    WEB_APPLICATION = "WEB_APPLICATION"
    APPLICATION_SERVER = "APPLICATION_SERVER"
    DATABASE = "DATABASE"
    FILE_SERVER = "FILE_SERVER"
    LOCAL_FILE_SERVER = "LOCAL_FILE_SERVER"
    ERP = "ERP"
    CMS = "CMS"
    WEB_SERVICE_REST = "WEB_SERVICE_REST"
    WEB_SERVICE_SOAP = "WEB_SERVICE_SOAP"
    EJB = "EJB"
    SEARCH_INDEX = "SEARCH_INDEX"
    SEARCH_ENGINE = "SEARCH_ENGINE"
    SERVICE_REGISTRY = "SERVICE_REGISTRY"
    REVERSE_PROXY = "REVERSE_PROXY"
    LOAD_BALANCER = "LOAD_BALANCER"
    BUILD_PIPELINE = "BUILD_PIPELINE"
    SOURCECODE_REPOSITORY = "SOURCECODE_REPOSITORY"
    ARTIFACT_REGISTRY = "ARTIFACT_REGISTRY"
    CODE_INSPECTION_PLATFORM = "CODE_INSPECTION_PLATFORM"
    MONITORING = "MONITORING"
    LDAP_SERVER = "LDAP_SERVER"
    CONTAINER_PLATFORM = "CONTAINER_PLATFORM"
    BATCH_PROCESSING = "BATCH_PROCESSING"
    EVENT_LISTENER = "EVENT_LISTENER"
    IDENTITIY_PROVIDER = "IDENTITIY_PROVIDER"
    IDENTITY_STORE_LDAP = "IDENTITY_STORE_LDAP"
    IDENTITY_STORE_DATABASE = "IDENTITY_STORE_DATABASE"
    TOOL = "TOOL"
    CLI = "CLI"
    TASK = "TASK"
    FUNCTION = "FUNCTION"
    GATEWAY = "GATEWAY"
    IOT_DEVICE = "IOT_DEVICE"
    MESSAGE_QUEUE = "MESSAGE_QUEUE"
    STREAM_PROCESSING = "STREAM_PROCESSING"
    SERVICE_MESH = "SERVICE_MESH"
    DATA_LAKE = "DATA_LAKE"
    REPORT_ENGINE = "REPORT_ENGINE"
    AI = "AI"
    MAIL_SERVER = "MAIL_SERVER"
    VAULT = "VAULT"
    HASM = "HASM"
    WAF = "WAF"
    IDS = "IDS"
    IPS = "IPS"
    SCHEDULER = "SCHEDULER"
    MAINFRAME = "MAINFRAME"
    BLOCK_STORAGE = "BLOCK_STORAGE"
    LIBRARY = "LIBRARY"


class Testing(metaclass=jsii.JSIIMeta, jsii_type="cdktg.Testing"):
    '''Testing utilities for cdktg models.'''

    @jsii.member(jsii_name="model") # type: ignore[misc]
    @builtins.classmethod
    def model(cls) -> Model:
        return typing.cast(Model, jsii.sinvoke(cls, "model", []))


class TrustBoundary(Resource, metaclass=jsii.JSIIMeta, jsii_type="cdktg.TrustBoundary"):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        type: "TrustBoundaryType",
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
        description: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param type: 
        :param tags: 
        :param description: 
        '''
        props = TrustBoundaryProps(type=type, tags=tags, description=description)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="addTechnicalAssets")
    def add_technical_assets(self, *assets: TechnicalAsset) -> None:
        '''
        :param assets: -
        '''
        return typing.cast(None, jsii.invoke(self, "addTechnicalAssets", [*assets]))

    @jsii.member(jsii_name="addTrustBoundary")
    def add_trust_boundary(self, boundary: "TrustBoundary") -> None:
        '''
        :param boundary: -
        '''
        return typing.cast(None, jsii.invoke(self, "addTrustBoundary", [boundary]))

    @jsii.member(jsii_name="isNetworkBoundary")
    def is_network_boundary(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.invoke(self, "isNetworkBoundary", []))

    @jsii.member(jsii_name="isWithinCloud")
    def is_within_cloud(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.invoke(self, "isWithinCloud", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="type")
    def type(self) -> "TrustBoundaryType":
        return typing.cast("TrustBoundaryType", jsii.get(self, "type"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "tags"))


@jsii.data_type(
    jsii_type="cdktg.TrustBoundaryProps",
    jsii_struct_bases=[ResourceProps],
    name_mapping={"description": "description", "type": "type", "tags": "tags"},
)
class TrustBoundaryProps(ResourceProps):
    def __init__(
        self,
        *,
        description: typing.Optional[builtins.str] = None,
        type: "TrustBoundaryType",
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param description: 
        :param type: 
        :param tags: 
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "type": type,
        }
        if description is not None:
            self._values["description"] = description
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type(self) -> "TrustBoundaryType":
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast("TrustBoundaryType", result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[builtins.str]]:
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TrustBoundaryProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="cdktg.TrustBoundaryType")
class TrustBoundaryType(enum.Enum):
    NETWORK_ON_PREM = "NETWORK_ON_PREM"
    NETWORK_DEDICATED_HOSTER = "NETWORK_DEDICATED_HOSTER"
    NETWORK_VIRTUAL_LAN = "NETWORK_VIRTUAL_LAN"
    NETWORK_CLOUD_PROVIDER = "NETWORK_CLOUD_PROVIDER"
    NETWORK_CLOUD_SECURITY_GROUP = "NETWORK_CLOUD_SECURITY_GROUP"
    NETWORK_POLICY_NAMESPACE_ISOLATION = "NETWORK_POLICY_NAMESPACE_ISOLATION"
    EXECUTION_ENVIRONMENT = "EXECUTION_ENVIRONMENT"


@jsii.enum(jsii_type="cdktg.Usage")
class Usage(enum.Enum):
    BUSINESS = "BUSINESS"
    DEVOPS = "DEVOPS"


class DataAsset(Resource, metaclass=jsii.JSIIMeta, jsii_type="cdktg.DataAsset"):
    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        cia_triad: CIATriad,
        quantity: Quantity,
        usage: Usage,
        origin: typing.Optional[builtins.str] = None,
        owner: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
        description: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param cia_triad: 
        :param quantity: 
        :param usage: 
        :param origin: 
        :param owner: 
        :param tags: 
        :param description: 
        '''
        props = DataAssetProps(
            cia_triad=cia_triad,
            quantity=quantity,
            usage=usage,
            origin=origin,
            owner=owner,
            tags=tags,
            description=description,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ciaTriad")
    def cia_triad(self) -> CIATriad:
        return typing.cast(CIATriad, jsii.get(self, "ciaTriad"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="quantity")
    def quantity(self) -> Quantity:
        return typing.cast(Quantity, jsii.get(self, "quantity"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="usage")
    def usage(self) -> Usage:
        return typing.cast(Usage, jsii.get(self, "usage"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="origin")
    def origin(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "origin"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="owner")
    def owner(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "owner"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "tags"))


@jsii.data_type(
    jsii_type="cdktg.DataAssetProps",
    jsii_struct_bases=[ResourceProps],
    name_mapping={
        "description": "description",
        "cia_triad": "ciaTriad",
        "quantity": "quantity",
        "usage": "usage",
        "origin": "origin",
        "owner": "owner",
        "tags": "tags",
    },
)
class DataAssetProps(ResourceProps):
    def __init__(
        self,
        *,
        description: typing.Optional[builtins.str] = None,
        cia_triad: CIATriad,
        quantity: Quantity,
        usage: Usage,
        origin: typing.Optional[builtins.str] = None,
        owner: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param description: 
        :param cia_triad: 
        :param quantity: 
        :param usage: 
        :param origin: 
        :param owner: 
        :param tags: 
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "cia_triad": cia_triad,
            "quantity": quantity,
            "usage": usage,
        }
        if description is not None:
            self._values["description"] = description
        if origin is not None:
            self._values["origin"] = origin
        if owner is not None:
            self._values["owner"] = owner
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cia_triad(self) -> CIATriad:
        result = self._values.get("cia_triad")
        assert result is not None, "Required property 'cia_triad' is missing"
        return typing.cast(CIATriad, result)

    @builtins.property
    def quantity(self) -> Quantity:
        result = self._values.get("quantity")
        assert result is not None, "Required property 'quantity' is missing"
        return typing.cast(Quantity, result)

    @builtins.property
    def usage(self) -> Usage:
        result = self._values.get("usage")
        assert result is not None, "Required property 'usage' is missing"
        return typing.cast(Usage, result)

    @builtins.property
    def origin(self) -> typing.Optional[builtins.str]:
        result = self._values.get("origin")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def owner(self) -> typing.Optional[builtins.str]:
        result = self._values.get("owner")
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
        return "DataAssetProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "AbuseCase",
    "AbuseCaseProps",
    "AnnotationMetadataEntryType",
    "Annotations",
    "Aspects",
    "Authentication",
    "Author",
    "AuthorProps",
    "Authorization",
    "Availability",
    "BusinessCriticality",
    "CIATriad",
    "CIATriadProps",
    "Communication",
    "CommunicationOptions",
    "CommunicationProps",
    "Confidentiality",
    "DataAsset",
    "DataAssetProps",
    "DataBreachProbability",
    "DataFormat",
    "Encryption",
    "ExploitationImpact",
    "ExploitationLikelihood",
    "IAspect",
    "ICustomSynthesis",
    "IManifest",
    "IModelSynthesizer",
    "ISynthesisSession",
    "Image",
    "Integrity",
    "Machine",
    "Manifest",
    "Model",
    "ModelAnnotation",
    "ModelManifest",
    "ModelProps",
    "ModelSynthesizer",
    "OutOfScopeProps",
    "Overview",
    "OverviewProps",
    "Project",
    "ProjectProps",
    "Protocol",
    "Quantity",
    "Question",
    "Resource",
    "ResourceProps",
    "Risk",
    "RiskCategory",
    "RiskCategoryProps",
    "RiskFunction",
    "RiskOptions",
    "RiskProps",
    "RiskTracking",
    "RiskTrackingProps",
    "RiskTrackingStatus",
    "Scope",
    "SecurityRequirement",
    "SecurityRequirementProps",
    "Severity",
    "SharedRuntime",
    "SharedRuntimeProps",
    "Size",
    "Stride",
    "TechnicalAsset",
    "TechnicalAssetProps",
    "TechnicalAssetType",
    "Technology",
    "Testing",
    "TrustBoundary",
    "TrustBoundaryProps",
    "TrustBoundaryType",
    "Usage",
    "plus",
    "plus_aws",
]

publication.publish()

# Loading modules to ensure their types are registered with the jsii runtime library
from . import plus
from . import plus_aws
