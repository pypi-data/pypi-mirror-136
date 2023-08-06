from gooey import GooeyParser, Gooey
from pprint import pprint


@Gooey(dump_build_config=True)
def main():
    parser = GooeyParser(description="FFQ profile generation and auditing")

    g2 = parser.add_argument_group("g2", "Group 2")
    g1 = parser.add_argument_group("g1", "Group 1")

    g1.add_argument("abc", default="abc")
    g2.add_argument("def", default="def")
    parser.add_argument("hij", default="hij")

    args = parser.parse_args()

    pprint(args)


if __name__ == "__main__":
    main()
