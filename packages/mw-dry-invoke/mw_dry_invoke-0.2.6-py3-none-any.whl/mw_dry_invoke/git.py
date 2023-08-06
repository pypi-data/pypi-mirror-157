"""Common Git tasks."""
from pathlib import Path

from invoke import Collection, task
from invoke.exceptions import Failure


def init(ctx, username, repo_name, cc_version, gitflow=True):
    """Init scm repo (if required).

    Raises:
        Failure: .gitignore does not exist

    Returns:
        None
    """
    if not Path('.gitignore').is_file():
        raise Failure('.gitignore does not exist')

    is_new_repo = not Path('.git').is_dir()
    uri_remote = f'git@github.com:{username}/{repo_name}.git'
    commit_msg = f'new package from midwatch/cc-py3-pkg ({cc_version})'
    branches = ['main']

    if is_new_repo:
        ctx.run('git init')
        ctx.run('git add .')
        ctx.run(f'git commit -m "{commit_msg}"')
        ctx.run('git branch -M main')
        ctx.run('git remote add origin {}'.format(uri_remote))
        ctx.run('git tag -a "v_0.0.0" -m "cookiecutter ref"')

    if gitflow:
        ctx.run('git flow init -d')
        ctx.run('git flow config set versiontagprefix v_')
        branches.append('develop')

    if is_new_repo:
        for branch in branches:
            ctx.run(f'git push -u origin {branch}')

        ctx.run('git push --tags')


@task
def push(ctx):
    """Push all branches and tags to origin."""

    ctx.run('git push --all')
    ctx.run('git push --tags')


@task
def status(ctx):
    """Show status of remote branches."""
    ctx.run(
        'git for-each-ref --format="%(refname:short) %(upstream:track)" refs/heads'
    )


collection = Collection()
collection.add_task(push)
collection.add_task(status)
