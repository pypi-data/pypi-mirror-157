import os

# Disable SAM spyware, should be opt-in
os.environ['SAM_CLI_TELEMETRY'] = '0'
os.environ['CDK_NEW_BOOTSTRAP'] = '1'


def ssm_lookup(scope, parameter_name):
    from aws_cdk import aws_ssm
    return aws_ssm.StringParameter.value_from_lookup(scope, parameter_name=parameter_name)
