

import gooey
from gooey import Gooey

@Gooey
def main():
    parser = gooey.GooeyParser(description='Add two integers together, then subtract a decimal')
    parser.add_argument('--first', type=int, widget="IntegerField", gooey_options={'min': 5, 'max': 20})
    parser.add_argument('--second', type=int, widget="Slider", gooey_options={'min': 1, 'max': 10})
    parser.add_argument('--third', type=int, widget="DecimalField", gooey_options={'min': 0, 'max': 5.0})
    args = parser.parse_args()
    print(args.first + args.second - args.third)

main()