"""CLI module."""


import click


@click.group()
@click.option("-v", "--verbose", help="Show additional information")
@click.option("-d", "--debug/--no-debug", help="Show debug information")
def cli_commands(verbose=None, debug=None):
    """CLI commands"""


@cli_commands.command()
@click.argument("Tag", type=str, default="", required=False)
def list_cards(tag):
    """List all cards."""


@cli_commands.command()
@click.argument("Tag", type=str, default="", required=False)
def review_cards(tag):
    """Review all cards."""


@cli_commands.command()
def add_card():
    """Add new card."""


@cli_commands.command()
def remove_card():
    """Remove card."""


@cli_commands.command()
def edit_card():
    """Edit card."""


@cli_commands.command()
def stats():
    """Show user stats."""


def main():
    """Main function."""
    cli_commands()


if __name__ == "__main__":
    main()
