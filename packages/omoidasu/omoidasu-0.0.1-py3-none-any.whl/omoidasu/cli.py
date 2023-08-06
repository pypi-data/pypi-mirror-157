import click


@click.group()
def main():
    pass


@main.command()
def list():
    pass


@main.command()
def review():
    pass


@main.command()
def add():
    pass


@main.command()
def remove():
    pass


@main.command()
def edit():
    pass


@main.command()
def stats():
    pass


if __name__ == "__main__":
    main()
