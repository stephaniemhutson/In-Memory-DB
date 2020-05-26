from collections import Counter
import csv
import os
import sys


class Database():
    def __init__(self, file_name):
        self._file_name = file_name
        self._data = self._get_data()
        self._counts = self._get_counts()
        # indicates whether we need to make a file change or not
        self._changes_made = False
        # storage for when we are in a transaction
        self._sets = {}
        self._deletes = []
        self._set_count = Counter()
        self._in_txn = False

    def _get_data(self):
        '''
        Loads the csv file given into a dictionary
        '''
        try:
            f = open(self._file_name, 'r')
            data = self.format_csv(f)
            f.close()
        except FileNotFoundError:
            data = {}
        return data

    def _get_counts(self):
        '''
        Pre-processes the counts for each value
        '''
        counts = Counter()
        for v in self._data.values():
            counts[v] += 1
        return counts

    def get_value(self, key):
        value = self._data.get(key)
        if self._in_txn:
            value = self._sets.get(key, value)
        return value

    def set_value(self, key, value):
        self._changes_made = True
        current = self.get_value(key)
        if self._in_txn:
            self._sets[key] = value
            self._set_count[value] += 1
            if current:
                self._set_count[current] -= 1
        else:
            self._data[key] = value
            # add one to the count for value
            self._counts[value] += 1
            if current:
                # subtract one from the existing count for the value
                self._counts[current] -= 1

    def delete(self, key):
        current = self._data.get(key)
        if current:
            if self._in_txn:
                self._deletes.append(key)
                # set value to None in txn so it's easier to GET
                self._sets[key] = None
                self._set_count[current] -= 1
            else:
                # remove the row from the data
                self._data.pop(key)
                # subtract one from the existing count for the value
                self._counts[current] -= 1
            # only make changes if the data already exists.
            self._changes_made = True

    def begin(self):
        self._in_txn = True

    def commit(self):
        # exist the transaction and save
        self._in_txn = False
        # update data from the transaction
        self._data.update(self._sets)
        for deleted in self._deletes:
            self._data.pop(deleted)
        for value, count in self._set_count.items():
            self._counts[value] += count
        # clear transaction data
        self._sets = {}
        self._set_count = Counter()
        self._deletes = []
        # save
        self.save()

    def rollback(self):
        if self._in_txn:
            self._in_txn = False

            # reset the data to what it was before the transaction
            self._sets = {}
            self._set_count = Counter()
            self._deletes = []
        else:
            print('TRANSACTION NOT FOUND')

    def format_csv(self, f):
        reader = csv.reader(f)
        return {
            key.strip(): value.strip() for key, value in reader
        }

    def count(self, value):
        return self._counts[value] + self._set_count[value]

    def save(self):
        # only write to the file if changes have been made
        if self._changes_made:
            if not self._in_txn:
                # save all changes
                f = open(self._file_name, 'w')
                f.write(
                    '\n'.join(f'{key},{value}'
                    for key, value in self._data.items())
                )
                f.close()

    def receive_data(self):
        # Accept a command from the program runner
        stdin = input('> ')
        commands = stdin.split(' ')
        command = commands[0]
        try:
            if command == 'SET':
                assert(len(commands) == 3)
                self.set_value(commands[1], commands[2])
            elif command == 'GET':
                assert(len(commands) == 2)
                value = self.get_value(commands[1])
                print(value if value else 'NULL')
            elif command == 'DELETE':
                assert(len(commands) == 2)
                self.delete(commands[1])
            elif command == 'COUNT':
                assert(len(commands) == 2)
                print(self.count(commands[1]))
            elif command == 'BEGIN':
                self.begin()
            elif command == 'COMMIT':
                self.commit()
            elif command == 'ROLLBACK':
                self.rollback()
            elif command == 'END':
                pass
            else:
                print('Invalid command')
        except AssertionError:
            print('Invalid command')

        if command == 'END':
            self.save()
        else:
            self.receive_data()


if __name__ == '__main__':
    if len(sys.argv) > 1:
        file_name = sys.argv[1]
    else:
        file_name = 'db.csv'
    db = Database(file_name)
    try:
        db.receive_data()
    except KeyboardInterrupt:
        print('\nInterrupted. Saving changes unless in transaction.')
        db.save()
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
