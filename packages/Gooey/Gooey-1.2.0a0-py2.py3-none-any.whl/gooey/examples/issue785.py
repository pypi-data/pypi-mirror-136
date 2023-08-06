"""
Example program to demonstrate Gooey's presentation of subparsers
"""
import shlex

import sys

from gooey import Gooey, GooeyParser, Events
from gooey.python_bindings.constants import TABBED

running = True

with open('t-module-top.txt', 'w') as f:
    f.write(str(sys.argv))

xxx = r""""C:\Users\Chris\Documents\Gooey\venv368\Scripts\python.exe" -u "C:/Users/Chris/Documents/Gooey/gooey/examples/issue785.py" parser1 --textfield "2" --textarea "b'oneline twoline'" --password "hunter42" --commandfield "b'cmdr'" --dropdown "two" --listboxie "Option three" "Option four" -c -c -c -o --mutextwo "mut-2" --filechooser "fc-value" --filesaver "fs-value" --dirchooser "dc-value" --datechooser "2015-01-01" --colourchooser "#000000" --gooey-validate-form --gooey-state eyJhY3RpdmVfZm9ybSI6IFt7ImlkIjogInRleHRmaWVsZCIsICJ0eXBlIjogIlRleHRGaWVsZCIsICJ2YWx1ZSI6ICIyIiwgInBsYWNlaG9sZGVyIjogIiIsICJlcnJvciI6ICIiLCAiZW5hYmxlZCI6IHRydWUsICJ2aXNpYmxlIjogdHJ1ZX0sIHsiaWQiOiAidGV4dGFyZWEiLCAidHlwZSI6ICJUZXh0YXJlYSIsICJ2YWx1ZSI6ICJvbmVsaW5lIHR3b2xpbmUiLCAicGxhY2Vob2xkZXIiOiAiIiwgImVycm9yIjogIiIsICJlbmFibGVkIjogdHJ1ZSwgInZpc2libGUiOiB0cnVlfSwgeyJpZCI6ICJwYXNzd29yZCIsICJ0eXBlIjogIlBhc3N3b3JkRmllbGQiLCAidmFsdWUiOiAiaHVudGVyNDIiLCAicGxhY2Vob2xkZXIiOiAiIiwgImVycm9yIjogIiIsICJlbmFibGVkIjogdHJ1ZSwgInZpc2libGUiOiB0cnVlfSwgeyJpZCI6ICJjb21tYW5kZmllbGQiLCAidHlwZSI6ICJDb21tYW5kRmllbGQiLCAidmFsdWUiOiAiY21kciIsICJwbGFjZWhvbGRlciI6ICIiLCAiZXJyb3IiOiAiIiwgImVuYWJsZWQiOiB0cnVlLCAidmlzaWJsZSI6IHRydWV9LCB7ImlkIjogImRyb3Bkb3duIiwgInR5cGUiOiAiRHJvcGRvd24iLCAic2VsZWN0ZWQiOiAidHdvIiwgImNob2ljZXMiOiBbIlNlbGVjdCBPcHRpb24iLCAib25lIiwgInR3byJdLCAiZXJyb3IiOiBudWxsLCAiZW5hYmxlZCI6IHRydWUsICJ2aXNpYmxlIjogdHJ1ZX0sIHsiaWQiOiAibGlzdGJveGllIiwgInR5cGUiOiAiTGlzdGJveCIsICJzZWxlY3RlZCI6IFsiT3B0aW9uIHRocmVlIiwgIk9wdGlvbiBmb3VyIl0sICJjaG9pY2VzIjogWyJPcHRpb24gb25lIiwgIk9wdGlvbiB0d28iLCAiT3B0aW9uIHRocmVlIiwgIk9wdGlvbiBmb3VyIl0sICJlcnJvciI6IG51bGwsICJlbmFibGVkIjogdHJ1ZSwgInZpc2libGUiOiB0cnVlfSwgeyJpZCI6ICJjb3VudGVyIiwgInR5cGUiOiAiQ291bnRlciIsICJzZWxlY3RlZCI6ICIzIiwgImNob2ljZXMiOiBbIlNlbGVjdCBPcHRpb24iLCAiMCIsICIxIiwgIjIiLCAiMyIsICI0IiwgIjUiLCAiNiIsICI3IiwgIjgiLCAiOSIsICIxMCJdLCAiZXJyb3IiOiBudWxsLCAiZW5hYmxlZCI6IHRydWUsICJ2aXNpYmxlIjogdHJ1ZX0sIHsiaWQiOiAib3ZlcndyaXRlIiwgInR5cGUiOiAiQ2hlY2tib3giLCAiY2hlY2tlZCI6IHRydWUsICJlcnJvciI6IG51bGwsICJlbmFibGVkIjogdHJ1ZSwgInZpc2libGUiOiB0cnVlfSwgeyJpZCI6ICJncm91cF9tdXRleG9uZV9tdXRleHR3byIsICJ0eXBlIjogIlJhZGlvR3JvdXAiLCAiZXJyb3IiOiAiIiwgImVuYWJsZWQiOiB0cnVlLCAidmlzaWJsZSI6IHRydWUsICJzZWxlY3RlZCI6IDEsICJvcHRpb25zIjogW3siaWQiOiAibXV0ZXhvbmUiLCAidHlwZSI6ICJDaGVja2JveCIsICJjaGVja2VkIjogZmFsc2UsICJlcnJvciI6IG51bGwsICJlbmFibGVkIjogZmFsc2UsICJ2aXNpYmxlIjogdHJ1ZX0sIHsiaWQiOiAibXV0ZXh0d28iLCAidHlwZSI6ICJUZXh0RmllbGQiLCAidmFsdWUiOiAibXV0LTIiLCAicGxhY2Vob2xkZXIiOiAiIiwgImVycm9yIjogIiIsICJlbmFibGVkIjogdHJ1ZSwgInZpc2libGUiOiB0cnVlfV19LCB7ImlkIjogImZpbGVjaG9vc2VyIiwgInR5cGUiOiAiRmlsZUNob29zZXIiLCAidmFsdWUiOiAiZmMtdmFsdWUiLCAiYnRuX2xhYmVsIjogIkJyb3dzZSIsICJlcnJvciI6IG51bGwsICJlbmFibGVkIjogdHJ1ZSwgInZpc2libGUiOiB0cnVlfSwgeyJpZCI6ICJmaWxlc2F2ZXIiLCAidHlwZSI6ICJGaWxlU2F2ZXIiLCAidmFsdWUiOiAiZnMtdmFsdWUiLCAiYnRuX2xhYmVsIjogIkJyb3dzZSIsICJlcnJvciI6IG51bGwsICJlbmFibGVkIjogdHJ1ZSwgInZpc2libGUiOiB0cnVlfSwgeyJpZCI6ICJkaXJjaG9vc2VyIiwgInR5cGUiOiAiRGlyQ2hvb3NlciIsICJ2YWx1ZSI6ICJkYy12YWx1ZSIsICJidG5fbGFiZWwiOiAiQnJvd3NlIiwgImVycm9yIjogbnVsbCwgImVuYWJsZWQiOiB0cnVlLCAidmlzaWJsZSI6IHRydWV9LCB7ImlkIjogImRhdGVjaG9vc2VyIiwgInR5cGUiOiAiRGF0ZUNob29zZXIiLCAidmFsdWUiOiAiMjAxNS0wMS0wMSIsICJidG5fbGFiZWwiOiAiQ2hvb3NlIERhdGUiLCAiZXJyb3IiOiBudWxsLCAiZW5hYmxlZCI6IHRydWUsICJ2aXNpYmxlIjogdHJ1ZX0sIHsiaWQiOiAiY29sb3VyY2hvb3NlciIsICJ0eXBlIjogIkNvbG91ckNob29zZXIiLCAidmFsdWUiOiAiIzAwMDAwMCIsICJidG5fbGFiZWwiOiAiQ2hvb3NlIENvbG91ciIsICJlcnJvciI6IG51bGwsICJlbmFibGVkIjogdHJ1ZSwgInZpc2libGUiOiB0cnVlfV19"""
xxx = shlex.split(xxx)[3:]

