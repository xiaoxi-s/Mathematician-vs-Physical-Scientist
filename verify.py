import argparse


from utils import init_connection, query_exist

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Verification that scientists are all in a table')
    parser.add_argument('-f', '--file_path', type=str,
                        help='path to file that contains simplified urls (names)')
    parser.add_argument('-db', '--database_path', type=str,
                        help='path to database that contains (name, bio) pairs')
    args = parser.parse_args()

    # parameter initialization
    file_path = args.file_path
    database_path = args.database_path
    table_name = 'mathematicians' if 'math' in file_path else 'physical_sci'

    connection, cursor = init_connection(database_path)

    with open(file_path, 'r', encoding='utf-8') as url_file:
        names = url_file.readlines()

    if names is None or len(names) == 0:
        raise ValueError('Invalid name file')

    with open('./wiki_sci_spiders/log/log_verify_' + table_name + '.txt', 'w+', encoding='utf-8') as f:
        for name in names:
            name = name.strip()
            if query_exist(connection, name, table_name):
                pass
            else:
                f.write('https://en.wikipedia.org/wiki/' + name + '\n')
