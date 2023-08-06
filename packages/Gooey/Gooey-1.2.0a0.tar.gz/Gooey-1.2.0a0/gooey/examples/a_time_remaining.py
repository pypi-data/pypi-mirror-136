from random import random
from typing import List

from gooey import Gooey, GooeyParser, constants, Events
import os

from gooey.python_bindings.types import PublicGooeyState
from gooey.python_bindings.types import FormField


save_dir = os.path.join(os.path.dirname(__file__), 'saves')

def grab_latest(args, state: PublicGooeyState):
    form: List[FormField] = state['active_form']
    for item in form:
        if item['id'] == 'length':
            item['value'] = 'Good job, mang!'
        if item['id'] == 'options':
            item['choices'] = os.listdir(save_dir)
    state['active_form'] = form
    return state

def handle_error(args, state: PublicGooeyState):
    form: List[FormField] = state['active_form']
    for item in form:
        if item['id'] == 'length':
            item['value'] = 'no way, bro'
    state['active_form'] = form
    return state


def nope(x):
    if int(x) == 10:
        return int(x)
    else:
        raise Exception('omg. Get fucked!')


@Gooey(optional_cols=2,
        program_name="Elapsed / Remaining Timer on Progress in Gooey",
        progress_regex=r"^progress: (?P<current>\d+)/(?P<total>\d+)$",
        progress_expr="current / total * 100",
        use_events=[Events.VALIDATE_FORM, Events.ON_SUCCESS, Events.ON_ERROR],
        show_sidebar=True,
        show_preview_warning=False,
        timing_options={
            'show_time_remaining':True,
            'hide_time_remaining_on_complete':False
        },
        menu=[{'name': 'Help', 'items': [{'type': 'Link', 'menuTitle': 'Visit Our Site',
                                         'url': 'https://github.com/chriskiehl/Gooey'}]}]
        )
def parse_args():
    print('hello!')
    print('starting run!')
    prog_descrip = 'Elapsed / Remaining Timer on Progress in Gooey'
    parser = GooeyParser(
        description=prog_descrip,
        on_success=grab_latest,
        on_error=handle_error
    )

    from random import choices

    sub_parsers = parser.add_subparsers(help='commands', dest='command')

    range_parser = sub_parsers.add_parser('range')

    range_parser.add_argument('--length',default=10, type=nope, widget='MultiFileChooser')

    group = range_parser.add_argument_group('foobar')
    group.add_argument(
        '--options',
        choices=os.listdir(save_dir),
        nargs='*',
        widget='Listbox')

    # subgroup = group.add_argument_group("inner")
    # subgroup.add_argument('--schlength', default='55th street')
    #
    # strange_parser = sub_parsers.add_parser('strange')
    # strange_parser.add_argument('--length', default=10)
    #
    # strange_parser = sub_parsers.add_parser('mange')

    x = parser.parse_args()
    import time
    # raise Exception("FUCK!")
    with open(os.path.join(save_dir, f'Save-{int(time.time())}.txt'), 'w') as f:
        f.write('hello')
    print(x)
    return x


def compute_range(length):
    for i in range(length):
        # print("sometin")
        import time
        from random import randint
        time.sleep(0.5)
        print(f"progress: {i + 1}/{length}")

if __name__ == '__main__':
    conf = parse_args()
    if conf.command == 'range':
        compute_range(int(conf.length))