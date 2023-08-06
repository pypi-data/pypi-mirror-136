#!/usr/bin/env python3

import click
from pypelinez.feature import feature
from pypelinez.apple import apple


@click.group()
def main():
    pass


main.add_command(feature)
main.add_command(apple)

if __name__ == "__main__":
    main()
