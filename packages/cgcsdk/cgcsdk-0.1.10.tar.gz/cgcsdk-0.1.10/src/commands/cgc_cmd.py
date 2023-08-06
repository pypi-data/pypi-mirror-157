import click

from src.commands.compute.compute_cmd import compute_delete
from src.utils.version_control import check_version
from src.utils.click_group import CustomCommand


@click.command("rm", cls=CustomCommand)
@click.argument("name", type=click.STRING)
def cgc_rm(name: str):
    """
    Delete a compute pod in user namespace
    \f
    :param name: name of pod to delete
    :type name: str
    """
    check_version()
    compute_delete(name)
