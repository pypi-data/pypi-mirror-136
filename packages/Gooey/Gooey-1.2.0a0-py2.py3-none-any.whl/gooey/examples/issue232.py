from argparse import ArgumentParser
from gooey import Gooey
import time
import signal


running = [True]

@Gooey(shutdown_signal=signal.CTRL_BREAK_EVENT,
       program_name='Graceful Stopification',
       disable_progress_bar_animation=True)
def main_argparse():
    parser = ArgumentParser(description='Sum two integers.')
    # parser.add_argument('integers', type=int, nargs=2)
    # signal.signal(signal.SIGTERM, logit)
    # signal.signal(signal.SIGINT , logit)
    # signal.signal(signal.SIGBREAK, logit)
    # signal.signal(signal.SIGILL, logit)

    try:
        args = parser.parse_args()
        end = time.time() + 101111
        while time.time() < end and running[0]:
            print("Just try and stop me!")
            # print('waiting...', time.time(), running)
            time.sleep(0.2)

        if not running:
            print("stopped due to Ctrl+C")
    except (KeyboardInterrupt, SystemExit):
        print("HOLY SHIT!!!")


def logit(*args):
    print(args, 'logit')
    # raise Exception("get fucked!!!!")
    running[0] = False
    # print("HELLLLLLL")
    print("Shutting down!")

if __name__ == "__main__":
    # main_argparse()
    main_argparse()