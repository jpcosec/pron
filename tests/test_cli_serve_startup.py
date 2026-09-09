"""Regression coverage for the CLI's server startup summary."""

from unittest.mock import patch

from pron.cli.main import main
from pron.serve import Server


def test_serve_prints_worlds_before_entering_loop(tmp_path, capsys):
    # Preserve the real class API: worlds is a method returning paths, not Worlds.
    with patch("pron.serve.Server", autospec=Server) as server_type:
        server = server_type.return_value
        server.worlds.return_value = {"home": str(tmp_path)}
        result = main(["serve", "--world", f"home={tmp_path}"])

    assert result == 0
    server.worlds.assert_called_once_with()
    server.serve_forever.assert_called_once_with()
    assert f"home={tmp_path}" in capsys.readouterr().out
