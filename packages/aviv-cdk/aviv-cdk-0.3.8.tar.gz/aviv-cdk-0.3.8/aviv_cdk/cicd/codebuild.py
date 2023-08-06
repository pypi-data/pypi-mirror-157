import typing
from aws_cdk import aws_codebuild


def buildenv(environment_variables: dict) -> typing.Dict[str, aws_codebuild.BuildEnvironmentVariable]:
    """Facilitate Codebuild environmemt creation
    Simply pass your dict to be turned a env variabltes
    For values that starts with 'aws:sm:', the prefix will be striped off
     and the Codebuild env variable type wil be set to SECRETS_MANAGER.

    Args:
        environment_variables (dict): key/value store to turn into Codebuild Env

    Returns:
        typing.Dict[aws_codebuild.BuildEnvironmentVariable]: [description]
    """
    envs = dict()
    for env, value in environment_variables.items():
        if isinstance(value, str) and value.startswith('aws:sm:'):
            envs[env] = aws_codebuild.BuildEnvironmentVariable(
                value=value.replace('aws:sm:', ''),
                type=aws_codebuild.BuildEnvironmentVariableType.SECRETS_MANAGER
            )
        else:
            envs[env] = aws_codebuild.BuildEnvironmentVariable(value=value)
    return envs


def load_buildspec(specfile: str='buildspec.yml') -> aws_codebuild.BuildSpec:
    """Load a buildspec yaml file

    Args:
        specfile ([type]): [description]

    Returns:
        [type]: [description]
    """
    import yaml
    with open(specfile, encoding="utf8") as fp:
        bsfile = fp.read()
        bs = yaml.safe_load(bsfile)
        return aws_codebuild.BuildSpec.from_object(value=bs)
