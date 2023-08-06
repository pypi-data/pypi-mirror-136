from gooey import GooeyParser, Gooey


@Gooey(show_sidebar=True)
def main():
    parser = GooeyParser()
    search_options = parser.add_argument_group('Search Options', 'Customize the search options',
                                               gooey_options={
                                                   'show_border': True,
                                                   'columns': 2})
    search_options.add_argument('--query', help='base search string')
    search_options.add_argument('--query2', help='base search string')
    search_flags = search_options.add_argument_group('Flags',
                                                     gooey_options={'show_border': True}
                                                     )

    search_flags.add_argument('--buy-it-now', help="Will immediately purchase if possible")
    search_flags.add_argument('--auction', help="Place bids up to PRICE_MAX")

    foobar = search_options.add_mutually_exclusive_group(
        gooey_options={'title': 'foobar',
                       'show_border': True,
                       'label_color': '#00ff00'}
    )
    foobar.add_argument('--snortRule', help='oneie')
    foobar.add_argument('--mtxRule', help='twoie')
    foobar.add_argument('--three', help='twoie')

    parser.parse_args()


if __name__ == '__main__':
    main()