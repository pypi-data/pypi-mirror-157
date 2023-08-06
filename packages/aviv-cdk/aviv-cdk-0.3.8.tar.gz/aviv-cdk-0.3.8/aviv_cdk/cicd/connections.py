from constructs import Construct
from aws_cdk import (
    aws_codestarconnections,
    aws_ssm,
    CfnOutput
)


class GithubConnection(aws_codestarconnections.CfnConnection):
    _ssm: aws_ssm.StringParameter

    def __init__(self, scope: Construct, id: str, connection_name: str=None, *, host_arn: str=None, provider_type: str='GitHub', tags: dict=None, ssm_parameter_prefix: str='/github/connections', **kwargs) -> None:
        """Create a CodeStar connection between AWS and Github app.

        Outputs the CS connection arn and a link to the connector.
        It must be validated by a Github organisation administrator.

        Args:
            scope (Construct): stack/contruct this connection belongs to
            id (str): primary name for the construct and CS connection.
            connection_name (str, optional): specific name for the CS connection. Defaults to id.
            host_arn (str, optional): _description_. Defaults to None.
            provider_type (str, optional): _description_. Defaults to 'GitHub'.
            tags (dict, optional): _description_. Defaults to None.
            ssm_parameter_prefix (str, optional): _description_. Defaults to '/github/connections'.
        """
        if not connection_name:
            connection_name = id
        super().__init__(scope, id, connection_name=connection_name, host_arn=host_arn, provider_type=provider_type, tags=tags)
        CfnOutput(
            self, "output",
            value=self.attr_connection_arn,
            description="Validate with Github [app connection](https://console.aws.amazon.com/codesuite/settings/connections)"
        )
        if ssm_parameter_prefix:
            self._ssm = aws_ssm.StringParameter(
                self, "ssm",
                string_value=self.attr_connection_arn,
                parameter_name=f"{ssm_parameter_prefix}/{connection_name}"
            )

    @property
    def arn(self) -> str:
        return self.attr_connection_arn

    @property
    def ssm(self) -> str:
        return self._ssm.parameter_name
