import argparse
from gooey import Gooey

@Gooey
def process_options():
    parser = argparse.ArgumentParser()
    parser.add_argument("--grids", type=str, help='top x%% of data')
    return parser.parse_args(['-h'])

args = process_options()