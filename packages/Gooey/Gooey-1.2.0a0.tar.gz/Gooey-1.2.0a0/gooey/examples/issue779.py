import math

from gooey import Gooey, GooeyParser

parser = GooeyParser()


@Gooey(program_name='Area of a Circle Program',
       menu=[{'name': 'Help', 'items': [{'type': 'Link', 'menuTitle': 'Visit Our Site',
                                         'url': 'https://github.com/chriskiehl/Gooey'}]}])
def main():
    parser.add_argument('-r', '--radius', type=float, help='Radius of a Circle')
    args = parser.parse_args()
    area = circle_area(args.radius)
    print(area)


def circle_area(r: float):
    return math.pi * r * r


if __name__ == '__main__':
    main()