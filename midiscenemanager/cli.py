#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
os.environ["KIVY_NO_ARGS"] = "1"  # noqa:E402

import click

from midiscenemanager.midiscenemanager import MIDISceneManagerApp


@click.command()
@click.option(
    '-l', '--language', help='Default language of the App', default='en',
    type=click.Choice(['en', 'es', 'de', 'fr'])
)
def main(language):
    """Run MIDISceneManagerApp with the given language setting.
    """
    MIDISceneManagerApp(language).run()
