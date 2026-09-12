"""CDKのコスト・認可・保存制御を合成テンプレートで検証する。"""

import json

import pytest
from aws_cdk import App, Aspects
from aws_cdk.assertions import Annotations, Match, Template
from cdk_nag import AwsSolutionsChecks
from kotorelay_infra.stack import KotoRelayStack


@pytest.fixture(scope="module")
def stack(tmp_path_factory):
    folder = tmp_path_factory.mktemp("lambda")
    (folder / "backend").mkdir()
    (folder / "backend/Dockerfile.lambda").write_text("FROM scratch\n")
    (folder / "handler.py").write_text('"""アセット構造の試験用fixture。"""\n')
    app = App(outdir=str(tmp_path_factory.mktemp("synth")))
    result = KotoRelayStack(app, "KotoRelay", asset_path=str(folder))
    Aspects.of(app).add(AwsSolutionsChecks(verbose=True))
    app.synth()
    return result


def test_常設計算資源と固定費要因を作成しない(stack):
    template = Template.from_stack(stack)
    for resource in [
        "AWS::EC2::Instance",
        "AWS::EC2::NatGateway",
        "AWS::ElasticLoadBalancingV2::LoadBalancer",
        "AWS::ECS::Service",
        "AWS::OpenSearchServerless::Collection",
        "AWS::KMS::Key",
    ]:
        template.resource_count_is(resource, 0)
    template.has_resource_properties("AWS::Lambda::Function", {"ReservedConcurrentExecutions": 3})
    assert "ProvisionedConcurrencyConfig" not in json.dumps(template.to_json())


def test_DSQLの削除保護と非公開S3を構成する(stack):
    template = Template.from_stack(stack)
    template.has_resource_properties("AWS::DSQL::Cluster", {"DeletionProtectionEnabled": True})
    template.resource_count_is("AWS::S3::Bucket", 2)
    for resource in template.find_resources("AWS::S3::Bucket").values():
        assert all(resource["Properties"]["PublicAccessBlockConfiguration"].values())
        assert resource["DeletionPolicy"] == "Retain"
    template.has_resource_properties(
        "AWS::S3Vectors::Index", {"Dimension": 256, "DistanceMetric": "cosine"}
    )


def test_JWT認証と保護コンテンツのキャッシュ無効化(stack):
    template = Template.from_stack(stack)
    template.has_resource_properties("AWS::ApiGatewayV2::Authorizer", {"AuthorizerType": "JWT"})
    template.has_resource_properties("AWS::ApiGatewayV2::Route", {"AuthorizationType": "JWT"})
    template.has_resource_properties(
        "AWS::Cognito::UserPool", {"AdminCreateUserConfig": {"AllowAdminCreateUserOnly": True}}
    )
    template.has_resource_properties(
        "AWS::CloudFront::Distribution",
        {
            "DistributionConfig": {
                "CacheBehaviors": Match.array_with(
                    [
                        Match.object_like(
                            {
                                "PathPattern": "api/*",
                                "CachePolicyId": "4135ea2d-6df8-44a3-9df3-4b5a84be39ad",
                            }
                        )
                    ]
                )
            }
        },
    )


def test_実行ロールにDSQL管理者権限を与えない(stack):
    policies = Template.from_stack(stack).find_resources("AWS::IAM::Policy")
    rendered = json.dumps(policies)
    assert "dsql:DbConnect" in rendered
    assert "dsql:DbConnectAdmin" not in rendered
    assert '"bedrock:*"' not in rendered
    assert '"Action": "*"' not in rendered


def test_cdk_nagの未抑制違反がない(stack):
    errors = Annotations.from_stack(stack).find_error("*", Match.any_value())
    assert errors == []


def test_構成スナップショットが一致する(stack, snapshot):
    template = Template.from_stack(stack).to_json()
    for resource in template["Resources"].values():
        if resource["Type"] == "AWS::Lambda::Function":
            resource["Properties"]["Code"] = {
                "S3Bucket": "CDKアセットバケット",
                "S3Key": "検査fixtureのアセット",
            }
    assert template == snapshot
