"""Tests for CLI source adapter wiring."""

import os
from unittest import mock

import click
from click.testing import CliRunner

from smae.sources.acled import ACLEDAdapter
from smae.sources.gfw import GFWAdapter
from smae.sources.idmc import IDMCAdapter


def test_build_sources_no_env_vars():
    """With no env vars, only GFW (keyless) and IDMC are created."""
    with mock.patch.dict(os.environ, {}, clear=True):
        from smae.cli.main import _build_sources

        sources = _build_sources()

    # GFW always created, IDMC always created, ACLED skipped
    assert len(sources) == 2
    types = {type(s) for s in sources}
    assert GFWAdapter in types
    assert IDMCAdapter in types
    assert ACLEDAdapter not in types


def test_build_sources_with_acled_creds():
    """With ACLED creds set, all three adapters are created."""
    env = {
        "SMAE_ACLED_EMAIL": "test@example.com",
        "SMAE_ACLED_PASSWORD": "secret",
        "SMAE_GFW_KEY": "gfw-key-123",
        "SMAE_IDMC_KEY": "idmc-key-456",
    }
    with mock.patch.dict(os.environ, env, clear=True):
        from smae.cli.main import _build_sources

        sources = _build_sources()

    assert len(sources) == 3
    types = {type(s) for s in sources}
    assert ACLEDAdapter in types
    assert GFWAdapter in types
    assert IDMCAdapter in types


def test_build_sources_acled_needs_both_fields():
    """ACLED adapter is only created when both email and password are set."""
    env_email_only = {"SMAE_ACLED_EMAIL": "test@example.com"}
    with mock.patch.dict(os.environ, env_email_only, clear=True):
        from smae.cli.main import _build_sources

        sources = _build_sources()

    types = {type(s) for s in sources}
    assert ACLEDAdapter not in types


def test_cli_sources_command():
    """The 'sources' command lists available adapters."""
    from smae.cli.main import cli

    runner = CliRunner()
    result = runner.invoke(cli, ["sources"])
    assert result.exit_code == 0
    assert "ACLED" in result.output
    assert "GFW" in result.output
    assert "IDMC" in result.output


def test_cli_networks_shows_all_eight():
    """The 'networks' command shows all eight metabolic networks."""
    from smae.cli.main import cli

    runner = CliRunner()
    result = runner.invoke(cli, ["networks"])
    assert result.exit_code == 0
    assert "Carbon Accumulation" in result.output
    assert "Biodiversity" in result.output
    assert "Ocean" in result.output
    assert "Labor" in result.output
    assert "VIII" in result.output


def test_cli_convergence_help():
    """The 'convergence' command exists and has help text."""
    from smae.cli.main import cli

    runner = CliRunner()
    result = runner.invoke(cli, ["convergence", "--help"])
    assert result.exit_code == 0
    assert "30-day" in result.output
