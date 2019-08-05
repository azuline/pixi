import functools

import click


def download_directory(func):
    return functools.wraps(func)(
        click.option(
            '--directory', '-d',
            type=click.Path(exists=True, file_okay=False),
            help='Config override for download directory.',
        )(func)
    )


def allow_duplicates(func):
    return functools.wraps(func)(
        click.option(
            '--allow-duplicates', '-a',
            is_flag=True,
            default=False,
            help='Downloads illustrations even if previously downloaded.',
        )(func)
    )


def track_download(func):
    return functools.wraps(func)(
        click.option(
            '--track/--no-track', '-t/-T',
            default=None,
            help='Record the downloaded image to avoid future duplicates.',
        )(func)
    )


def page(func):
    return functools.wraps(func)(
        click.option(
            '--page', '-p',
            nargs=1,
            type=click.INT,
            default=1,
            help='Page to start downloading on.',
        )(func)
    )


def visibility(func):
    return functools.wraps(func)(
        click.option(
            '--visibility', '-v',
            type=click.Choice(['public', 'private']),
            help=(
                'The visibility of the bookmarks that should be downloaded. '
                'Leave blank to download all.'
            ),
        )(func)
    )