@Gooey(
    optional_cols=2,
    program_name="Subparser Demo",
    navigation=TABBED,
    tabbed_groups=True,
    dump_build_config=True,
    show_success_modal=False,
    # cli=xxx,
    use_events=[Events.VALIDATE_FORM]
)
def main():
    parser = GooeyParser()
    subs = parser.add_subparsers(help='commands', dest='command')

    parser_one = subs.add_parser('parser1', prog="Parser 1")
    parser_one.add_argument('--textfield', default=2, widget="TextField", required=True)
    parser_one.add_argument('--textarea', default="oneline twoline", widget='Textarea')
    parser_one.add_argument('--password', default="hunter42", widget='PasswordField')
    parser_one.add_argument('--commandfield', default="cmdr", widget='CommandField')
    parser_one.add_argument('--dropdown',
                        choices=["one", "two"], default="two", widget='Dropdown')
    parser_one.add_argument('--listboxie',
                        nargs='+',
                        default=['Option three', 'Option four'],
                        choices=['Option one', 'Option two', 'Option three',
                                 'Option four'],
                        widget='Listbox',
                        gooey_options={
                            'height': 300,
                            'validate': '',
                            'heading_color': '',
                            'text_color': '',
                            'hide_heading': True,
                            'hide_text': True,
                        }
                        )
    parser_one.add_argument('-c', '--counter', default=3, action='count',
                        widget='Counter')
    #
    parser_one.add_argument("-o", "--overwrite", action="store_true",
                        default=True,
                        widget='CheckBox')

    ### Mutex Group ###
    verbosity = parser_one.add_mutually_exclusive_group(
        required=True,
        gooey_options={
            'initial_selection': 1
        }
    )
    verbosity.add_argument(
        '--mutexone',
        default=True,
        action='store_true',
        help="Show more details")

    verbosity.add_argument(
        '--mutextwo',
        default='mut-2',
        widget='TextField')

    parser_one.add_argument("--filechooser", default="fc-value", widget='FileChooser')
    parser_one.add_argument("--filesaver", default="fs-value", widget='FileSaver')
    parser_one.add_argument("--dirchooser", default="dc-value", widget='DirChooser')
    parser_one.add_argument("--datechooser", default="2015-01-01", widget='DateChooser')
    parser_one.add_argument("--colourchooser", default="#000000", widget='ColourChooser')

    parser_two = subs.add_parser('parser2', prog="parser 2, mah man")
    parser_two.add_argument('textfield', default=2, type=int, widget="TextField")
    parser_two.add_argument('textarea', default="oneline twoline",
                            widget='Textarea')
    parser_two.add_argument('password', default="hunter42", widget='PasswordField')
    parser_two.add_argument('commandfield', default="cmdr", widget='CommandField')
    parser_two.add_argument('dropdown',
                            choices=["one", "two"], default="two", widget='Dropdown')
    parser_two.add_argument('listboxie',
                            nargs='+',
                            default=['Option three', 'Option four'],
                            choices=['Option one', 'Option two', 'Option three',
                                     'Option four'],
                            widget='Listbox',
                            gooey_options={
                                'height': 300,
                                'validate': '',
                                'heading_color': '',
                                'text_color': '',
                                'hide_heading': True,
                                'hide_text': True,
                            }
                            )
    parser_two.add_argument('-c', '--counter', default=3, action='count',
                            widget='Counter')
    #
    parser_two.add_argument("-o", "--overwrite", action="store_true",
                            default=True,
                            widget='CheckBox')

    ### Mutex Group ###
    verbosity = parser_two.add_mutually_exclusive_group(
        required=True,
        gooey_options={
            'initial_selection': 1
        }
    )
    verbosity.add_argument(
        '--mutexone',
        default=True,
        action='store_true',
        help="Show more details")

    verbosity.add_argument(
        '--mutextwo',
        default='mut-2',
        widget='TextField')

    parser_two.add_argument("--filechooser", default="fc-value", widget='FileChooser')
    parser_two.add_argument("--filesaver", default="fs-value", widget='FileSaver')
    parser_two.add_argument("--dirchooser", default="dc-value", widget='DirChooser')
    parser_two.add_argument("--datechooser", default="2015-01-01",widget='DateChooser')
    parser_two.add_argument("--colourchooser", default="#000000", widget='ColourChooser')

    dest_vars = [
        'textfield',
        'textarea',
        'password',
        'commandfield',
        'dropdown',
        'listboxie',
        'counter',
        'overwrite',
        'mutextwo',
        'filechooser',
        'filesaver',
        'dirchooser',
        'datechooser',
        'colourchooser'
    ]

    with open('tmp2.txt', 'w') as f:
        f.write(str(sys.argv))
    args = parser.parse_args()
    import time
    time.sleep(.3)
    for i in dest_vars:
        assert getattr(args, i) is not None
    print("Success")


if __name__ == '__main__':
    main()