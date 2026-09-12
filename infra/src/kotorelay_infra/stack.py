"""待機計算固定費を持たないKotoRelayのAWS構成を定義する。"""

from pathlib import Path
from typing import cast

from aws_cdk import (
    CfnOutput,
    Duration,
    RemovalPolicy,
    Stack,
    Tags,
)
from aws_cdk import (
    aws_apigatewayv2 as apigw,
)
from aws_cdk import (
    aws_apigatewayv2_authorizers as authorizers,
)
from aws_cdk import (
    aws_apigatewayv2_integrations as integrations,
)
from aws_cdk import (
    aws_cloudfront as cloudfront,
)
from aws_cdk import (
    aws_cloudfront_origins as origins,
)
from aws_cdk import (
    aws_cognito as cognito,
)
from aws_cdk import (
    aws_dsql as dsql,
)
from aws_cdk import aws_events as events
from aws_cdk import aws_events_targets as targets
from aws_cdk import (
    aws_iam as iam,
)
from aws_cdk import (
    aws_lambda as lambda_,
)
from aws_cdk import (
    aws_logs as logs,
)
from aws_cdk import (
    aws_s3 as s3,
)
from aws_cdk import (
    aws_s3vectors as vectors,
)
from cdk_nag import NagSuppressions
from constructs import Construct

ROOT = Path(__file__).resolve().parents[3]


class KotoRelayStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, *, asset_path: str | None = None):
        super().__init__(scope, construct_id)
        Tags.of(self).add("Project", "kotorelay")
        Tags.of(self).add("CostCenter", "sample")
        data = s3.Bucket(
            self,
            "Content",
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            enforce_ssl=True,
            removal_policy=RemovalPolicy.RETAIN,
        )
        web = s3.Bucket(
            self,
            "Frontend",
            encryption=s3.BucketEncryption.S3_MANAGED,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            enforce_ssl=True,
            removal_policy=RemovalPolicy.RETAIN,
        )
        cluster = dsql.CfnCluster(self, "Database", deletion_protection_enabled=True)
        cluster.apply_removal_policy(RemovalPolicy.RETAIN)
        vector_bucket = vectors.CfnVectorBucket(self, "Vectors")
        vector_bucket.apply_removal_policy(RemovalPolicy.RETAIN)
        vector_index = vectors.CfnIndex(
            self,
            "VectorIndex",
            vector_bucket_arn=vector_bucket.attr_vector_bucket_arn,
            index_name="knowledge",
            data_type="float32",
            dimension=256,
            distance_metric="cosine",
        )
        pool = cognito.UserPool(
            self,
            "Users",
            self_sign_up_enabled=False,
            sign_in_aliases=cognito.SignInAliases(username=True),
            password_policy=cognito.PasswordPolicy(
                min_length=14,
                require_digits=True,
                require_lowercase=True,
                require_uppercase=True,
                require_symbols=True,
            ),
            mfa=cognito.Mfa.OPTIONAL,
            mfa_second_factor=cognito.MfaSecondFactor(sms=False, otp=True),
            removal_policy=RemovalPolicy.RETAIN,
        )
        client = pool.add_client(
            "WebClient",
            generate_secret=False,
            auth_flows=cognito.AuthFlow(user_srp=True),
            prevent_user_existence_errors=True,
            access_token_validity=Duration.minutes(15),
            id_token_validity=Duration.minutes(15),
        )
        log_group = logs.LogGroup(
            self,
            "ApiLogs",
            retention=logs.RetentionDays.ONE_WEEK,
            removal_policy=RemovalPolicy.DESTROY,
        )
        role = iam.Role(self, "ApiRole", assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"))
        log_group.grant_write(role)
        data.grant_read_write(role)
        role.add_to_policy(
            iam.PolicyStatement(actions=["dsql:DbConnect"], resources=[cluster.attr_resource_arn])
        )
        role.add_to_policy(
            iam.PolicyStatement(
                actions=["bedrock:InvokeModel"],
                resources=[
                    self.format_arn(
                        service="bedrock",
                        account="",
                        resource="foundation-model",
                        resource_name="amazon.nova-lite-v1:0",
                    ),
                    self.format_arn(
                        service="bedrock",
                        account="",
                        resource="foundation-model",
                        resource_name="amazon.titan-embed-text-v2:0",
                    ),
                ],
            )
        )
        role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "s3vectors:PutVectors",
                    "s3vectors:GetVectors",
                    "s3vectors:QueryVectors",
                    "s3vectors:DeleteVectors",
                ],
                resources=[vector_index.attr_index_arn],
            )
        )
        code_path = asset_path or str(ROOT)
        api_function = lambda_.DockerImageFunction(
            self,
            "Api",
            architecture=lambda_.Architecture.X86_64,
            code=lambda_.DockerImageCode.from_image_asset(
                code_path,
                file="backend/Dockerfile.lambda",
                exclude=["backend/tests", "**/__pycache__"]
                + sorted(
                    [
                        p.name
                        for p in ROOT.iterdir()
                        if p.name not in {"backend", "pyproject.toml", "uv.lock"}
                    ]
                ),
            ),
            role=role,
            log_group=log_group,
            memory_size=1024,
            timeout=Duration.seconds(29),
            reserved_concurrent_executions=3,
            environment={
                "KOTORELAY_MODE": "aws",
                "KOTORELAY_BUCKET": data.bucket_name,
                "KOTORELAY_DSQL_HOST": cluster.attr_endpoint,
                "KOTORELAY_DSQL_USER": "kotorelay_app",
                "KOTORELAY_REGION": self.region,
                "KOTORELAY_ISSUER": pool.user_pool_provider_url,
                "KOTORELAY_CLIENT_ID": client.user_pool_client_id,
                "KOTORELAY_VECTOR_INDEX_ARN": vector_index.attr_index_arn,
                "KOTORELAY_MAX_QUESTIONS_PER_DAY": "100",
            },
        )
        worker = lambda_.DockerImageFunction(
            self,
            "Worker",
            architecture=lambda_.Architecture.X86_64,
            code=lambda_.DockerImageCode.from_image_asset(
                code_path,
                file="backend/Dockerfile.lambda",
                exclude=["backend/tests", "**/__pycache__"]
                + sorted(
                    [
                        p.name
                        for p in ROOT.iterdir()
                        if p.name not in {"backend", "pyproject.toml", "uv.lock"}
                    ]
                ),
                cmd=["kotorelay.worker.handler"],
            ),
            role=role,
            log_group=log_group,
            memory_size=1024,
            timeout=Duration.minutes(5),
            reserved_concurrent_executions=1,
            environment={
                "KOTORELAY_MODE": "aws",
                "KOTORELAY_BUCKET": data.bucket_name,
                "KOTORELAY_DSQL_HOST": cluster.attr_endpoint,
                "KOTORELAY_DSQL_USER": "kotorelay_app",
                "KOTORELAY_REGION": self.region,
                "KOTORELAY_VECTOR_INDEX_ARN": vector_index.attr_index_arn,
            },
        )
        events.Rule(
            self,
            "DeliverOutbox",
            schedule=events.Schedule.rate(Duration.minutes(15)),
            targets=[targets.LambdaFunction(worker, retry_attempts=2)],
        )
        authorizer = authorizers.HttpJwtAuthorizer(
            "UserJwt", pool.user_pool_provider_url, jwt_audience=[client.user_pool_client_id]
        )
        api = apigw.HttpApi(self, "HttpApi", default_authorizer=authorizer)
        api_access_logs = logs.LogGroup(
            self, "ApiAccessLogs", retention=logs.RetentionDays.ONE_WEEK
        )
        stage = cast(apigw.CfnStage, cast(apigw.IHttpStage, api.default_stage).node.default_child)
        stage.access_log_settings = apigw.CfnStage.AccessLogSettingsProperty(
            destination_arn=api_access_logs.log_group_arn,
            format='{"requestId":"$context.requestId","status":"$context.status","routeKey":"$context.routeKey"}',
        )
        integration = integrations.HttpLambdaIntegration("FastAPI", api_function)
        api.add_routes(path="/{proxy+}", methods=[apigw.HttpMethod.ANY], integration=integration)
        distribution = cloudfront.Distribution(
            self,
            "Distribution",
            default_behavior=cloudfront.BehaviorOptions(
                response_headers_policy=cloudfront.ResponseHeadersPolicy.SECURITY_HEADERS,
                origin=origins.S3BucketOrigin.with_origin_access_control(web),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
            ),
            additional_behaviors={
                "api/*": cloudfront.BehaviorOptions(
                    origin=origins.HttpOrigin(
                        f"{api.api_id}.execute-api.{self.region}.amazonaws.com"
                    ),
                    viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.HTTPS_ONLY,
                    allowed_methods=cloudfront.AllowedMethods.ALLOW_ALL,
                    cache_policy=cloudfront.CachePolicy.CACHING_DISABLED,
                    origin_request_policy=cloudfront.OriginRequestPolicy.ALL_VIEWER_EXCEPT_HOST_HEADER,
                )
            },
            default_root_object="index.html",
            price_class=cloudfront.PriceClass.PRICE_CLASS_100,
            minimum_protocol_version=cloudfront.SecurityPolicyProtocol.TLS_V1_2_2021,
        )
        api_function.add_environment(
            "KOTORELAY_FRONTEND_ORIGIN", f"https://{distribution.distribution_domain_name}"
        )
        # 固定費と追加ログ費を避ける例外は対象リソースに限定し、根拠をテンプレートへ残す。
        NagSuppressions.add_resource_suppressions(
            [data, web],
            [
                {
                    "id": "AwsSolutions-S1",
                    "reason": "サンプルではS3アクセスログの保存費を抑え、API監査IDを使う。",
                }
            ],
        )
        NagSuppressions.add_resource_suppressions(
            distribution,
            [
                {"id": "AwsSolutions-CFR1", "reason": "サンプルの配信先を国で制限する要件がない。"},
                {
                    "id": "AwsSolutions-CFR2",
                    "reason": "WAFの月額基本料を避け、JWT認証と入力検査で制限する。",
                },
                {
                    "id": "AwsSolutions-CFR3",
                    "reason": "アクセスログの追加保存費を避け、本文なしのAPIログを使う。",
                },
                {
                    "id": "AwsSolutions-CFR4",
                    "reason": "ドメイン維持費を避け、CloudFront既定HTTPSを使う。",
                },
            ],
        )
        NagSuppressions.add_resource_suppressions(
            pool,
            [
                {
                    "id": "AwsSolutions-COG8",
                    "reason": "追加料金を避け、自己登録禁止・短命JWT・所属の再確認を使う。",
                }
            ],
        )
        NagSuppressions.add_resource_suppressions(
            role,
            [
                {
                    "id": "AwsSolutions-IAM5",
                    "reason": "対象バケット内の内容ハッシュキーと対象ログ内の動的ストリームのみ。",
                }
            ],
            apply_to_children=True,
        )
        CfnOutput(self, "Website", value=f"https://{distribution.distribution_domain_name}")
        CfnOutput(self, "DatabaseEndpoint", value=cluster.attr_endpoint)
        CfnOutput(self, "ContentBucket", value=data.bucket_name)
        CfnOutput(self, "FrontendBucket", value=web.bucket_name)
        CfnOutput(self, "AppRoleArn", value=role.role_arn)
        CfnOutput(self, "UserPoolId", value=pool.user_pool_id)
        CfnOutput(self, "UserPoolClientId", value=client.user_pool_client_id)
