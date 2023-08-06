import logging
import typer

from mlstfest import __version__, __title__


app = typer.Typer()
LOG = logging.getLogger(__name__)


@app.callback()
def callback(debug: bool = False):
    """
    mlstfest - Strain type assignment to novel microbe sequences
    """
    if debug:
        typer.echo("DEBUG logging enabled")
        logging.basicConfig(level=logging.DEBUG)


@app.command()
def version():
    """
    Print the version
    """
    typer.echo("%s, version %s" % (__title__, __version__))
