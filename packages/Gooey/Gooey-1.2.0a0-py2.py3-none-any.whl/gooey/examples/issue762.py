from argparse import _StoreAction

from gooey import Gooey, GooeyParser
from python_bindings.control import Gooey1


def foo(*args):
    return [1,2,3]


def mything(x):
    raise Exception('Nope!!!!')

class MyAction(_StoreAction):
    def __call__(self, *args, **kwargs):
        # print('Hello!!!')
        super(MyAction, self).__call__(*args, **kwargs)


@Gooey
def main():
    parser = GooeyParser()
    subs = parser.add_subparsers()
    curl = subs.add_parser('curl')
    subgroup = curl.add_argument_group('Super cool group')
    subgroup.add_argument(
        '-foo',
        metavar='Hello World!',
        help='I am a helpful message!')

    ffmpeg = subs.add_parser('ffmpeg')
    subgroup2 = ffmpeg.add_argument_group('Super cool group2')
    subgroup2.add_argument(
        '-foob',
        metavar='Hello World Again!',
        help='I am a helpful message!')

    parser.parse_args()



if __name__ == '__main__':
    main()