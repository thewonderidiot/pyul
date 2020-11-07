#!/usr/bin/env python3

import argparse
import sys
import traceback
from monitor import Monitor

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Yul System')
    parser.add_argument('cards', nargs='?', default=None, help='File containing punch card deck')
    parser.add_argument('-y', '--year', type=int, default=None,
                        help='Feature year for Yul, which changes available features and ouput')
    parser.add_argument('-d', '--date', type=str, default=None, help='YYYY-MM-DD format for date to show on listing')
    parser.add_argument('-j', '--job', type=int, default=None, help='Job number')
    args = parser.parse_args()

    # Default to stdin for input punch cards
    if args.cards is None:
        card_file = sys.stdin
    else:
        card_file = open(args.cards, 'r')

    # Initialize a simulation of the MIT Monitor operating system
    mon = Monitor(card_file, year=args.year, date=args.date, job=args.job)

    # Process the input punch cards
    try:
        mon.execute()
    except Exception as e:
        traceback.print_exc()

    # Close the punch card file if we opened one
    if card_file != sys.stdin:
        card_file.close()
