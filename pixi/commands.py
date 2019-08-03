import click

from pixi import commandgroup
from pixi.common import get_client, parse_id


@commandgroup.command()
@click.argument('image', nargs=1)
def image(image):
    """Download an image by URL or ID."""
    client = get_client()
    illustration_id = parse_id(
        string=image,
        path='/member_illust.php',
        param='illust_id',
    )
    illustration = client.fetch_illustration(illustration_id)
    illustration.download()
