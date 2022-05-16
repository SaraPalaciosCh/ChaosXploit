from argparse import ArgumentParser, ArgumentTypeError
import random
import sys
import json


def find_changes(input_file):
    file1 = open(input_file, 'r')

    buckets = json.load(file1)

    res = True
    message = "Steady State validated"
    for bucket in buckets:
        vals = buckets[bucket]
        if not vals["SS_Collectable"]:
            res = False
            message = "Failed validation for Collectable Buckets"
        if not vals["SS_ACL_Collectable"]:
            res = False
            message = "Failed validation for ACL Collectable Buckets"

    print(f"Is Steady State validated?: {res}")
    print(message)
    return res


def select_random_List(input_file, output_file, size):
    file = open(input_file, 'r')
    lines = file.readlines()
    res = random.sample(lines, size)
    final = {
        bucket.rstrip(): {
            "SS_Collectable": True,
            "SS_ACL_Collectable": True
        } for bucket in res}

    with open(output_file, 'w') as selected:
        json.dump(final, selected)


def print_help():
    print('No arguments received')


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-l",
                        dest="bucket_list",
                        required=True,
                        help="a list with bucket names.")
    parser.add_argument("-n",
                        dest="number",
                        type=int,
                        default=50,
                        required=False,
                        help="Number of buckets to be selected")
    parser.add_argument("-o",
                        dest="output",
                        type=str,
                        required=False,
                        default="output.txt",
                        help="output file.")

    if len(sys.argv) == 1:
        print_help()
        sys.exit()

    arguments = parser.parse_args()

    select_random_List(arguments.bucket_list, arguments.output, arguments.number)
