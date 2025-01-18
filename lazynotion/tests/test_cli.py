from click.testing import CliRunner
from lazynotion.cli import cli  # import your main cli group

class TestCLICommands:
    def setup_method(self):
        self.runner = CliRunner()

    def test_page_create_command(self):
        result = self.runner.invoke(cli, [
            'page', 'create',
            '--parent-id', '123',
            '--title', 'Test Page'
        ])
        assert result.exit_code == 0
        assert 'Created page' in result.output
