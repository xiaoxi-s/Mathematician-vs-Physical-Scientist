import argparse
import sqlite3

from utils import *
from analysis import naive_analyzer

analyzer_types = [naive_analyzer]

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Interface for Analyzing text')
    parser.add_argument('-db', '--database_path', type=str,
                        help='path to database that contains (name, bio) pairs')
    parser.add_argument('-at', '--analyzer_type', type=int,
                        help='integer denotes type of the analyzer: 0 - naive')
    args = parser.parse_args()

    database_path = args.database_path
    analyzer_type = args.analyzer_type

    connection, cursor = init_connection(database_path)

    args = parser.parse_args()

    pass