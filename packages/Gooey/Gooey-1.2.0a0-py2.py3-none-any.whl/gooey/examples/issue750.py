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
    parser.add_argument('Choose Command Line',
                        choices=["--avhw --cbr 6000 --codec h265 --multipass none --preset quality --profile main10 --tier high --level 4.1 --output-depth 10 --vpp-edgelevel strength=9,threshold=12 --bframes 2 --ref 4 --gop-len 150 --lookahead 32 --aq --qp-init 1 --cuda-schedule auto --mv-precision q-pel --colorrange auto --colormatrix auto --colorprim auto --transfer auto --max-cll copy --master-display copy --videoformat auto --chromaloc auto --vpp-unsharp weight=1.5,radius=3 --vpp-gauss 3 --crop 0,0,0,0 --seek 0:00:00.000", "two"],
                        default="two",
                        widget='Dropdown'
                        )
    parser.parse_args()



if __name__ == '__main__':
    main()




