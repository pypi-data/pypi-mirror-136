from gooey import Gooey, GooeyParser, constants


@Gooey(program_name="Gooey!!!!",
       tabbed_groups=False,
       naviation=constants.TABBED)
def parse_args():
    # import sys
    # print(sys.argv)
    parser = GooeyParser(description="Gooey turns your CLI apps into beautiful GUIs!")
    parser.add_argument('data_directory',
                        action='store',
                        default='scale=',
                        # type=lambda x: 'foo ' + x,
                        widget='DirChooser',
                        # gooey_options={
                        #     'validator': {
                        #         'test': "__import__('re').search('\d+x\d+', user_input) != None",
                        #         'message': 'oops'
                        #     }
                        # }
                        )
    import sys
    print(sys.argv)
    args = parser.parse_args()
    print(args)

if __name__ == '__main__':
    conf = parse_args()
    print("Done")