import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from .._jsii import *

import cdktf
import constructs


class LightsailContainerService(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lightsail.LightsailContainerService",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service aws_lightsail_container_service}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        power: builtins.str,
        scale: jsii.Number,
        id: typing.Optional[builtins.str] = None,
        is_disabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        public_domain_names: typing.Optional["LightsailContainerServicePublicDomainNames"] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        tags_all: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        timeouts: typing.Optional["LightsailContainerServiceTimeouts"] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service aws_lightsail_container_service} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service#name LightsailContainerService#name}.
        :param power: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service#power LightsailContainerService#power}.
        :param scale: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service#scale LightsailContainerService#scale}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service#id LightsailContainerService#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param is_disabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service#is_disabled LightsailContainerService#is_disabled}.
        :param public_domain_names: public_domain_names block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service#public_domain_names LightsailContainerService#public_domain_names}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service#tags LightsailContainerService#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service#tags_all LightsailContainerService#tags_all}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service#timeouts LightsailContainerService#timeouts}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = LightsailContainerServiceConfig(
            name=name,
            power=power,
            scale=scale,
            id=id,
            is_disabled=is_disabled,
            public_domain_names=public_domain_names,
            tags=tags,
            tags_all=tags_all,
            timeouts=timeouts,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="putPublicDomainNames")
    def put_public_domain_names(
        self,
        *,
        certificate: typing.Union[cdktf.IResolvable, typing.Sequence["LightsailContainerServicePublicDomainNamesCertificate"]],
    ) -> None:
        '''
        :param certificate: certificate block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service#certificate LightsailContainerService#certificate}
        '''
        value = LightsailContainerServicePublicDomainNames(certificate=certificate)

        return typing.cast(None, jsii.invoke(self, "putPublicDomainNames", [value]))

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service#create LightsailContainerService#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service#delete LightsailContainerService#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service#update LightsailContainerService#update}.
        '''
        value = LightsailContainerServiceTimeouts(
            create=create, delete=delete, update=update
        )

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetIsDisabled")
    def reset_is_disabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsDisabled", []))

    @jsii.member(jsii_name="resetPublicDomainNames")
    def reset_public_domain_names(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPublicDomainNames", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="resetTimeouts")
    def reset_timeouts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeouts", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="availabilityZone")
    def availability_zone(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "availabilityZone"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdAt"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="powerId")
    def power_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "powerId"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="principalArn")
    def principal_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "principalArn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="privateDomainName")
    def private_domain_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "privateDomainName"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publicDomainNames")
    def public_domain_names(
        self,
    ) -> "LightsailContainerServicePublicDomainNamesOutputReference":
        return typing.cast("LightsailContainerServicePublicDomainNamesOutputReference", jsii.get(self, "publicDomainNames"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="resourceType")
    def resource_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "resourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "LightsailContainerServiceTimeoutsOutputReference":
        return typing.cast("LightsailContainerServiceTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="isDisabledInput")
    def is_disabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "isDisabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="powerInput")
    def power_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "powerInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publicDomainNamesInput")
    def public_domain_names_input(
        self,
    ) -> typing.Optional["LightsailContainerServicePublicDomainNames"]:
        return typing.cast(typing.Optional["LightsailContainerServicePublicDomainNames"], jsii.get(self, "publicDomainNamesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="scaleInput")
    def scale_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "scaleInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAllInput")
    def tags_all_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tagsAllInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(
        self,
    ) -> typing.Optional[typing.Union["LightsailContainerServiceTimeouts", cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union["LightsailContainerServiceTimeouts", cdktf.IResolvable]], jsii.get(self, "timeoutsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="isDisabled")
    def is_disabled(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "isDisabled"))

    @is_disabled.setter
    def is_disabled(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "isDisabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="power")
    def power(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "power"))

    @power.setter
    def power(self, value: builtins.str) -> None:
        jsii.set(self, "power", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="scale")
    def scale(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "scale"))

    @scale.setter
    def scale(self, value: jsii.Number) -> None:
        jsii.set(self, "scale", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        jsii.set(self, "tags", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAll")
    def tags_all(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tagsAll"))

    @tags_all.setter
    def tags_all(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        jsii.set(self, "tagsAll", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lightsail.LightsailContainerServiceConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "power": "power",
        "scale": "scale",
        "id": "id",
        "is_disabled": "isDisabled",
        "public_domain_names": "publicDomainNames",
        "tags": "tags",
        "tags_all": "tagsAll",
        "timeouts": "timeouts",
    },
)
class LightsailContainerServiceConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        power: builtins.str,
        scale: jsii.Number,
        id: typing.Optional[builtins.str] = None,
        is_disabled: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        public_domain_names: typing.Optional["LightsailContainerServicePublicDomainNames"] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        tags_all: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        timeouts: typing.Optional["LightsailContainerServiceTimeouts"] = None,
    ) -> None:
        '''AWS Lightsail.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service#name LightsailContainerService#name}.
        :param power: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service#power LightsailContainerService#power}.
        :param scale: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service#scale LightsailContainerService#scale}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service#id LightsailContainerService#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param is_disabled: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service#is_disabled LightsailContainerService#is_disabled}.
        :param public_domain_names: public_domain_names block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service#public_domain_names LightsailContainerService#public_domain_names}
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service#tags LightsailContainerService#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service#tags_all LightsailContainerService#tags_all}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service#timeouts LightsailContainerService#timeouts}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(public_domain_names, dict):
            public_domain_names = LightsailContainerServicePublicDomainNames(**public_domain_names)
        if isinstance(timeouts, dict):
            timeouts = LightsailContainerServiceTimeouts(**timeouts)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "power": power,
            "scale": scale,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if id is not None:
            self._values["id"] = id
        if is_disabled is not None:
            self._values["is_disabled"] = is_disabled
        if public_domain_names is not None:
            self._values["public_domain_names"] = public_domain_names
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all
        if timeouts is not None:
            self._values["timeouts"] = timeouts

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service#name LightsailContainerService#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def power(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service#power LightsailContainerService#power}.'''
        result = self._values.get("power")
        assert result is not None, "Required property 'power' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def scale(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service#scale LightsailContainerService#scale}.'''
        result = self._values.get("scale")
        assert result is not None, "Required property 'scale' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service#id LightsailContainerService#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def is_disabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service#is_disabled LightsailContainerService#is_disabled}.'''
        result = self._values.get("is_disabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def public_domain_names(
        self,
    ) -> typing.Optional["LightsailContainerServicePublicDomainNames"]:
        '''public_domain_names block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service#public_domain_names LightsailContainerService#public_domain_names}
        '''
        result = self._values.get("public_domain_names")
        return typing.cast(typing.Optional["LightsailContainerServicePublicDomainNames"], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service#tags LightsailContainerService#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def tags_all(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service#tags_all LightsailContainerService#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["LightsailContainerServiceTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service#timeouts LightsailContainerService#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["LightsailContainerServiceTimeouts"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LightsailContainerServiceConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LightsailContainerServiceDeploymentVersion(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lightsail.LightsailContainerServiceDeploymentVersion",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service_deployment_version aws_lightsail_container_service_deployment_version}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        container: typing.Union[cdktf.IResolvable, typing.Sequence["LightsailContainerServiceDeploymentVersionContainer"]],
        service_name: builtins.str,
        id: typing.Optional[builtins.str] = None,
        public_endpoint: typing.Optional["LightsailContainerServiceDeploymentVersionPublicEndpoint"] = None,
        timeouts: typing.Optional["LightsailContainerServiceDeploymentVersionTimeouts"] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service_deployment_version aws_lightsail_container_service_deployment_version} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param container: container block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service_deployment_version#container LightsailContainerServiceDeploymentVersion#container}
        :param service_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service_deployment_version#service_name LightsailContainerServiceDeploymentVersion#service_name}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service_deployment_version#id LightsailContainerServiceDeploymentVersion#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param public_endpoint: public_endpoint block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service_deployment_version#public_endpoint LightsailContainerServiceDeploymentVersion#public_endpoint}
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service_deployment_version#timeouts LightsailContainerServiceDeploymentVersion#timeouts}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = LightsailContainerServiceDeploymentVersionConfig(
            container=container,
            service_name=service_name,
            id=id,
            public_endpoint=public_endpoint,
            timeouts=timeouts,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="putContainer")
    def put_container(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence["LightsailContainerServiceDeploymentVersionContainer"]],
    ) -> None:
        '''
        :param value: -
        '''
        return typing.cast(None, jsii.invoke(self, "putContainer", [value]))

    @jsii.member(jsii_name="putPublicEndpoint")
    def put_public_endpoint(
        self,
        *,
        container_name: builtins.str,
        container_port: jsii.Number,
        health_check: "LightsailContainerServiceDeploymentVersionPublicEndpointHealthCheck",
    ) -> None:
        '''
        :param container_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service_deployment_version#container_name LightsailContainerServiceDeploymentVersion#container_name}.
        :param container_port: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service_deployment_version#container_port LightsailContainerServiceDeploymentVersion#container_port}.
        :param health_check: health_check block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service_deployment_version#health_check LightsailContainerServiceDeploymentVersion#health_check}
        '''
        value = LightsailContainerServiceDeploymentVersionPublicEndpoint(
            container_name=container_name,
            container_port=container_port,
            health_check=health_check,
        )

        return typing.cast(None, jsii.invoke(self, "putPublicEndpoint", [value]))

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(self, *, create: typing.Optional[builtins.str] = None) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service_deployment_version#create LightsailContainerServiceDeploymentVersion#create}.
        '''
        value = LightsailContainerServiceDeploymentVersionTimeouts(create=create)

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetPublicEndpoint")
    def reset_public_endpoint(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPublicEndpoint", []))

    @jsii.member(jsii_name="resetTimeouts")
    def reset_timeouts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeouts", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="container")
    def container(self) -> "LightsailContainerServiceDeploymentVersionContainerList":
        return typing.cast("LightsailContainerServiceDeploymentVersionContainerList", jsii.get(self, "container"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdAt"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publicEndpoint")
    def public_endpoint(
        self,
    ) -> "LightsailContainerServiceDeploymentVersionPublicEndpointOutputReference":
        return typing.cast("LightsailContainerServiceDeploymentVersionPublicEndpointOutputReference", jsii.get(self, "publicEndpoint"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeouts")
    def timeouts(
        self,
    ) -> "LightsailContainerServiceDeploymentVersionTimeoutsOutputReference":
        return typing.cast("LightsailContainerServiceDeploymentVersionTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="version")
    def version(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "version"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="containerInput")
    def container_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["LightsailContainerServiceDeploymentVersionContainer"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["LightsailContainerServiceDeploymentVersionContainer"]]], jsii.get(self, "containerInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publicEndpointInput")
    def public_endpoint_input(
        self,
    ) -> typing.Optional["LightsailContainerServiceDeploymentVersionPublicEndpoint"]:
        return typing.cast(typing.Optional["LightsailContainerServiceDeploymentVersionPublicEndpoint"], jsii.get(self, "publicEndpointInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceNameInput")
    def service_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serviceNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(
        self,
    ) -> typing.Optional[typing.Union["LightsailContainerServiceDeploymentVersionTimeouts", cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union["LightsailContainerServiceDeploymentVersionTimeouts", cdktf.IResolvable]], jsii.get(self, "timeoutsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serviceName")
    def service_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serviceName"))

    @service_name.setter
    def service_name(self, value: builtins.str) -> None:
        jsii.set(self, "serviceName", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lightsail.LightsailContainerServiceDeploymentVersionConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "container": "container",
        "service_name": "serviceName",
        "id": "id",
        "public_endpoint": "publicEndpoint",
        "timeouts": "timeouts",
    },
)
class LightsailContainerServiceDeploymentVersionConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        container: typing.Union[cdktf.IResolvable, typing.Sequence["LightsailContainerServiceDeploymentVersionContainer"]],
        service_name: builtins.str,
        id: typing.Optional[builtins.str] = None,
        public_endpoint: typing.Optional["LightsailContainerServiceDeploymentVersionPublicEndpoint"] = None,
        timeouts: typing.Optional["LightsailContainerServiceDeploymentVersionTimeouts"] = None,
    ) -> None:
        '''AWS Lightsail.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param container: container block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service_deployment_version#container LightsailContainerServiceDeploymentVersion#container}
        :param service_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service_deployment_version#service_name LightsailContainerServiceDeploymentVersion#service_name}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service_deployment_version#id LightsailContainerServiceDeploymentVersion#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param public_endpoint: public_endpoint block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service_deployment_version#public_endpoint LightsailContainerServiceDeploymentVersion#public_endpoint}
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service_deployment_version#timeouts LightsailContainerServiceDeploymentVersion#timeouts}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(public_endpoint, dict):
            public_endpoint = LightsailContainerServiceDeploymentVersionPublicEndpoint(**public_endpoint)
        if isinstance(timeouts, dict):
            timeouts = LightsailContainerServiceDeploymentVersionTimeouts(**timeouts)
        self._values: typing.Dict[str, typing.Any] = {
            "container": container,
            "service_name": service_name,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if id is not None:
            self._values["id"] = id
        if public_endpoint is not None:
            self._values["public_endpoint"] = public_endpoint
        if timeouts is not None:
            self._values["timeouts"] = timeouts

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def container(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.List["LightsailContainerServiceDeploymentVersionContainer"]]:
        '''container block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service_deployment_version#container LightsailContainerServiceDeploymentVersion#container}
        '''
        result = self._values.get("container")
        assert result is not None, "Required property 'container' is missing"
        return typing.cast(typing.Union[cdktf.IResolvable, typing.List["LightsailContainerServiceDeploymentVersionContainer"]], result)

    @builtins.property
    def service_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service_deployment_version#service_name LightsailContainerServiceDeploymentVersion#service_name}.'''
        result = self._values.get("service_name")
        assert result is not None, "Required property 'service_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service_deployment_version#id LightsailContainerServiceDeploymentVersion#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def public_endpoint(
        self,
    ) -> typing.Optional["LightsailContainerServiceDeploymentVersionPublicEndpoint"]:
        '''public_endpoint block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service_deployment_version#public_endpoint LightsailContainerServiceDeploymentVersion#public_endpoint}
        '''
        result = self._values.get("public_endpoint")
        return typing.cast(typing.Optional["LightsailContainerServiceDeploymentVersionPublicEndpoint"], result)

    @builtins.property
    def timeouts(
        self,
    ) -> typing.Optional["LightsailContainerServiceDeploymentVersionTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service_deployment_version#timeouts LightsailContainerServiceDeploymentVersion#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["LightsailContainerServiceDeploymentVersionTimeouts"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LightsailContainerServiceDeploymentVersionConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lightsail.LightsailContainerServiceDeploymentVersionContainer",
    jsii_struct_bases=[],
    name_mapping={
        "container_name": "containerName",
        "image": "image",
        "command": "command",
        "environment": "environment",
        "ports": "ports",
    },
)
class LightsailContainerServiceDeploymentVersionContainer:
    def __init__(
        self,
        *,
        container_name: builtins.str,
        image: builtins.str,
        command: typing.Optional[typing.Sequence[builtins.str]] = None,
        environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        ports: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''
        :param container_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service_deployment_version#container_name LightsailContainerServiceDeploymentVersion#container_name}.
        :param image: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service_deployment_version#image LightsailContainerServiceDeploymentVersion#image}.
        :param command: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service_deployment_version#command LightsailContainerServiceDeploymentVersion#command}.
        :param environment: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service_deployment_version#environment LightsailContainerServiceDeploymentVersion#environment}.
        :param ports: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service_deployment_version#ports LightsailContainerServiceDeploymentVersion#ports}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "container_name": container_name,
            "image": image,
        }
        if command is not None:
            self._values["command"] = command
        if environment is not None:
            self._values["environment"] = environment
        if ports is not None:
            self._values["ports"] = ports

    @builtins.property
    def container_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service_deployment_version#container_name LightsailContainerServiceDeploymentVersion#container_name}.'''
        result = self._values.get("container_name")
        assert result is not None, "Required property 'container_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def image(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service_deployment_version#image LightsailContainerServiceDeploymentVersion#image}.'''
        result = self._values.get("image")
        assert result is not None, "Required property 'image' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def command(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service_deployment_version#command LightsailContainerServiceDeploymentVersion#command}.'''
        result = self._values.get("command")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def environment(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service_deployment_version#environment LightsailContainerServiceDeploymentVersion#environment}.'''
        result = self._values.get("environment")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def ports(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service_deployment_version#ports LightsailContainerServiceDeploymentVersion#ports}.'''
        result = self._values.get("ports")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LightsailContainerServiceDeploymentVersionContainer(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LightsailContainerServiceDeploymentVersionContainerList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lightsail.LightsailContainerServiceDeploymentVersionContainerList",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
        wraps_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param wraps_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "LightsailContainerServiceDeploymentVersionContainerOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("LightsailContainerServiceDeploymentVersionContainerOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        jsii.set(self, "terraformAttribute", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformResource")
    def _terraform_resource(self) -> cdktf.IInterpolatingParent:
        '''The parent resource.'''
        return typing.cast(cdktf.IInterpolatingParent, jsii.get(self, "terraformResource"))

    @_terraform_resource.setter
    def _terraform_resource(self, value: cdktf.IInterpolatingParent) -> None:
        jsii.set(self, "terraformResource", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="wrapsSet")
    def _wraps_set(self) -> builtins.bool:
        '''whether the list is wrapping a set (will add tolist() to be able to access an item via an index).'''
        return typing.cast(builtins.bool, jsii.get(self, "wrapsSet"))

    @_wraps_set.setter
    def _wraps_set(self, value: builtins.bool) -> None:
        jsii.set(self, "wrapsSet", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[LightsailContainerServiceDeploymentVersionContainer]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[LightsailContainerServiceDeploymentVersionContainer]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[LightsailContainerServiceDeploymentVersionContainer]]],
    ) -> None:
        jsii.set(self, "internalValue", value)


class LightsailContainerServiceDeploymentVersionContainerOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lightsail.LightsailContainerServiceDeploymentVersionContainerOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_index: jsii.Number,
        complex_object_is_from_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_index: the index of this item in the list.
        :param complex_object_is_from_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetCommand")
    def reset_command(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCommand", []))

    @jsii.member(jsii_name="resetEnvironment")
    def reset_environment(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnvironment", []))

    @jsii.member(jsii_name="resetPorts")
    def reset_ports(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPorts", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="commandInput")
    def command_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "commandInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="containerNameInput")
    def container_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "containerNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="environmentInput")
    def environment_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "environmentInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="imageInput")
    def image_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "imageInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="portsInput")
    def ports_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "portsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="command")
    def command(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "command"))

    @command.setter
    def command(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "command", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="containerName")
    def container_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "containerName"))

    @container_name.setter
    def container_name(self, value: builtins.str) -> None:
        jsii.set(self, "containerName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="environment")
    def environment(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "environment"))

    @environment.setter
    def environment(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        jsii.set(self, "environment", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="image")
    def image(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "image"))

    @image.setter
    def image(self, value: builtins.str) -> None:
        jsii.set(self, "image", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ports")
    def ports(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "ports"))

    @ports.setter
    def ports(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        jsii.set(self, "ports", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[LightsailContainerServiceDeploymentVersionContainer, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[LightsailContainerServiceDeploymentVersionContainer, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[LightsailContainerServiceDeploymentVersionContainer, cdktf.IResolvable]],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lightsail.LightsailContainerServiceDeploymentVersionPublicEndpoint",
    jsii_struct_bases=[],
    name_mapping={
        "container_name": "containerName",
        "container_port": "containerPort",
        "health_check": "healthCheck",
    },
)
class LightsailContainerServiceDeploymentVersionPublicEndpoint:
    def __init__(
        self,
        *,
        container_name: builtins.str,
        container_port: jsii.Number,
        health_check: "LightsailContainerServiceDeploymentVersionPublicEndpointHealthCheck",
    ) -> None:
        '''
        :param container_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service_deployment_version#container_name LightsailContainerServiceDeploymentVersion#container_name}.
        :param container_port: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service_deployment_version#container_port LightsailContainerServiceDeploymentVersion#container_port}.
        :param health_check: health_check block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service_deployment_version#health_check LightsailContainerServiceDeploymentVersion#health_check}
        '''
        if isinstance(health_check, dict):
            health_check = LightsailContainerServiceDeploymentVersionPublicEndpointHealthCheck(**health_check)
        self._values: typing.Dict[str, typing.Any] = {
            "container_name": container_name,
            "container_port": container_port,
            "health_check": health_check,
        }

    @builtins.property
    def container_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service_deployment_version#container_name LightsailContainerServiceDeploymentVersion#container_name}.'''
        result = self._values.get("container_name")
        assert result is not None, "Required property 'container_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def container_port(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service_deployment_version#container_port LightsailContainerServiceDeploymentVersion#container_port}.'''
        result = self._values.get("container_port")
        assert result is not None, "Required property 'container_port' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def health_check(
        self,
    ) -> "LightsailContainerServiceDeploymentVersionPublicEndpointHealthCheck":
        '''health_check block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service_deployment_version#health_check LightsailContainerServiceDeploymentVersion#health_check}
        '''
        result = self._values.get("health_check")
        assert result is not None, "Required property 'health_check' is missing"
        return typing.cast("LightsailContainerServiceDeploymentVersionPublicEndpointHealthCheck", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LightsailContainerServiceDeploymentVersionPublicEndpoint(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lightsail.LightsailContainerServiceDeploymentVersionPublicEndpointHealthCheck",
    jsii_struct_bases=[],
    name_mapping={
        "healthy_threshold": "healthyThreshold",
        "interval_seconds": "intervalSeconds",
        "path": "path",
        "success_codes": "successCodes",
        "timeout_seconds": "timeoutSeconds",
        "unhealthy_threshold": "unhealthyThreshold",
    },
)
class LightsailContainerServiceDeploymentVersionPublicEndpointHealthCheck:
    def __init__(
        self,
        *,
        healthy_threshold: typing.Optional[jsii.Number] = None,
        interval_seconds: typing.Optional[jsii.Number] = None,
        path: typing.Optional[builtins.str] = None,
        success_codes: typing.Optional[builtins.str] = None,
        timeout_seconds: typing.Optional[jsii.Number] = None,
        unhealthy_threshold: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param healthy_threshold: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service_deployment_version#healthy_threshold LightsailContainerServiceDeploymentVersion#healthy_threshold}.
        :param interval_seconds: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service_deployment_version#interval_seconds LightsailContainerServiceDeploymentVersion#interval_seconds}.
        :param path: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service_deployment_version#path LightsailContainerServiceDeploymentVersion#path}.
        :param success_codes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service_deployment_version#success_codes LightsailContainerServiceDeploymentVersion#success_codes}.
        :param timeout_seconds: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service_deployment_version#timeout_seconds LightsailContainerServiceDeploymentVersion#timeout_seconds}.
        :param unhealthy_threshold: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service_deployment_version#unhealthy_threshold LightsailContainerServiceDeploymentVersion#unhealthy_threshold}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if healthy_threshold is not None:
            self._values["healthy_threshold"] = healthy_threshold
        if interval_seconds is not None:
            self._values["interval_seconds"] = interval_seconds
        if path is not None:
            self._values["path"] = path
        if success_codes is not None:
            self._values["success_codes"] = success_codes
        if timeout_seconds is not None:
            self._values["timeout_seconds"] = timeout_seconds
        if unhealthy_threshold is not None:
            self._values["unhealthy_threshold"] = unhealthy_threshold

    @builtins.property
    def healthy_threshold(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service_deployment_version#healthy_threshold LightsailContainerServiceDeploymentVersion#healthy_threshold}.'''
        result = self._values.get("healthy_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def interval_seconds(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service_deployment_version#interval_seconds LightsailContainerServiceDeploymentVersion#interval_seconds}.'''
        result = self._values.get("interval_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def path(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service_deployment_version#path LightsailContainerServiceDeploymentVersion#path}.'''
        result = self._values.get("path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def success_codes(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service_deployment_version#success_codes LightsailContainerServiceDeploymentVersion#success_codes}.'''
        result = self._values.get("success_codes")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def timeout_seconds(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service_deployment_version#timeout_seconds LightsailContainerServiceDeploymentVersion#timeout_seconds}.'''
        result = self._values.get("timeout_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def unhealthy_threshold(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service_deployment_version#unhealthy_threshold LightsailContainerServiceDeploymentVersion#unhealthy_threshold}.'''
        result = self._values.get("unhealthy_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LightsailContainerServiceDeploymentVersionPublicEndpointHealthCheck(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LightsailContainerServiceDeploymentVersionPublicEndpointHealthCheckOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lightsail.LightsailContainerServiceDeploymentVersionPublicEndpointHealthCheckOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetHealthyThreshold")
    def reset_healthy_threshold(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHealthyThreshold", []))

    @jsii.member(jsii_name="resetIntervalSeconds")
    def reset_interval_seconds(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIntervalSeconds", []))

    @jsii.member(jsii_name="resetPath")
    def reset_path(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPath", []))

    @jsii.member(jsii_name="resetSuccessCodes")
    def reset_success_codes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSuccessCodes", []))

    @jsii.member(jsii_name="resetTimeoutSeconds")
    def reset_timeout_seconds(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeoutSeconds", []))

    @jsii.member(jsii_name="resetUnhealthyThreshold")
    def reset_unhealthy_threshold(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUnhealthyThreshold", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="healthyThresholdInput")
    def healthy_threshold_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "healthyThresholdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="intervalSecondsInput")
    def interval_seconds_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "intervalSecondsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pathInput")
    def path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pathInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="successCodesInput")
    def success_codes_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "successCodesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeoutSecondsInput")
    def timeout_seconds_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "timeoutSecondsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="unhealthyThresholdInput")
    def unhealthy_threshold_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "unhealthyThresholdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="healthyThreshold")
    def healthy_threshold(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "healthyThreshold"))

    @healthy_threshold.setter
    def healthy_threshold(self, value: jsii.Number) -> None:
        jsii.set(self, "healthyThreshold", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="intervalSeconds")
    def interval_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "intervalSeconds"))

    @interval_seconds.setter
    def interval_seconds(self, value: jsii.Number) -> None:
        jsii.set(self, "intervalSeconds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="path")
    def path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "path"))

    @path.setter
    def path(self, value: builtins.str) -> None:
        jsii.set(self, "path", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="successCodes")
    def success_codes(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "successCodes"))

    @success_codes.setter
    def success_codes(self, value: builtins.str) -> None:
        jsii.set(self, "successCodes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="timeoutSeconds")
    def timeout_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "timeoutSeconds"))

    @timeout_seconds.setter
    def timeout_seconds(self, value: jsii.Number) -> None:
        jsii.set(self, "timeoutSeconds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="unhealthyThreshold")
    def unhealthy_threshold(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "unhealthyThreshold"))

    @unhealthy_threshold.setter
    def unhealthy_threshold(self, value: jsii.Number) -> None:
        jsii.set(self, "unhealthyThreshold", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[LightsailContainerServiceDeploymentVersionPublicEndpointHealthCheck]:
        return typing.cast(typing.Optional[LightsailContainerServiceDeploymentVersionPublicEndpointHealthCheck], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[LightsailContainerServiceDeploymentVersionPublicEndpointHealthCheck],
    ) -> None:
        jsii.set(self, "internalValue", value)


class LightsailContainerServiceDeploymentVersionPublicEndpointOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lightsail.LightsailContainerServiceDeploymentVersionPublicEndpointOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putHealthCheck")
    def put_health_check(
        self,
        *,
        healthy_threshold: typing.Optional[jsii.Number] = None,
        interval_seconds: typing.Optional[jsii.Number] = None,
        path: typing.Optional[builtins.str] = None,
        success_codes: typing.Optional[builtins.str] = None,
        timeout_seconds: typing.Optional[jsii.Number] = None,
        unhealthy_threshold: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param healthy_threshold: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service_deployment_version#healthy_threshold LightsailContainerServiceDeploymentVersion#healthy_threshold}.
        :param interval_seconds: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service_deployment_version#interval_seconds LightsailContainerServiceDeploymentVersion#interval_seconds}.
        :param path: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service_deployment_version#path LightsailContainerServiceDeploymentVersion#path}.
        :param success_codes: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service_deployment_version#success_codes LightsailContainerServiceDeploymentVersion#success_codes}.
        :param timeout_seconds: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service_deployment_version#timeout_seconds LightsailContainerServiceDeploymentVersion#timeout_seconds}.
        :param unhealthy_threshold: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service_deployment_version#unhealthy_threshold LightsailContainerServiceDeploymentVersion#unhealthy_threshold}.
        '''
        value = LightsailContainerServiceDeploymentVersionPublicEndpointHealthCheck(
            healthy_threshold=healthy_threshold,
            interval_seconds=interval_seconds,
            path=path,
            success_codes=success_codes,
            timeout_seconds=timeout_seconds,
            unhealthy_threshold=unhealthy_threshold,
        )

        return typing.cast(None, jsii.invoke(self, "putHealthCheck", [value]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="healthCheck")
    def health_check(
        self,
    ) -> LightsailContainerServiceDeploymentVersionPublicEndpointHealthCheckOutputReference:
        return typing.cast(LightsailContainerServiceDeploymentVersionPublicEndpointHealthCheckOutputReference, jsii.get(self, "healthCheck"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="containerNameInput")
    def container_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "containerNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="containerPortInput")
    def container_port_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "containerPortInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="healthCheckInput")
    def health_check_input(
        self,
    ) -> typing.Optional[LightsailContainerServiceDeploymentVersionPublicEndpointHealthCheck]:
        return typing.cast(typing.Optional[LightsailContainerServiceDeploymentVersionPublicEndpointHealthCheck], jsii.get(self, "healthCheckInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="containerName")
    def container_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "containerName"))

    @container_name.setter
    def container_name(self, value: builtins.str) -> None:
        jsii.set(self, "containerName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="containerPort")
    def container_port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "containerPort"))

    @container_port.setter
    def container_port(self, value: jsii.Number) -> None:
        jsii.set(self, "containerPort", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[LightsailContainerServiceDeploymentVersionPublicEndpoint]:
        return typing.cast(typing.Optional[LightsailContainerServiceDeploymentVersionPublicEndpoint], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[LightsailContainerServiceDeploymentVersionPublicEndpoint],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lightsail.LightsailContainerServiceDeploymentVersionTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create"},
)
class LightsailContainerServiceDeploymentVersionTimeouts:
    def __init__(self, *, create: typing.Optional[builtins.str] = None) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service_deployment_version#create LightsailContainerServiceDeploymentVersion#create}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if create is not None:
            self._values["create"] = create

    @builtins.property
    def create(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service_deployment_version#create LightsailContainerServiceDeploymentVersion#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LightsailContainerServiceDeploymentVersionTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LightsailContainerServiceDeploymentVersionTimeoutsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lightsail.LightsailContainerServiceDeploymentVersionTimeoutsOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCreate")
    def reset_create(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreate", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createInput")
    def create_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="create")
    def create(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "create"))

    @create.setter
    def create(self, value: builtins.str) -> None:
        jsii.set(self, "create", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[LightsailContainerServiceDeploymentVersionTimeouts, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[LightsailContainerServiceDeploymentVersionTimeouts, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[LightsailContainerServiceDeploymentVersionTimeouts, cdktf.IResolvable]],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lightsail.LightsailContainerServicePublicDomainNames",
    jsii_struct_bases=[],
    name_mapping={"certificate": "certificate"},
)
class LightsailContainerServicePublicDomainNames:
    def __init__(
        self,
        *,
        certificate: typing.Union[cdktf.IResolvable, typing.Sequence["LightsailContainerServicePublicDomainNamesCertificate"]],
    ) -> None:
        '''
        :param certificate: certificate block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service#certificate LightsailContainerService#certificate}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "certificate": certificate,
        }

    @builtins.property
    def certificate(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.List["LightsailContainerServicePublicDomainNamesCertificate"]]:
        '''certificate block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service#certificate LightsailContainerService#certificate}
        '''
        result = self._values.get("certificate")
        assert result is not None, "Required property 'certificate' is missing"
        return typing.cast(typing.Union[cdktf.IResolvable, typing.List["LightsailContainerServicePublicDomainNamesCertificate"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LightsailContainerServicePublicDomainNames(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lightsail.LightsailContainerServicePublicDomainNamesCertificate",
    jsii_struct_bases=[],
    name_mapping={
        "certificate_name": "certificateName",
        "domain_names": "domainNames",
    },
)
class LightsailContainerServicePublicDomainNamesCertificate:
    def __init__(
        self,
        *,
        certificate_name: builtins.str,
        domain_names: typing.Sequence[builtins.str],
    ) -> None:
        '''
        :param certificate_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service#certificate_name LightsailContainerService#certificate_name}.
        :param domain_names: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service#domain_names LightsailContainerService#domain_names}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "certificate_name": certificate_name,
            "domain_names": domain_names,
        }

    @builtins.property
    def certificate_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service#certificate_name LightsailContainerService#certificate_name}.'''
        result = self._values.get("certificate_name")
        assert result is not None, "Required property 'certificate_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def domain_names(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service#domain_names LightsailContainerService#domain_names}.'''
        result = self._values.get("domain_names")
        assert result is not None, "Required property 'domain_names' is missing"
        return typing.cast(typing.List[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LightsailContainerServicePublicDomainNamesCertificate(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LightsailContainerServicePublicDomainNamesCertificateList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lightsail.LightsailContainerServicePublicDomainNamesCertificateList",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
        wraps_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param wraps_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "LightsailContainerServicePublicDomainNamesCertificateOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("LightsailContainerServicePublicDomainNamesCertificateOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        jsii.set(self, "terraformAttribute", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformResource")
    def _terraform_resource(self) -> cdktf.IInterpolatingParent:
        '''The parent resource.'''
        return typing.cast(cdktf.IInterpolatingParent, jsii.get(self, "terraformResource"))

    @_terraform_resource.setter
    def _terraform_resource(self, value: cdktf.IInterpolatingParent) -> None:
        jsii.set(self, "terraformResource", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="wrapsSet")
    def _wraps_set(self) -> builtins.bool:
        '''whether the list is wrapping a set (will add tolist() to be able to access an item via an index).'''
        return typing.cast(builtins.bool, jsii.get(self, "wrapsSet"))

    @_wraps_set.setter
    def _wraps_set(self, value: builtins.bool) -> None:
        jsii.set(self, "wrapsSet", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[LightsailContainerServicePublicDomainNamesCertificate]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[LightsailContainerServicePublicDomainNamesCertificate]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[LightsailContainerServicePublicDomainNamesCertificate]]],
    ) -> None:
        jsii.set(self, "internalValue", value)


class LightsailContainerServicePublicDomainNamesCertificateOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lightsail.LightsailContainerServicePublicDomainNamesCertificateOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_index: jsii.Number,
        complex_object_is_from_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_index: the index of this item in the list.
        :param complex_object_is_from_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="certificateNameInput")
    def certificate_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "certificateNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainNamesInput")
    def domain_names_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "domainNamesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="certificateName")
    def certificate_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificateName"))

    @certificate_name.setter
    def certificate_name(self, value: builtins.str) -> None:
        jsii.set(self, "certificateName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainNames")
    def domain_names(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "domainNames"))

    @domain_names.setter
    def domain_names(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "domainNames", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[LightsailContainerServicePublicDomainNamesCertificate, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[LightsailContainerServicePublicDomainNamesCertificate, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[LightsailContainerServicePublicDomainNamesCertificate, cdktf.IResolvable]],
    ) -> None:
        jsii.set(self, "internalValue", value)


class LightsailContainerServicePublicDomainNamesOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lightsail.LightsailContainerServicePublicDomainNamesOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putCertificate")
    def put_certificate(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence[LightsailContainerServicePublicDomainNamesCertificate]],
    ) -> None:
        '''
        :param value: -
        '''
        return typing.cast(None, jsii.invoke(self, "putCertificate", [value]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="certificate")
    def certificate(self) -> LightsailContainerServicePublicDomainNamesCertificateList:
        return typing.cast(LightsailContainerServicePublicDomainNamesCertificateList, jsii.get(self, "certificate"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="certificateInput")
    def certificate_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[LightsailContainerServicePublicDomainNamesCertificate]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[LightsailContainerServicePublicDomainNamesCertificate]]], jsii.get(self, "certificateInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[LightsailContainerServicePublicDomainNames]:
        return typing.cast(typing.Optional[LightsailContainerServicePublicDomainNames], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[LightsailContainerServicePublicDomainNames],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lightsail.LightsailContainerServiceTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create", "delete": "delete", "update": "update"},
)
class LightsailContainerServiceTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service#create LightsailContainerService#create}.
        :param delete: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service#delete LightsailContainerService#delete}.
        :param update: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service#update LightsailContainerService#update}.
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if create is not None:
            self._values["create"] = create
        if delete is not None:
            self._values["delete"] = delete
        if update is not None:
            self._values["update"] = update

    @builtins.property
    def create(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service#create LightsailContainerService#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service#delete LightsailContainerService#delete}.'''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_container_service#update LightsailContainerService#update}.'''
        result = self._values.get("update")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LightsailContainerServiceTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LightsailContainerServiceTimeoutsOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lightsail.LightsailContainerServiceTimeoutsOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCreate")
    def reset_create(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreate", []))

    @jsii.member(jsii_name="resetDelete")
    def reset_delete(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDelete", []))

    @jsii.member(jsii_name="resetUpdate")
    def reset_update(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUpdate", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createInput")
    def create_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="deleteInput")
    def delete_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deleteInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="updateInput")
    def update_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "updateInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="create")
    def create(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "create"))

    @create.setter
    def create(self, value: builtins.str) -> None:
        jsii.set(self, "create", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="delete")
    def delete(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "delete"))

    @delete.setter
    def delete(self, value: builtins.str) -> None:
        jsii.set(self, "delete", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="update")
    def update(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "update"))

    @update.setter
    def update(self, value: builtins.str) -> None:
        jsii.set(self, "update", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[LightsailContainerServiceTimeouts, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[LightsailContainerServiceTimeouts, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[LightsailContainerServiceTimeouts, cdktf.IResolvable]],
    ) -> None:
        jsii.set(self, "internalValue", value)


class LightsailDomain(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lightsail.LightsailDomain",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/lightsail_domain aws_lightsail_domain}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        domain_name: builtins.str,
        id: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/lightsail_domain aws_lightsail_domain} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param domain_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_domain#domain_name LightsailDomain#domain_name}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_domain#id LightsailDomain#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = LightsailDomainConfig(
            domain_name=domain_name,
            id=id,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainNameInput")
    def domain_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "domainNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainName")
    def domain_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "domainName"))

    @domain_name.setter
    def domain_name(self, value: builtins.str) -> None:
        jsii.set(self, "domainName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        jsii.set(self, "id", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lightsail.LightsailDomainConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "domain_name": "domainName",
        "id": "id",
    },
)
class LightsailDomainConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        domain_name: builtins.str,
        id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Lightsail.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param domain_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_domain#domain_name LightsailDomain#domain_name}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_domain#id LightsailDomain#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "domain_name": domain_name,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if id is not None:
            self._values["id"] = id

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def domain_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_domain#domain_name LightsailDomain#domain_name}.'''
        result = self._values.get("domain_name")
        assert result is not None, "Required property 'domain_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_domain#id LightsailDomain#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LightsailDomainConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LightsailInstance(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lightsail.LightsailInstance",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/lightsail_instance aws_lightsail_instance}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        availability_zone: builtins.str,
        blueprint_id: builtins.str,
        bundle_id: builtins.str,
        name: builtins.str,
        id: typing.Optional[builtins.str] = None,
        key_pair_name: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        tags_all: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        user_data: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/lightsail_instance aws_lightsail_instance} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param availability_zone: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_instance#availability_zone LightsailInstance#availability_zone}.
        :param blueprint_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_instance#blueprint_id LightsailInstance#blueprint_id}.
        :param bundle_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_instance#bundle_id LightsailInstance#bundle_id}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_instance#name LightsailInstance#name}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_instance#id LightsailInstance#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param key_pair_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_instance#key_pair_name LightsailInstance#key_pair_name}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_instance#tags LightsailInstance#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_instance#tags_all LightsailInstance#tags_all}.
        :param user_data: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_instance#user_data LightsailInstance#user_data}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = LightsailInstanceConfig(
            availability_zone=availability_zone,
            blueprint_id=blueprint_id,
            bundle_id=bundle_id,
            name=name,
            id=id,
            key_pair_name=key_pair_name,
            tags=tags,
            tags_all=tags_all,
            user_data=user_data,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetKeyPairName")
    def reset_key_pair_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeyPairName", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="resetUserData")
    def reset_user_data(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUserData", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cpuCount")
    def cpu_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "cpuCount"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdAt"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ipv6Address")
    def ipv6_address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ipv6Address"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ipv6Addresses")
    def ipv6_addresses(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "ipv6Addresses"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="isStaticIp")
    def is_static_ip(self) -> cdktf.IResolvable:
        return typing.cast(cdktf.IResolvable, jsii.get(self, "isStaticIp"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="privateIpAddress")
    def private_ip_address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "privateIpAddress"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publicIpAddress")
    def public_ip_address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "publicIpAddress"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ramSize")
    def ram_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "ramSize"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="username")
    def username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "username"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="availabilityZoneInput")
    def availability_zone_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "availabilityZoneInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="blueprintIdInput")
    def blueprint_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "blueprintIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bundleIdInput")
    def bundle_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bundleIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keyPairNameInput")
    def key_pair_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyPairNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAllInput")
    def tags_all_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tagsAllInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsInput")
    def tags_input(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tagsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userDataInput")
    def user_data_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userDataInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="availabilityZone")
    def availability_zone(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "availabilityZone"))

    @availability_zone.setter
    def availability_zone(self, value: builtins.str) -> None:
        jsii.set(self, "availabilityZone", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="blueprintId")
    def blueprint_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "blueprintId"))

    @blueprint_id.setter
    def blueprint_id(self, value: builtins.str) -> None:
        jsii.set(self, "blueprintId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bundleId")
    def bundle_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bundleId"))

    @bundle_id.setter
    def bundle_id(self, value: builtins.str) -> None:
        jsii.set(self, "bundleId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keyPairName")
    def key_pair_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "keyPairName"))

    @key_pair_name.setter
    def key_pair_name(self, value: builtins.str) -> None:
        jsii.set(self, "keyPairName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        jsii.set(self, "tags", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tagsAll")
    def tags_all(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tagsAll"))

    @tags_all.setter
    def tags_all(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        jsii.set(self, "tagsAll", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userData")
    def user_data(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userData"))

    @user_data.setter
    def user_data(self, value: builtins.str) -> None:
        jsii.set(self, "userData", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lightsail.LightsailInstanceConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "availability_zone": "availabilityZone",
        "blueprint_id": "blueprintId",
        "bundle_id": "bundleId",
        "name": "name",
        "id": "id",
        "key_pair_name": "keyPairName",
        "tags": "tags",
        "tags_all": "tagsAll",
        "user_data": "userData",
    },
)
class LightsailInstanceConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        availability_zone: builtins.str,
        blueprint_id: builtins.str,
        bundle_id: builtins.str,
        name: builtins.str,
        id: typing.Optional[builtins.str] = None,
        key_pair_name: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        tags_all: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        user_data: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Lightsail.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param availability_zone: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_instance#availability_zone LightsailInstance#availability_zone}.
        :param blueprint_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_instance#blueprint_id LightsailInstance#blueprint_id}.
        :param bundle_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_instance#bundle_id LightsailInstance#bundle_id}.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_instance#name LightsailInstance#name}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_instance#id LightsailInstance#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param key_pair_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_instance#key_pair_name LightsailInstance#key_pair_name}.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_instance#tags LightsailInstance#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_instance#tags_all LightsailInstance#tags_all}.
        :param user_data: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_instance#user_data LightsailInstance#user_data}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "availability_zone": availability_zone,
            "blueprint_id": blueprint_id,
            "bundle_id": bundle_id,
            "name": name,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if id is not None:
            self._values["id"] = id
        if key_pair_name is not None:
            self._values["key_pair_name"] = key_pair_name
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all
        if user_data is not None:
            self._values["user_data"] = user_data

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def availability_zone(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_instance#availability_zone LightsailInstance#availability_zone}.'''
        result = self._values.get("availability_zone")
        assert result is not None, "Required property 'availability_zone' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def blueprint_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_instance#blueprint_id LightsailInstance#blueprint_id}.'''
        result = self._values.get("blueprint_id")
        assert result is not None, "Required property 'blueprint_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def bundle_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_instance#bundle_id LightsailInstance#bundle_id}.'''
        result = self._values.get("bundle_id")
        assert result is not None, "Required property 'bundle_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_instance#name LightsailInstance#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_instance#id LightsailInstance#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def key_pair_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_instance#key_pair_name LightsailInstance#key_pair_name}.'''
        result = self._values.get("key_pair_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_instance#tags LightsailInstance#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def tags_all(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_instance#tags_all LightsailInstance#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def user_data(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_instance#user_data LightsailInstance#user_data}.'''
        result = self._values.get("user_data")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LightsailInstanceConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LightsailInstancePublicPorts(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lightsail.LightsailInstancePublicPorts",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/lightsail_instance_public_ports aws_lightsail_instance_public_ports}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        instance_name: builtins.str,
        port_info: typing.Union[cdktf.IResolvable, typing.Sequence["LightsailInstancePublicPortsPortInfo"]],
        id: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/lightsail_instance_public_ports aws_lightsail_instance_public_ports} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param instance_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_instance_public_ports#instance_name LightsailInstancePublicPorts#instance_name}.
        :param port_info: port_info block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_instance_public_ports#port_info LightsailInstancePublicPorts#port_info}
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_instance_public_ports#id LightsailInstancePublicPorts#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = LightsailInstancePublicPortsConfig(
            instance_name=instance_name,
            port_info=port_info,
            id=id,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="putPortInfo")
    def put_port_info(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence["LightsailInstancePublicPortsPortInfo"]],
    ) -> None:
        '''
        :param value: -
        '''
        return typing.cast(None, jsii.invoke(self, "putPortInfo", [value]))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="portInfo")
    def port_info(self) -> "LightsailInstancePublicPortsPortInfoList":
        return typing.cast("LightsailInstancePublicPortsPortInfoList", jsii.get(self, "portInfo"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceNameInput")
    def instance_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "instanceNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="portInfoInput")
    def port_info_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["LightsailInstancePublicPortsPortInfo"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["LightsailInstancePublicPortsPortInfo"]]], jsii.get(self, "portInfoInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceName")
    def instance_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "instanceName"))

    @instance_name.setter
    def instance_name(self, value: builtins.str) -> None:
        jsii.set(self, "instanceName", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lightsail.LightsailInstancePublicPortsConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "instance_name": "instanceName",
        "port_info": "portInfo",
        "id": "id",
    },
)
class LightsailInstancePublicPortsConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        instance_name: builtins.str,
        port_info: typing.Union[cdktf.IResolvable, typing.Sequence["LightsailInstancePublicPortsPortInfo"]],
        id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Lightsail.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param instance_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_instance_public_ports#instance_name LightsailInstancePublicPorts#instance_name}.
        :param port_info: port_info block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_instance_public_ports#port_info LightsailInstancePublicPorts#port_info}
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_instance_public_ports#id LightsailInstancePublicPorts#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "instance_name": instance_name,
            "port_info": port_info,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if id is not None:
            self._values["id"] = id

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def instance_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_instance_public_ports#instance_name LightsailInstancePublicPorts#instance_name}.'''
        result = self._values.get("instance_name")
        assert result is not None, "Required property 'instance_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def port_info(
        self,
    ) -> typing.Union[cdktf.IResolvable, typing.List["LightsailInstancePublicPortsPortInfo"]]:
        '''port_info block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_instance_public_ports#port_info LightsailInstancePublicPorts#port_info}
        '''
        result = self._values.get("port_info")
        assert result is not None, "Required property 'port_info' is missing"
        return typing.cast(typing.Union[cdktf.IResolvable, typing.List["LightsailInstancePublicPortsPortInfo"]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_instance_public_ports#id LightsailInstancePublicPorts#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LightsailInstancePublicPortsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lightsail.LightsailInstancePublicPortsPortInfo",
    jsii_struct_bases=[],
    name_mapping={
        "from_port": "fromPort",
        "protocol": "protocol",
        "to_port": "toPort",
        "cidrs": "cidrs",
    },
)
class LightsailInstancePublicPortsPortInfo:
    def __init__(
        self,
        *,
        from_port: jsii.Number,
        protocol: builtins.str,
        to_port: jsii.Number,
        cidrs: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param from_port: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_instance_public_ports#from_port LightsailInstancePublicPorts#from_port}.
        :param protocol: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_instance_public_ports#protocol LightsailInstancePublicPorts#protocol}.
        :param to_port: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_instance_public_ports#to_port LightsailInstancePublicPorts#to_port}.
        :param cidrs: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_instance_public_ports#cidrs LightsailInstancePublicPorts#cidrs}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "from_port": from_port,
            "protocol": protocol,
            "to_port": to_port,
        }
        if cidrs is not None:
            self._values["cidrs"] = cidrs

    @builtins.property
    def from_port(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_instance_public_ports#from_port LightsailInstancePublicPorts#from_port}.'''
        result = self._values.get("from_port")
        assert result is not None, "Required property 'from_port' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def protocol(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_instance_public_ports#protocol LightsailInstancePublicPorts#protocol}.'''
        result = self._values.get("protocol")
        assert result is not None, "Required property 'protocol' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def to_port(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_instance_public_ports#to_port LightsailInstancePublicPorts#to_port}.'''
        result = self._values.get("to_port")
        assert result is not None, "Required property 'to_port' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def cidrs(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_instance_public_ports#cidrs LightsailInstancePublicPorts#cidrs}.'''
        result = self._values.get("cidrs")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LightsailInstancePublicPortsPortInfo(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LightsailInstancePublicPortsPortInfoList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lightsail.LightsailInstancePublicPortsPortInfoList",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
        wraps_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param wraps_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "LightsailInstancePublicPortsPortInfoOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("LightsailInstancePublicPortsPortInfoOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        jsii.set(self, "terraformAttribute", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformResource")
    def _terraform_resource(self) -> cdktf.IInterpolatingParent:
        '''The parent resource.'''
        return typing.cast(cdktf.IInterpolatingParent, jsii.get(self, "terraformResource"))

    @_terraform_resource.setter
    def _terraform_resource(self, value: cdktf.IInterpolatingParent) -> None:
        jsii.set(self, "terraformResource", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="wrapsSet")
    def _wraps_set(self) -> builtins.bool:
        '''whether the list is wrapping a set (will add tolist() to be able to access an item via an index).'''
        return typing.cast(builtins.bool, jsii.get(self, "wrapsSet"))

    @_wraps_set.setter
    def _wraps_set(self, value: builtins.bool) -> None:
        jsii.set(self, "wrapsSet", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[LightsailInstancePublicPortsPortInfo]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[LightsailInstancePublicPortsPortInfo]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[LightsailInstancePublicPortsPortInfo]]],
    ) -> None:
        jsii.set(self, "internalValue", value)


class LightsailInstancePublicPortsPortInfoOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lightsail.LightsailInstancePublicPortsPortInfoOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_index: jsii.Number,
        complex_object_is_from_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_index: the index of this item in the list.
        :param complex_object_is_from_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetCidrs")
    def reset_cidrs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCidrs", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cidrsInput")
    def cidrs_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "cidrsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fromPortInput")
    def from_port_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "fromPortInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="protocolInput")
    def protocol_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "protocolInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="toPortInput")
    def to_port_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "toPortInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cidrs")
    def cidrs(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "cidrs"))

    @cidrs.setter
    def cidrs(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "cidrs", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fromPort")
    def from_port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "fromPort"))

    @from_port.setter
    def from_port(self, value: jsii.Number) -> None:
        jsii.set(self, "fromPort", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="protocol")
    def protocol(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "protocol"))

    @protocol.setter
    def protocol(self, value: builtins.str) -> None:
        jsii.set(self, "protocol", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="toPort")
    def to_port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "toPort"))

    @to_port.setter
    def to_port(self, value: jsii.Number) -> None:
        jsii.set(self, "toPort", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[LightsailInstancePublicPortsPortInfo, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[LightsailInstancePublicPortsPortInfo, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[LightsailInstancePublicPortsPortInfo, cdktf.IResolvable]],
    ) -> None:
        jsii.set(self, "internalValue", value)


class LightsailKeyPair(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lightsail.LightsailKeyPair",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/lightsail_key_pair aws_lightsail_key_pair}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        id: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        name_prefix: typing.Optional[builtins.str] = None,
        pgp_key: typing.Optional[builtins.str] = None,
        public_key: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/lightsail_key_pair aws_lightsail_key_pair} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_key_pair#id LightsailKeyPair#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_key_pair#name LightsailKeyPair#name}.
        :param name_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_key_pair#name_prefix LightsailKeyPair#name_prefix}.
        :param pgp_key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_key_pair#pgp_key LightsailKeyPair#pgp_key}.
        :param public_key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_key_pair#public_key LightsailKeyPair#public_key}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = LightsailKeyPairConfig(
            id=id,
            name=name,
            name_prefix=name_prefix,
            pgp_key=pgp_key,
            public_key=public_key,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetNamePrefix")
    def reset_name_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNamePrefix", []))

    @jsii.member(jsii_name="resetPgpKey")
    def reset_pgp_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPgpKey", []))

    @jsii.member(jsii_name="resetPublicKey")
    def reset_public_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPublicKey", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encryptedFingerprint")
    def encrypted_fingerprint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "encryptedFingerprint"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="encryptedPrivateKey")
    def encrypted_private_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "encryptedPrivateKey"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="fingerprint")
    def fingerprint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fingerprint"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="privateKey")
    def private_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "privateKey"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="namePrefixInput")
    def name_prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "namePrefixInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pgpKeyInput")
    def pgp_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pgpKeyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publicKeyInput")
    def public_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "publicKeyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="namePrefix")
    def name_prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "namePrefix"))

    @name_prefix.setter
    def name_prefix(self, value: builtins.str) -> None:
        jsii.set(self, "namePrefix", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pgpKey")
    def pgp_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pgpKey"))

    @pgp_key.setter
    def pgp_key(self, value: builtins.str) -> None:
        jsii.set(self, "pgpKey", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publicKey")
    def public_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "publicKey"))

    @public_key.setter
    def public_key(self, value: builtins.str) -> None:
        jsii.set(self, "publicKey", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lightsail.LightsailKeyPairConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "id": "id",
        "name": "name",
        "name_prefix": "namePrefix",
        "pgp_key": "pgpKey",
        "public_key": "publicKey",
    },
)
class LightsailKeyPairConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        id: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        name_prefix: typing.Optional[builtins.str] = None,
        pgp_key: typing.Optional[builtins.str] = None,
        public_key: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Lightsail.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_key_pair#id LightsailKeyPair#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_key_pair#name LightsailKeyPair#name}.
        :param name_prefix: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_key_pair#name_prefix LightsailKeyPair#name_prefix}.
        :param pgp_key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_key_pair#pgp_key LightsailKeyPair#pgp_key}.
        :param public_key: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_key_pair#public_key LightsailKeyPair#public_key}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {}
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if id is not None:
            self._values["id"] = id
        if name is not None:
            self._values["name"] = name
        if name_prefix is not None:
            self._values["name_prefix"] = name_prefix
        if pgp_key is not None:
            self._values["pgp_key"] = pgp_key
        if public_key is not None:
            self._values["public_key"] = public_key

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_key_pair#id LightsailKeyPair#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_key_pair#name LightsailKeyPair#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name_prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_key_pair#name_prefix LightsailKeyPair#name_prefix}.'''
        result = self._values.get("name_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pgp_key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_key_pair#pgp_key LightsailKeyPair#pgp_key}.'''
        result = self._values.get("pgp_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def public_key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_key_pair#public_key LightsailKeyPair#public_key}.'''
        result = self._values.get("public_key")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LightsailKeyPairConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LightsailStaticIp(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lightsail.LightsailStaticIp",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/lightsail_static_ip aws_lightsail_static_ip}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        id: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/lightsail_static_ip aws_lightsail_static_ip} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_static_ip#name LightsailStaticIp#name}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_static_ip#id LightsailStaticIp#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = LightsailStaticIpConfig(
            name=name,
            id=id,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ipAddress")
    def ip_address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ipAddress"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="supportCode")
    def support_code(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "supportCode"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)


class LightsailStaticIpAttachment(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.lightsail.LightsailStaticIpAttachment",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/lightsail_static_ip_attachment aws_lightsail_static_ip_attachment}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        instance_name: builtins.str,
        static_ip_name: builtins.str,
        id: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/lightsail_static_ip_attachment aws_lightsail_static_ip_attachment} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param instance_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_static_ip_attachment#instance_name LightsailStaticIpAttachment#instance_name}.
        :param static_ip_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_static_ip_attachment#static_ip_name LightsailStaticIpAttachment#static_ip_name}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_static_ip_attachment#id LightsailStaticIpAttachment#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = LightsailStaticIpAttachmentConfig(
            instance_name=instance_name,
            static_ip_name=static_ip_name,
            id=id,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ipAddress")
    def ip_address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ipAddress"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceNameInput")
    def instance_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "instanceNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="staticIpNameInput")
    def static_ip_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "staticIpNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="instanceName")
    def instance_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "instanceName"))

    @instance_name.setter
    def instance_name(self, value: builtins.str) -> None:
        jsii.set(self, "instanceName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="staticIpName")
    def static_ip_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "staticIpName"))

    @static_ip_name.setter
    def static_ip_name(self, value: builtins.str) -> None:
        jsii.set(self, "staticIpName", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lightsail.LightsailStaticIpAttachmentConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "instance_name": "instanceName",
        "static_ip_name": "staticIpName",
        "id": "id",
    },
)
class LightsailStaticIpAttachmentConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        instance_name: builtins.str,
        static_ip_name: builtins.str,
        id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Lightsail.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param instance_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_static_ip_attachment#instance_name LightsailStaticIpAttachment#instance_name}.
        :param static_ip_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_static_ip_attachment#static_ip_name LightsailStaticIpAttachment#static_ip_name}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_static_ip_attachment#id LightsailStaticIpAttachment#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "instance_name": instance_name,
            "static_ip_name": static_ip_name,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if id is not None:
            self._values["id"] = id

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def instance_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_static_ip_attachment#instance_name LightsailStaticIpAttachment#instance_name}.'''
        result = self._values.get("instance_name")
        assert result is not None, "Required property 'instance_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def static_ip_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_static_ip_attachment#static_ip_name LightsailStaticIpAttachment#static_ip_name}.'''
        result = self._values.get("static_ip_name")
        assert result is not None, "Required property 'static_ip_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_static_ip_attachment#id LightsailStaticIpAttachment#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LightsailStaticIpAttachmentConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.lightsail.LightsailStaticIpConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "id": "id",
    },
)
class LightsailStaticIpConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''AWS Lightsail.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_static_ip#name LightsailStaticIp#name}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_static_ip#id LightsailStaticIp#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if id is not None:
            self._values["id"] = id

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_static_ip#name LightsailStaticIp#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/lightsail_static_ip#id LightsailStaticIp#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LightsailStaticIpConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "LightsailContainerService",
    "LightsailContainerServiceConfig",
    "LightsailContainerServiceDeploymentVersion",
    "LightsailContainerServiceDeploymentVersionConfig",
    "LightsailContainerServiceDeploymentVersionContainer",
    "LightsailContainerServiceDeploymentVersionContainerList",
    "LightsailContainerServiceDeploymentVersionContainerOutputReference",
    "LightsailContainerServiceDeploymentVersionPublicEndpoint",
    "LightsailContainerServiceDeploymentVersionPublicEndpointHealthCheck",
    "LightsailContainerServiceDeploymentVersionPublicEndpointHealthCheckOutputReference",
    "LightsailContainerServiceDeploymentVersionPublicEndpointOutputReference",
    "LightsailContainerServiceDeploymentVersionTimeouts",
    "LightsailContainerServiceDeploymentVersionTimeoutsOutputReference",
    "LightsailContainerServicePublicDomainNames",
    "LightsailContainerServicePublicDomainNamesCertificate",
    "LightsailContainerServicePublicDomainNamesCertificateList",
    "LightsailContainerServicePublicDomainNamesCertificateOutputReference",
    "LightsailContainerServicePublicDomainNamesOutputReference",
    "LightsailContainerServiceTimeouts",
    "LightsailContainerServiceTimeoutsOutputReference",
    "LightsailDomain",
    "LightsailDomainConfig",
    "LightsailInstance",
    "LightsailInstanceConfig",
    "LightsailInstancePublicPorts",
    "LightsailInstancePublicPortsConfig",
    "LightsailInstancePublicPortsPortInfo",
    "LightsailInstancePublicPortsPortInfoList",
    "LightsailInstancePublicPortsPortInfoOutputReference",
    "LightsailKeyPair",
    "LightsailKeyPairConfig",
    "LightsailStaticIp",
    "LightsailStaticIpAttachment",
    "LightsailStaticIpAttachmentConfig",
    "LightsailStaticIpConfig",
]

publication.publish()
