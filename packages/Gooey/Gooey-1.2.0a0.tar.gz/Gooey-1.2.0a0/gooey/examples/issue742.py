from argparse import ArgumentParser
from gooey import Gooey, GooeyParser
import time
from time import sleep
import signal
import sys
import argparse



@Gooey()
def main():
    parser = GooeyParser(description='Process some data.')
    parser.add_argument('required_field1', metavar='Some Field 1', type=argparse.FileType(encoding="UTF-8"), help='Enter some numbers!')
    parser.add_argument('required_field2', metavar='Some Field 2', help='Enter some text!')
    parser.add_argument('required_field3', metavar='Some Option', help='Select a Option', widget='Dropdown', choices=['a', 'b', 'c'])
    parser.add_argument('-f', '--foo', metavar='Some Flag', action='store_true', help='I turn things on and off')
    parser.add_argument(
        "-v", "--something",
        metavar="* Something",
        help="Anything",
        default=1.0,
        widget="DecimalField")
    parser.parse_args()



if __name__ == '__main__':
    main()