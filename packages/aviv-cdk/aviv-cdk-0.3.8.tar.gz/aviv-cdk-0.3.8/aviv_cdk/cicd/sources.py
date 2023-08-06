import logging
import typing
from constructs import Construct
from aws_cdk import pipelines

SourceRepositoryAttrs = typing.Dict[typing.Literal['owner', 'repo', 'branch'], str]
GitRepositoryInfo = typing.Dict[typing.Literal['url', 'branch'], str]


class Source(pipelines.CodePipelineSource):
    def __init__(
            self, scope: Construct, id: str, *,
            repo_string: str, branch: str='main',
            url: str='',
            connection_arn: str=None,
            code_build_clone_output: bool=None,
            trigger_on_push: bool=None) -> None:
        super().__init__(scope, id)
        if url:
            git = git_url_split(url=url)
            repo_string = f"{git['owner']}/{git['repo']}"
            branch = git['branch']
        self.connection(
            repo_string=repo_string,
            branch=branch,
            connection_arn=connection_arn,
            code_build_clone_output=code_build_clone_output, trigger_on_push=trigger_on_push
        )


def git_repository_info() -> GitRepositoryInfo:
    import subprocess
    cmd = lambda input: subprocess.check_output(input, shell=True).decode('UTF-8').rstrip()
    url=cmd("git remote get-url origin")
    if url.endswith('.git'):
        url = url.replace('.git', '')

    return dict(
        url=url,
        branch=cmd("git branch --show-current")
    )


def github_url_split(url: str, branch: str='main') -> SourceRepositoryAttrs:
    """Splits a https github url to return a dict with:
    - owner     Github organization
    - repo      the git repository
    - branch    the branch

    Args:
        url (str): a https://github.com/your-org/myrepo
        branch (str, optional): [description]. Defaults to 'main'.

    Returns:
        dict: owner/repo/branch
    """
    if not url.startswith('https://github.com/'):
        logging.warning(f"Not an https Github URL: {url}")
    return git_url_split(url, branch)


def git_url_split(url: str, branch: str='main') -> SourceRepositoryAttrs:
    if url.startswith('git@github.com:'):
        url = url.replace('git@github.com:', '')

    repo_attrs = dict(branch=branch)
    # If we have a specific branch
    if url.find('@') > 0:
        branchsplit = url.split('@')
        url = branchsplit[0]
        if branchsplit[1]:
            repo_attrs['branch'] = branchsplit[1]
    if url.endswith('.git'):
        url = url.replace('.git', '')
    urlsplit = url.split('/')
    repo_attrs['owner'] = urlsplit[-2]
    repo_attrs['repo'] = urlsplit[-1]
    return repo_attrs
