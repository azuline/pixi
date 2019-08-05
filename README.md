# pixi

[![Build Status](https://travis-ci.org/dazuling/pixi.svg?branch=master)](https://travis-ci.org/dazuling/pixi)
[![Coverage Status](https://coveralls.io/repos/github/dazuling/pixi/badge.svg?branch=master)](https://coveralls.io/github/dazuling/pixi?branch=master)
[![Pypi](https://img.shields.io/pypi/v/pixi.svg)](https://pypi.python.org/pypi/pixi)
[![Pyversions](https://img.shields.io/pypi/pyversions/pixi.svg)](https://pypi.python.org/pypi/pixi)

A command line tool to download illustrations from Pixiv.

```
Usage: pixi [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  artist     Download illustrations of an artist by URL or ID.
  auth       Log into Pixiv and generate a refresh token.
  bookmarks  Download illustrations bookmarked by a user.
  config     Edit the config file.
  failed     View illustrations that failed to download.
  illust     Download an illustration by URL or ID.
  migrate    Upgrade the database to the latest migration.
  wipe       Wipe the saved history of downloaded illustrations.
```

## Usage

This tool can be installed from PyPI as `pixi`.

```sh
$ pip install --user pixi
or
$ pipx install pixi
```

Make sure the location that pixi installs to is a part of `$PATH`.

After installation, create the database and configure pixi with the following
commands.

```sh
$ pixi migrate  # Migrate the database
$ pixi config  # Configure pixi
```

Refer to the [configuration section](#Configuration) for details on the various
configuration options.

Now you can begin downloading!

For example, the following commands download an illustration. pixi accepts both
a URL to the illustration as well as just the illustration ID. The same applies
to all inputs that accept ID values.

```sh
$ pixi illustration https://www.pixiv.net/member_illust.php?mode=medium&illust_id=64930973
```

```sh
$ pixi illustration 64930973
```

Downloading all the illustrations of an artist can be done with the following
command.

```sh
$ pixi artist https://www.pixiv.net/member.php?id=2188232
```

Bookmarks, public and private, can be downloaded with the following command.

```sh
$ pixi bookmarks
```

The public bookmarks of other users can also be downloaded.

```sh
$ pixi bookmarks --user https://www.pixiv.net/member.php?id=2188232
```

And the following command downloads all bookmarks matching a user-assigned
bookmark tag.

```sh
$ pixi bookmarks --tag "has cats"
```

To view all the options available to a specific command, run the command with
the `--help` flag. For example, `illustration`'s options can be viewed with the
following command.

```sh
$ pixi --help illustration
```

TODO THE FOLLOWING

When downloading many images from an artist or a user's bookmarks, an image
can occasionally fail to download. If an image fails to download after several
retries, it will be recorded and skipped. Failed images can be viewed with the
following command.

```sh
$ pixi failed
```

If an image on the failed list is successfully downloaded, it will
automatically be removed from the list. To wipe the entire failed list, the
following command should be run.

```sh
$ pixi wipe --table=failed
```

pixi also keeps track of which illustrations have been downloaded and will avoid
downloading duplicate illustrations. However, if you wish to re-download
illustrations, pass the `--allow-duplicates` (or `-a`) flag.

By default, illustration downloads will be tracked if they are downloaded to
the default downloads directory and not tracked if they aren't. This behavior
can be manually set with the `--track/--no-track` (or `-t/-T`) flag.

If you wish to wipe the database of tracked downloads, run the following
command and confirm the action.

```sh
$ pixi wipe --table=downloads
```

END TODO

## Configuration

The configuration file is in `ini` format. A demo configuration is included
below. To run pixi, a default download directory must be configured.

```ini
[pixi]
; Leave this blank; the script will auto-populate it.
refresh_token =
; The default directory for iillustrations to be downloaded to.
download_directory = /home/azuline/images/pixiv
```

TODO filename format configuration option, support subdirectories
for `{artist}/{image}`-like formatting.
