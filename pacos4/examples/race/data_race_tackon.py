import sys
from typing import List, Any
import logging
import argparse
import time
import random
from .data_race import create_board


def run(log_lvl: str = 'WARNING'):
    print('=== data-race-tackon ===')
    board = create_board(log_lvl)
    while not board.any_exited():
        board.step()
    board.exit()


def description() -> str:
    return \
    """
    A data race demo.
    """


def process_args() -> Any:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--log", default='WARNING')
    parser.add_argument("--run_count", default=5, type=int)
    parser.add_argument('-h', '--help', action='help', 
                        default=argparse.SUPPRESS,
                        help=description())
    args = parser.parse_args(sys.argv[1:])
    logging.basicConfig(format='%(levelname)s:%(message)s',
                        level=logging.getLevelName(args.log.upper()))
    random.seed(time.time())
    return args


def main():
    args = process_args()
    for _ in range(args.run_count):
        run(args.log)


if __name__ == "__main__":
    main()
