#!/usr/bin/env python
"""Tests for `mw_dry_invoke` package."""
# pylint: disable=redefined-outer-name

import pytest
from click.testing import CliRunner

from mw_dry_invoke import cli


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(cli.main)
    assert result.exit_code == 0
    assert 'mw_dry_invoke.cli.main' in result.output
    help_result = runner.invoke(cli.main, ['--help'])
    assert help_result.exit_code == 0
    assert '--help  Show this message and exit.' in help_result.output
