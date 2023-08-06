"""
Dynamic updates in Gooey

Simple example demonstrating feeding Gooey a dynamic list of file names at runtime
"""
import datetime
import json
import os
import sys
from argparse import ArgumentParser

from gooey import Gooey, GooeyParser
from gooey import options
from python_bindings.control import Gooey1

directory_error = (
    'Unable to create a folder for your save files!\n'
    'Make sure you\re running in a directory where you have write permissions!'
)

def letter_a(x):
    if x == 'a':
        return x
    else:
        raise Exception("Must be the letter 'a'")





@Gooey1(
    program_name="Using Dynamic Values",
    # poll_external_updates=True
)
def main():
    parser = ArgumentParser(description='An example of polling for updates at runtime')
    g = parser.add_argument_group()
    parser.add_argument(
        '--save',
        required=True,
        type=letter_a,
        metavar='Save Progress',
        # action='store_true',
        help='Take a snap shot of your current progress!'
    )

    kwargs = [
        {'action': 'store_const', 'type': int},
        {'action': 'store_true', 'type': int},
        {'action': 'store_false', 'type': int},
        {'action': 'append', 'type': int},
        {'action': 'append_const', 'type': int},
        {'action': 'count', 'type': int},
        {'action': 'count', 'type': int},
        {'action': 'count', 'type': int},
        {'action': 'count', 'type': int}
    ]
    # parser.add_argument('--a', action='store_const', type=int)
    # parser.add_argument('--b', action='', type=int)
    # parser.add_argument('--c', action='store_true', type=int)
    # parser.add_argument('--c', action='store_false', type=int)



    # parser.add_argument(
    #     '--load',
    #     metavar='Load Previous Save',
    #     help='Load a Previous save file',
    #     dest='filename',
    #     widget='Listbox',
    #     nargs='+',
    #     choices=list_savefiles(),
    #     gooey_options={
    #         'full_width': True,
    #         'validator': {
    #             'test': 'user_input != "Select Option"',
    #             'message': 'Choose a save file from the list'
    #         }
    #     }
    # )

    args = parser.parse_args()

    if args.save:
        save_file()
    else:
        for f in args.filename:
            read_file(os.path.join('saves', f))
            print('Finished reading file %s!' % f)


def read_file(path):
    with open(path, 'r') as f:
        print(f.read())


def list_savefiles():
    """ List all available files in the save directory """
    return list(sorted(os.listdir('saves'), reverse=True))


def show_error_modal(error_msg):
    """ Spawns a modal with error_msg"""
    # wx imported locally so as not to interfere with Gooey
    import wx
    app = wx.App()
    dlg = wx.MessageDialog(None, error_msg, 'Error', wx.ICON_ERROR)
    dlg.ShowModal()
    dlg.Destroy()


def save_file():
    """Save a plain ol' text file with some metadata in the title"""
    next_number = '{:04d}'.format(len(list_savefiles()) + 1)
    now = datetime.datetime.now().strftime('%b %d, %Y - %H.%M%p')
    filename = 'Save{}{}.save'.format(next_number, now)
    with open(os.path.join('saves', filename), 'w') as f:
        f.write("Hello World!")
    print('Saved {}!'.format(filename))


def mk_savedir():
    """
    Attempt to create a directory where we can store the user's save files
    """
    try:
        os.mkdir('saves')
    except IOError as e:
        if not e.winerror == 183:  # already exists
            show_error_modal(directory_error)
            sys.exit(1)


if __name__ == '__main__':
    mk_savedir()
    main()
