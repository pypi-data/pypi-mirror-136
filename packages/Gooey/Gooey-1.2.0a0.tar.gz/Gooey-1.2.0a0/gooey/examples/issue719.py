import sys
import os

from time import sleep
from random import randint
from gooey import Gooey, GooeyParser


@Gooey(progress_regex=r"^progress: (?P<current>\d+)/(?P<total>\d+)$",
       progress_expr="current / total * 100",
       timing_options={
           'show_time_remaining': True,
           'hide_time_remaining_on_complete': False
       }
       )
def main():
    parser = GooeyParser(prog="example_progress_bar_3")
    parser.add_argument("steps", type=int, default=15)
    parser.add_argument("delay", type=int, default=1)
    parser.add_argument(
        "-v", "--something",
        metavar="* Something",
        help="Anything",
        default=1.0,
        widget="DecimalField")
    args = parser.parse_args(sys.argv[1:])

    for i in range(args.steps):
        print("progress: {}/{}".format(i + 1, args.steps))
        sys.stdout.flush()
        sleep(0.1)
    print("RESTING.....")
    sleep(1)
    for i in range(args.steps):
        print("progress: {}/{}".format(i + 1, args.steps))
        sys.stdout.flush()
        sleep(0.1)


if __name__ == "__main__":
    sys.exit(main())