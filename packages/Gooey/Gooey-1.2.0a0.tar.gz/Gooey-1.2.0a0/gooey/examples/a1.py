from argparse import _StoreAction

from gooey import Gooey, GooeyParser
from gooey import Gooey
from gooey import Events


def foo(*args):
    return [1,2,3]


def mything(x):
    num = int(x)
    if num > 0 and num < 10:
        return num
    else:
        raise ValueError('Must be between 0 and 10 inclusive')


class MyAction(_StoreAction):
    def __call__(self, *args, **kwargs):
        # print('Hello!!!')
        super(MyAction, self).__call__(*args, **kwargs)


@Gooey(program_name="Gooey!", dump_build_config=True,
        # cli='user-code -z "False" --ignore-gooey --gooey-validate-form --'.split()
        # cli='"C:\\Users\\Chris\\Documents\\Gooey\\venv368\\Scripts\\python.exe" -u "C:/Users/Chris/Documents/Gooey/gooey/examples/a1.py" user-code -p "1234" --gooey-validate-form',
       use_events=[Events.VALIDATE_FORM]
        )
def main():
    parser = GooeyParser(prog="Gooey",
                         description="Gooey turns your CLI apps into beautiful GUIs!",
                         )
    parser.add_argument('-f', '--foo', help='root', gooey_options={
        'root': 'root f!!'
    })
    subs = parser.add_subparsers(title='gooey-managed')
    clientvvv = subs.add_parser('user-smode')
    clientp = subs.add_parser('user-code')
    clientp.add_argument('-f', '--foo',
                         type=mything,
                         action=MyAction,
                         help='subbie',
                         widget='DirChooser',
                         gooey_options={
        'sub': 'sub f!!'
    })
    clientp.add_argument('-z', '--zzz')
    clientp.add_argument('-d', '--dope', type=int, widget='DirChooser')
    clientp.add_argument('-u', '--uope', type=mything, gooey_options={
        'validator': {
            'test': 'int(user_input) < 2',
            'message': 'some helpful message'
    }
    })
    clientp.add_argument('-p', type=int, choices=foo(),  gooey_options={
    })

    # args = parser.parse_args(['user-code', '-f', 'yo yo yo', '-d', '123'])
    # args = parser.parse_args('user-code -p 1234 --gooey-validate-form'.split())
    args = parser.parse_args()
    import sys
    a = 10
    print(args)
    # print('DUN got me fucked up!')
    # print('DUN GOOFED')
    # import sys
    # sys.exit(-80085)


if __name__ == '__main__':
    conf = main()
    # print("Done")