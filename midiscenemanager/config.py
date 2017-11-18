# -*- coding: utf-8 -*-
"""Scene definition and parsing."""

from collections import OrderedDict, namedtuple

from .saneconfigparser import ConfigParser


Scene = namedtuple('Scene', 'title,on_enter,on_exit')
Panel = namedtuple('Panel', 'title,scenes,cols,rows')


def parse_number(s):
    if s.endswith(('h', 'H')):
        return int(s[:-1], 16)
    else:
        return int(s)


def parse_command(s):
    cmd, *args = s.strip().split()
    kwargs = dict()

    for arg in args:
        try:
            name, val = arg.split('=')
            kwargs[name] = parse_number(val)
        except:
            pass

    return cmd, kwargs


def parse_scenes(parser):
    scenes = OrderedDict()

    for sect in parser.sections():
        if sect.startswith('scene:'):
            name = sect.split(':', 1)[1].strip()
            scenes[name] = Scene(
                title=parser.get(sect, 'title', name),
                on_enter=[parse_command(line)
                          for line in parser.get(sect, 'on_enter', '').splitlines()
                          if line.strip()],
                on_exit=[parse_command(line)
                         for line in parser.get(sect, 'on_exit', '').splitlines()
                         if line.strip()],
            )
    return scenes


def parse_panels(parser):
    panels = OrderedDict()

    for sect in parser.sections():
        if sect.startswith('panel:'):
            name = sect.split(':', 1)[1].strip()
            panels[name] = Panel(
                title=parser.get(sect, 'title'),
                scenes=parser.getlist(sect, 'scenes'),
                cols=parser.getint(sect, 'cols'),
                rows=parser.getint(sect, 'rows'),
            )
    return panels


def parse_config(filename):
    parser = ConfigParser()
    parser.read(filename)
    config = {
        'default_panel': parser.get('global', 'default_panel'),
        'scenes': parse_scenes(parser),
        'panels': parse_panels(parser),
    }
    return config


if __name__ == '__main__':
    import pprint
    import sys

    pprint.pprint(parse_scenes(sys.argv[1]))
