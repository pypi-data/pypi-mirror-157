"""Top-level package for MW Dry Invoke."""

__author__ = """Justin Stout"""
__email__ = 'midwatch@jstout.us'
__version__ = '0.2.3'

from invoke import task
from invoke.exceptions import Failure


@task(help={'part': "major, minor, or patch/hotfix"})
def bumpversion(ctx, part):
    """Bump project version: major, minor, patch/hotfix

    Raises:
        Failure: part not in [major, minor, patch]
    """
    part = 'patch' if part == 'hotfix' else part

    if part not in ['major', 'minor', 'patch']:
        raise Failure('Not a valid part')

    ctx.run(f'bump2version --no-tag {part}')
