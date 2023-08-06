import typer
from timecli.commands import oracle

__version__ = "0.1.3"

app = typer.Typer()
app.add_typer(oracle.app, name="oracle")


def call_version(value: bool):
    if value:
        typer.echo(f"timecli: version {__version__}")
        raise typer.Exit()


@app.callback()
def version_callback(
        version: bool = typer.Option(None, "--version", callback=call_version),
):
    pass


if __name__ == '__main__':
    app()
