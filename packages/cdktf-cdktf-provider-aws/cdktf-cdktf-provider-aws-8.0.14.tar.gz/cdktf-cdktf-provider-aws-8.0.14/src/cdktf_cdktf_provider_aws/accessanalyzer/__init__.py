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


class AccessanalyzerAnalyzer(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.accessanalyzer.AccessanalyzerAnalyzer",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/accessanalyzer_analyzer aws_accessanalyzer_analyzer}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        analyzer_name: builtins.str,
        id: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        tags_all: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        type: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/accessanalyzer_analyzer aws_accessanalyzer_analyzer} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param analyzer_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/accessanalyzer_analyzer#analyzer_name AccessanalyzerAnalyzer#analyzer_name}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/accessanalyzer_analyzer#id AccessanalyzerAnalyzer#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/accessanalyzer_analyzer#tags AccessanalyzerAnalyzer#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/accessanalyzer_analyzer#tags_all AccessanalyzerAnalyzer#tags_all}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/accessanalyzer_analyzer#type AccessanalyzerAnalyzer#type}.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = AccessanalyzerAnalyzerConfig(
            analyzer_name=analyzer_name,
            id=id,
            tags=tags,
            tags_all=tags_all,
            type=type,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTagsAll")
    def reset_tags_all(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagsAll", []))

    @jsii.member(jsii_name="resetType")
    def reset_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetType", []))

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
    @jsii.member(jsii_name="analyzerNameInput")
    def analyzer_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "analyzerNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

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
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="analyzerName")
    def analyzer_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "analyzerName"))

    @analyzer_name.setter
    def analyzer_name(self, value: builtins.str) -> None:
        jsii.set(self, "analyzerName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        jsii.set(self, "id", value)

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
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        jsii.set(self, "type", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.accessanalyzer.AccessanalyzerAnalyzerConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "analyzer_name": "analyzerName",
        "id": "id",
        "tags": "tags",
        "tags_all": "tagsAll",
        "type": "type",
    },
)
class AccessanalyzerAnalyzerConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        analyzer_name: builtins.str,
        id: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        tags_all: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Access Analyzer Analyzer.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param analyzer_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/accessanalyzer_analyzer#analyzer_name AccessanalyzerAnalyzer#analyzer_name}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/accessanalyzer_analyzer#id AccessanalyzerAnalyzer#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param tags: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/accessanalyzer_analyzer#tags AccessanalyzerAnalyzer#tags}.
        :param tags_all: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/accessanalyzer_analyzer#tags_all AccessanalyzerAnalyzer#tags_all}.
        :param type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/accessanalyzer_analyzer#type AccessanalyzerAnalyzer#type}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "analyzer_name": analyzer_name,
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
        if tags is not None:
            self._values["tags"] = tags
        if tags_all is not None:
            self._values["tags_all"] = tags_all
        if type is not None:
            self._values["type"] = type

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
    def analyzer_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/accessanalyzer_analyzer#analyzer_name AccessanalyzerAnalyzer#analyzer_name}.'''
        result = self._values.get("analyzer_name")
        assert result is not None, "Required property 'analyzer_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/accessanalyzer_analyzer#id AccessanalyzerAnalyzer#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/accessanalyzer_analyzer#tags AccessanalyzerAnalyzer#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def tags_all(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/accessanalyzer_analyzer#tags_all AccessanalyzerAnalyzer#tags_all}.'''
        result = self._values.get("tags_all")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/accessanalyzer_analyzer#type AccessanalyzerAnalyzer#type}.'''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AccessanalyzerAnalyzerConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AccessanalyzerArchiveRule(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.accessanalyzer.AccessanalyzerArchiveRule",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/aws/r/accessanalyzer_archive_rule aws_accessanalyzer_archive_rule}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        analyzer_name: builtins.str,
        filter: typing.Union[typing.Sequence["AccessanalyzerArchiveRuleFilter"], cdktf.IResolvable],
        rule_name: builtins.str,
        id: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/aws/r/accessanalyzer_archive_rule aws_accessanalyzer_archive_rule} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param analyzer_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/accessanalyzer_archive_rule#analyzer_name AccessanalyzerArchiveRule#analyzer_name}.
        :param filter: filter block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/accessanalyzer_archive_rule#filter AccessanalyzerArchiveRule#filter}
        :param rule_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/accessanalyzer_archive_rule#rule_name AccessanalyzerArchiveRule#rule_name}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/accessanalyzer_archive_rule#id AccessanalyzerArchiveRule#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = AccessanalyzerArchiveRuleConfig(
            analyzer_name=analyzer_name,
            filter=filter,
            rule_name=rule_name,
            id=id,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="putFilter")
    def put_filter(
        self,
        value: typing.Union[typing.Sequence["AccessanalyzerArchiveRuleFilter"], cdktf.IResolvable],
    ) -> None:
        '''
        :param value: -
        '''
        return typing.cast(None, jsii.invoke(self, "putFilter", [value]))

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
    @jsii.member(jsii_name="filter")
    def filter(self) -> "AccessanalyzerArchiveRuleFilterList":
        return typing.cast("AccessanalyzerArchiveRuleFilterList", jsii.get(self, "filter"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="analyzerNameInput")
    def analyzer_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "analyzerNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="filterInput")
    def filter_input(
        self,
    ) -> typing.Optional[typing.Union[typing.List["AccessanalyzerArchiveRuleFilter"], cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[typing.List["AccessanalyzerArchiveRuleFilter"], cdktf.IResolvable]], jsii.get(self, "filterInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ruleNameInput")
    def rule_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ruleNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="analyzerName")
    def analyzer_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "analyzerName"))

    @analyzer_name.setter
    def analyzer_name(self, value: builtins.str) -> None:
        jsii.set(self, "analyzerName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        jsii.set(self, "id", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ruleName")
    def rule_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ruleName"))

    @rule_name.setter
    def rule_name(self, value: builtins.str) -> None:
        jsii.set(self, "ruleName", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.accessanalyzer.AccessanalyzerArchiveRuleConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "analyzer_name": "analyzerName",
        "filter": "filter",
        "rule_name": "ruleName",
        "id": "id",
    },
)
class AccessanalyzerArchiveRuleConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        analyzer_name: builtins.str,
        filter: typing.Union[typing.Sequence["AccessanalyzerArchiveRuleFilter"], cdktf.IResolvable],
        rule_name: builtins.str,
        id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Access Analyzer Analyzer.

        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param analyzer_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/accessanalyzer_archive_rule#analyzer_name AccessanalyzerArchiveRule#analyzer_name}.
        :param filter: filter block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/accessanalyzer_archive_rule#filter AccessanalyzerArchiveRule#filter}
        :param rule_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/accessanalyzer_archive_rule#rule_name AccessanalyzerArchiveRule#rule_name}.
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/accessanalyzer_archive_rule#id AccessanalyzerArchiveRule#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "analyzer_name": analyzer_name,
            "filter": filter,
            "rule_name": rule_name,
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
    def analyzer_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/accessanalyzer_archive_rule#analyzer_name AccessanalyzerArchiveRule#analyzer_name}.'''
        result = self._values.get("analyzer_name")
        assert result is not None, "Required property 'analyzer_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def filter(
        self,
    ) -> typing.Union[typing.List["AccessanalyzerArchiveRuleFilter"], cdktf.IResolvable]:
        '''filter block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/accessanalyzer_archive_rule#filter AccessanalyzerArchiveRule#filter}
        '''
        result = self._values.get("filter")
        assert result is not None, "Required property 'filter' is missing"
        return typing.cast(typing.Union[typing.List["AccessanalyzerArchiveRuleFilter"], cdktf.IResolvable], result)

    @builtins.property
    def rule_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/accessanalyzer_archive_rule#rule_name AccessanalyzerArchiveRule#rule_name}.'''
        result = self._values.get("rule_name")
        assert result is not None, "Required property 'rule_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/accessanalyzer_archive_rule#id AccessanalyzerArchiveRule#id}.

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
        return "AccessanalyzerArchiveRuleConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-aws.accessanalyzer.AccessanalyzerArchiveRuleFilter",
    jsii_struct_bases=[],
    name_mapping={
        "criteria": "criteria",
        "contains": "contains",
        "eq": "eq",
        "exists": "exists",
        "neq": "neq",
    },
)
class AccessanalyzerArchiveRuleFilter:
    def __init__(
        self,
        *,
        criteria: builtins.str,
        contains: typing.Optional[typing.Sequence[builtins.str]] = None,
        eq: typing.Optional[typing.Sequence[builtins.str]] = None,
        exists: typing.Optional[builtins.str] = None,
        neq: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param criteria: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/accessanalyzer_archive_rule#criteria AccessanalyzerArchiveRule#criteria}.
        :param contains: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/accessanalyzer_archive_rule#contains AccessanalyzerArchiveRule#contains}.
        :param eq: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/accessanalyzer_archive_rule#eq AccessanalyzerArchiveRule#eq}.
        :param exists: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/accessanalyzer_archive_rule#exists AccessanalyzerArchiveRule#exists}.
        :param neq: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/accessanalyzer_archive_rule#neq AccessanalyzerArchiveRule#neq}.
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "criteria": criteria,
        }
        if contains is not None:
            self._values["contains"] = contains
        if eq is not None:
            self._values["eq"] = eq
        if exists is not None:
            self._values["exists"] = exists
        if neq is not None:
            self._values["neq"] = neq

    @builtins.property
    def criteria(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/accessanalyzer_archive_rule#criteria AccessanalyzerArchiveRule#criteria}.'''
        result = self._values.get("criteria")
        assert result is not None, "Required property 'criteria' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def contains(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/accessanalyzer_archive_rule#contains AccessanalyzerArchiveRule#contains}.'''
        result = self._values.get("contains")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def eq(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/accessanalyzer_archive_rule#eq AccessanalyzerArchiveRule#eq}.'''
        result = self._values.get("eq")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def exists(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/accessanalyzer_archive_rule#exists AccessanalyzerArchiveRule#exists}.'''
        result = self._values.get("exists")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def neq(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/aws/r/accessanalyzer_archive_rule#neq AccessanalyzerArchiveRule#neq}.'''
        result = self._values.get("neq")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AccessanalyzerArchiveRuleFilter(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AccessanalyzerArchiveRuleFilterList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.accessanalyzer.AccessanalyzerArchiveRuleFilterList",
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
    ) -> "AccessanalyzerArchiveRuleFilterOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("AccessanalyzerArchiveRuleFilterOutputReference", jsii.invoke(self, "get", [index]))

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
    ) -> typing.Optional[typing.Union[typing.List[AccessanalyzerArchiveRuleFilter], cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[typing.List[AccessanalyzerArchiveRuleFilter], cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[typing.List[AccessanalyzerArchiveRuleFilter], cdktf.IResolvable]],
    ) -> None:
        jsii.set(self, "internalValue", value)


class AccessanalyzerArchiveRuleFilterOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-aws.accessanalyzer.AccessanalyzerArchiveRuleFilterOutputReference",
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

    @jsii.member(jsii_name="resetContains")
    def reset_contains(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetContains", []))

    @jsii.member(jsii_name="resetEq")
    def reset_eq(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEq", []))

    @jsii.member(jsii_name="resetExists")
    def reset_exists(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExists", []))

    @jsii.member(jsii_name="resetNeq")
    def reset_neq(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNeq", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="containsInput")
    def contains_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "containsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="criteriaInput")
    def criteria_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "criteriaInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="eqInput")
    def eq_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "eqInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="existsInput")
    def exists_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "existsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="neqInput")
    def neq_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "neqInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="contains")
    def contains(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "contains"))

    @contains.setter
    def contains(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "contains", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="criteria")
    def criteria(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "criteria"))

    @criteria.setter
    def criteria(self, value: builtins.str) -> None:
        jsii.set(self, "criteria", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="eq")
    def eq(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "eq"))

    @eq.setter
    def eq(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "eq", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="exists")
    def exists(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "exists"))

    @exists.setter
    def exists(self, value: builtins.str) -> None:
        jsii.set(self, "exists", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="neq")
    def neq(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "neq"))

    @neq.setter
    def neq(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "neq", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[AccessanalyzerArchiveRuleFilter, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[AccessanalyzerArchiveRuleFilter, cdktf.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[AccessanalyzerArchiveRuleFilter, cdktf.IResolvable]],
    ) -> None:
        jsii.set(self, "internalValue", value)


__all__ = [
    "AccessanalyzerAnalyzer",
    "AccessanalyzerAnalyzerConfig",
    "AccessanalyzerArchiveRule",
    "AccessanalyzerArchiveRuleConfig",
    "AccessanalyzerArchiveRuleFilter",
    "AccessanalyzerArchiveRuleFilterList",
    "AccessanalyzerArchiveRuleFilterOutputReference",
]

publication.publish()
