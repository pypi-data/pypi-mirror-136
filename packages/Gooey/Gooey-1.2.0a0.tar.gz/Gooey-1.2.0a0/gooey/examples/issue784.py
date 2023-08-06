from gooey import Gooey, GooeyParser, options


@Gooey(tabbed_groups=True, navigation='SIDEBAR')
def main():
    parser = GooeyParser()
    sub = parser.add_subparsers(dest='ssss')

    # Main TABs
    parser = sub.add_parser('options',
                            prog="Options")

    parent = parser.add_argument_group('Search Options', gooey_options=options.ArgumentGroup(columns=1))
    parent.add_argument('--query-string', help='the search string')

    child_one = parent.add_argument_group('flags',
                                          gooey_options={'show_border': True, 'columns': 2})
    child_one.add_argument('--option1', help='some text here')
    child_one.add_argument('--option3', help='some text here3', gooey_options={'full_width': True})
    child_one.add_argument('--option34', help='some text here3', gooey_options={'full_width': True})
    child_one.add_argument('--option224', help='some text here3',
                           gooey_options={'full_width': True})
    child_one.add_argument('--option24', help='some text here3', gooey_options={'full_width': True})

    child_two = parent.add_argument_group('price', gooey_options={'show_border': True})
    child_two.add_argument('--option2333', help='some text here')

    child_3 = parent.add_argument_group('price', gooey_options={'show_border': True})
    child_3.add_argument('--option333345', help='some text here')

    child_4 = parent.add_argument_group('price', gooey_options={'show_border': True})
    child_4.add_argument('--option333ssss345', help='some text here')

    parent2 = parser.add_argument_group('Search Options2', gooey_options={
        'columns': 3
    })
    parent2.add_argument('--query-string2', help='the search string')

    args = parser.parse_args()

if __name__ == '__main__':
    main()
