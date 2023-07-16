import argparse

import src.steg as steg


def hide(args):
    print("-- HIDE --")
    steg.encode(args.input_file, message_filename=args.file_to_be_hidden, key=args.key, hidden_filename=args.output)


def reveal(args):
    print("-- REVEAL --")
    steg.decode(args.input_file, key=args.key, output_name=args.output)
    

def main():
    parser = argparse.ArgumentParser(description="SteganoPy - Hide data inside of images")
    parser.add_argument("method", choices=["hide", "reveal"], help="Method to execute")
    parser.add_argument("input_file", help="Filename of medíum")
    parser.add_argument("-k", "--key", help="(Optional) AES key")
    parser.add_argument("-o", "--output", help="(Optional) Filename of result")
    args, unknown_args = parser.parse_known_args()
    if args.key:
        args.key = args.key.encode('utf-8')
    if args.method == "hide":
        # Create the argument parser specific to hide
        hide_parser = argparse.ArgumentParser(add_help=False)
        hide_parser.add_argument("file_to_be_hidden", help="File to be hidden")
        hide_args = hide_parser.parse_args(unknown_args)
        # Add arguments from global parser
        hide_args.input_file = args.input_file
        hide_args.key = args.key
        hide_args.output = args.output
        hide(hide_args)
    elif args.method == "reveal":
        reveal(args)


if __name__ == "__main__":
    main()
