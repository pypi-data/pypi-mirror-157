# -*- coding: utf-8 -*-
# This file is part of https://github.com/26fe/jsonstat.py
# Copyright (C) 2016 gf <gf@26fe.com>
# See LICENSE file

# stdlib
from __future__ import print_function
# from __future__ import unicode_literals
import os
import sys

# external modules
import click

# jsonstat
JSONSTAT_HOME = os.path.join(os.path.dirname(__file__), '..', '..')
try:
    import jsonstatpy
except ImportError:
    sys.path.append(JSONSTAT_HOME)
    import jsonstatpy


@click.group()
@click.version_option(version=jsonstatpy.__version__)
def cli():
    # this function name will go into the setup.py,
    # if you rename it check setup.py
    pass


@cli.command()
@click.option('--cache_dir', default='./data', help='where to store downloaded files')
@click.argument('args', nargs=-1)
def info(cache_dir, args):
    if len(args) == 0:
        args = ['http://json-stat.org/samples/oecd-canada-col.json']

    d = jsonstatpy.cache_dir(cache_dir)
    print("downloaded file(s) are stored into '{}'\n".format(d))
    for arg in args:

        if arg.startswith("http"):
            print("download '{}'".format(arg))
            o = jsonstatpy.from_url(arg)
        else:
            print("reading '{}'".format(arg))
            o = jsonstatpy.from_file(arg)

        print(o)
        if isinstance(o, jsonstatpy.JsonStatCollection):
            print("\nfirst dataset:\n")
            print(o.dataset(0))


@cli.command()
@click.argument('args', nargs=-1)  # help="file containing jsonstat to validate")
def validate(args):
    for arg in args:
        if arg.startswith("http"):
            print("download '{}'".format(arg))
            contents = jsonstatpy.download(arg)
        else:
            print("reading '{}'".format(arg))
            contents = open(arg).read()
        click.echo("validate '{}'".format(arg))
        jsonstatpy.validate(contents)


if __name__ == "__main__":
    cli()
