"""CDK構成を生成し、cdk-nagの違反を検出する。"""

from aws_cdk import App, Aspects
from cdk_nag import AwsSolutionsChecks
from kotorelay_infra.stack import KotoRelayStack

app = App()
stack = KotoRelayStack(app, "KotoRelay")
Aspects.of(app).add(AwsSolutionsChecks(verbose=True))
app.synth()
