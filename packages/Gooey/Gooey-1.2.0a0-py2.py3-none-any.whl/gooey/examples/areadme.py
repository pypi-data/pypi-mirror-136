from gooey import Gooey, Events
from argparse import ArgumentParser

def must_be_exactly_ten(value):
    number = int(value)
    if number == 10:
        return number
    else:
        raise TypeError("Hey! you need to provide exactly the number 10!")

@Gooey(program_name='Validation Example', use_events=[Events.VALIDATE_FORM])
def main():
    parser = ArgumentParser(description="Checkout this validation!")
    parser.add_argument('--ten', metavar='This field should be 10', type=must_be_exactly_ten)
    args = parser.parse_args()
    print(args)

if __name__ == '__main__':
    main()


