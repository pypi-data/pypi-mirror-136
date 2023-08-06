import argparse
from gooey import Gooey

@Gooey()
def process_options():
  parser = argparse.ArgumentParser()
  parser.add_argument("-v", action="count", help='verbose mode', default=0)
  return parser.parse_args()


if __name__ == '__main__':
  args = process_options()
  print(args.v)