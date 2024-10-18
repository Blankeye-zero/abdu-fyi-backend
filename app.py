#!/usr/bin/env python3
import os

import aws_cdk as cdk

from abdu_fyi_backend.abdu_fyi_backend_stack import AbduFyiBackendStack


app = cdk.App()
AbduFyiBackendStack(app, "AbduFyiBackendStack",
                    env=cdk.Environment(account=os.getenv(
                        'CDK_DEFAULT_ACCOUNT'), region='us-east-1'),
                    )

app.synth()
