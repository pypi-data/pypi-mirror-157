import logging
import typing
from constructs import Construct
from aws_cdk import (
    Stack,
    aws_ssm,
    aws_codestarconnections,
    pipelines
)
from .connections import GithubConnection
from .sources import github_url_split


class CodePipelineStack(Stack):
    _connections: typing.Dict[str, aws_codestarconnections.CfnConnection]={}
    _sources: typing.Dict[str, pipelines.CodePipelineSource]={}
    codepipeline: pipelines.CodePipeline=None
    # source: pipelines.CodePipelineSource
    # waves: typing.Dict[str, pipelines.Wave]={}
    # stages: typing.Dict[str, typing.Dict[str, Stage]]={}

    def __init__(
            self,
            scope: Construct, id: str,
            *, 
            connections: typing.Dict[str, dict]={},
            sources: typing.Dict[str, dict]={},
            pipeline: dict=None,
            **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        self.connections = self.add_connections(connections)
        self.sources = self.add_sources(sources)
        if pipeline:
            if 'id' not in pipeline:
                pipeline['id'] = id
            self.codepipeline = self.add_codepipeline(**pipeline)

    @property
    def connections(self) -> typing.Dict[str, aws_codestarconnections.CfnConnection]:
        return self._connections

    @connections.setter
    def connections(self, values: dict) -> None:
        self._connections = {}
        for name, connection in values.items():
            if not connection.startswith('arn:aws:codestar-connections'):
                logging.warning(f"{name} not a CS arn {connection}")
            self._connections[name] = connection

    def add_connections(self, values: dict) -> typing.Dict[str, aws_codestarconnections.CfnConnection]:
        """A dict of CodestarConnections arn by name

        Args:
            connections (dict): CodestarConnections by name and connection details

            connection details can be:
            - ConnectionARN
            - SSM
            - Connection attributes like {"myorg": {"connection_name": "myorg"}, "org2": ...}
        """
        connections = {}
        for name, connection in values.items():
            if isinstance(connection, dict):
                connection = GithubConnection(self, name, **connection).arn
            if connection.startswith('aws:ssm:'):
                connection = aws_ssm.StringParameter.value_from_lookup(self, parameter_name=connection.replace('aws:ssm:', ''))
            connections[name] = connection
        return connections



    @property
    def sources(self) -> typing.Dict[str, pipelines.CodePipelineSource]:
        return self._sources

    @sources.setter
    def sources(self, values: dict) -> None:
        self._sources = values

    def add_sources(self, values: dict) -> typing.Dict[str, pipelines.CodePipelineSource]:
        sources = {}
        for name, source in values.items():
            if isinstance(source, str):
                source ={'url': source}
            if 'url' in source:
                git = github_url_split(url=source['url'])
                del source['url']
                source['repo_string'] = f"{git['owner']}/{git['repo']}"
                source['branch'] = git['branch']
            owner = source['repo_string'].split('/')[0]
            if 'connection_arn' not in source and owner in self.connections:
                source['connection_arn'] = self.connections[owner]
            sources[name] = pipelines.CodePipelineSource.connection(**source)
        return sources



    def add_codepipeline(self, id: str, *, synth: dict={}, **pipelineargs) -> pipelines.CodePipeline:
        if 'synth' not in pipelineargs:
            if isinstance(synth, dict):
                if 'input' not in synth and id in self.sources:
                    synth['input'] = self.sources[id]
                    # Automagically add all sources to synth
                    synth['additional_inputs'] = dict((k, v) for k, v in self.sources.items() if k != id)
                synth = self.add_shellstep(f"{id}-synth", **synth)
            pipelineargs['synth'] = synth
        elif synth:
            logging.warning(f"synth already defined, not applying {synth}")
        if 'pipeline_name' not in pipelineargs:
            pipelineargs['pipeline_name'] = id
        return pipelines.CodePipeline(self, id, **pipelineargs)

    def add_shellstep(self, id: str, **synth) -> pipelines.ShellStep:
        if 'commands' not in synth:
            synth['commands']=[
                'pip install aviv-cdk',
                'npm install -g aws-cdk',
                'cdk synth'
            ]
        return pipelines.ShellStep(id, **synth)
