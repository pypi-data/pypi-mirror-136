from argparse import ArgumentParser
from gooey import Gooey, GooeyParser
import time
from time import sleep
import signal
import sys

running = [True]


@Gooey(progress_regex=r"^progress: (\d+)%$",
       show_stop_warning=False,
       hide_progress_msg=True,
       disable_progress_bar_animation=True
       )
def main():
    parser = GooeyParser(prog="example_progress_bar_1")
    _ = parser.parse_args(sys.argv[1:])

    for i in range(100):
        print("progress: {}%".format(i + 1))
        sys.stdout.flush()
        sleep(0.1)


if __name__ == "__main__":
    sys.exit(main())