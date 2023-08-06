import click

import demotools


@click.command()
@click.argument('val1')
@click.argument('val2')
@click.argument('val3')
def dt(val1, val2, val3):
    demotools.int_char_int(val1, val2, val3)


def main():
    dt()
