# pixi

[![Build Status](https://travis-ci.org/dazuling/pixi.svg?branch=master)](https://travis-ci.org/dazuling/pixi)
[![Coverage Status](https://coveralls.io/repos/github/dazuling/pixi/badge.svg?branch=master)](https://coveralls.io/github/dazuling/pixi?branch=master)
[![Pypi](https://img.shields.io/pypi/v/pixi.svg)](https://pypi.python.org/pypi/pixi)
[![Pyversions](https://img.shields.io/pypi/pyversions/pixi.svg)](https://pypi.python.org/pypi/pixi)

A command line tool to download images from Pixiv.

```
Usage: pixi [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  auth    Log into Pixiv and generate a refresh token.
  config  Edit the config file.
  image   Download an image by URL or ID.
```

## Usage

This tool can be installed from PyPI as `pixi`.

```sh
$ pip install --user pixi
or
$ pipx install pixi
```

Make sure the location that pixi installs to is a part of `$PATH`.

After installation, configure pixi with the following command.

```sh
$ pixi config
```

Refer to the [configuration section](#Configuration) for details on the various
configuration options.

Now you can begin downloading!

For example, the following commands download an image. pixi accepts both a URL
to the image as well as just the image ID. The same applies to all inputs that
accept ID values.

```sh
$ pixi image https://www.pixiv.net/member_illust.php?mode=medium&illust_id=64930973
```

```sh
$ pixi image 64930973
```

TODO Implementation of the following commands:

Downloading all the images of an artist can be done with the following command.

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
$ pixi bookmarks --tag="has cats"
```

To view all the options available to a specific command, run the command with
the `--help` flag. For example, `image`'s options can be viewed with the
following command.

```sh
$ pixi --help image
```

pixi keeps track of which images have been downloaded and will avoid
downloading duplicate images. However, if you wish to re-download images,
pass the `--ignore-duplicates` flag.

If you wish to wipe the database of tracked downloads, run the following
command and confirm the action.

```sh
$ pixi wipe
```

END TODO

## Configuration

The configuration file is in `ini` format. A demo configuration is included
below. To run pixi, a default download directory must be configured.

```ini
[pixi]
; Leave this blank; the script will auto-populate it.
refresh_token =
; The default directory for images to be downloaded to.
download_directory = /home/azuline/images/pixiv
```

TODO filename format configuration option, support subdirectories
for `{artist}/{image}`-like formatting.
