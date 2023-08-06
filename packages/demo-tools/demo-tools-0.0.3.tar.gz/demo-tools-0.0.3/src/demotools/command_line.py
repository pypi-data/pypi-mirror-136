import click

import demotools


@click.command()
@click.argument('val1', type=int)
@click.argument('val2', type=int)
@click.argument('val3', type=int)
def dt(val1, val2, val3):
    demotools.int_char_int(val1, val2, val3)


def main():
    dt()
