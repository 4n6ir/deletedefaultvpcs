#!/usr/bin/env python3
import os

import aws_cdk as cdk

from deletedefaultvpcs.deletedefaultvpcs_stack import DeletedefaultvpcsStack

app = cdk.App()

DeletedefaultvpcsStack(
    app, 'DeletedefaultvpcsStack',
    env = cdk.Environment(
        account = os.getenv('CDK_DEFAULT_ACCOUNT'),
        region = os.getenv('CDK_DEFAULT_REGION')
    ),
    synthesizer = cdk.DefaultStackSynthesizer(
        qualifier = '4n6ir'
    )
)

cdk.Tags.of(app).add('deletedefaultvpcs','deletedefaultvpcs')

app.synth()
