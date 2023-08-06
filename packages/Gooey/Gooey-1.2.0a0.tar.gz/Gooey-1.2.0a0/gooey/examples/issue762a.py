from argparse import _StoreAction

from gooey import Gooey, GooeyParser
from python_bindings.control import Gooey1


def foo(*args):
    return [1, 2, 3]


from gooey import GooeyParser, Gooey


@Gooey(dump_build_config=True)
def main():
    parser = GooeyParser()
    group = parser.add_argument_group('Super cool group',
                                      gooey_options={'title': 'My gruop',
                                                     'metavar': 'Hello World!',
                                                     'columns': 2,
                                                     'full_width': 0,
                                                     'show_border': True})

    group.add_argument('--here-for-ui', gooey_options={'visible': False})
    group1 = group.add_argument_group('group1',
                                      gooey_options={'title': 'My gruop',
                                                     'metavar': 'Hello World!',
                                                     'columns': 2,
                                                     'full_width': 0,
                                                     'show_border': True})
    group1.add_argument('Rule_Description', help='desc')
    group1.add_argument('info', help='info')

    parser.parse_args()


if __name__ == '__main__':
    main()
