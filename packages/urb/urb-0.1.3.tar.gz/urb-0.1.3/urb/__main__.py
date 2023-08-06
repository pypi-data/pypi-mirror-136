"""
the cli logic managing all the commands, arguments and options

currently implemented commands are

define
    usage -
        urb define <search_term>
        e.g. urb define hello

    args -
        --google, -g
        uses the google dictionary API instead of urban dictionary
        e.g. urb define --google hello
            urb define -g hello

        --index, -i
        APIs teend to provide multiple definitions for a word at time.
        this option lets specify what definition is to be displayed
        e.g. urb define -i 2 noob
             urb define --index boon
"""

import click

from urb.wrappers import google, urban
from urb import prints


@click.group()
@click.option('--index', '-i', 'index', type=bool, is_flag=True,help='specific definition to display')
@click.option('--google', '-g', 'goog', type=bool, is_flag=True, help='use google search instead.')
def urb(goog, index): #pylint: disable=unused-argument
    # the group definition.
    # empty cuz idk what i can do with it
    pass

@urb.command("define")
@click.option('--google', '-g', 'goog', type=bool, default=False, is_flag=True)
@click.option('--index', '-i', 'index', type=int, default=0, required=False)
@click.argument("word")
def define(word, goog, index):
    '''
    the define command.
    usage and options specified at the beginning of the file
    '''
    try:
        if goog:
            definition = google.define(word)
            prints.print_goog(definition[0], index)
        else:
            definition = urban.define(word)
            prints.print_urb(definition[:index + 1][-1])
    except ConnectionError:
        print('please connect to the internet :)')
    except IndexError:
        print('\nno definitions found for this word :(')

def main():
    urb(obj={})

if __name__ == "__main__":
    main()
