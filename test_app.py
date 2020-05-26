import unittest

from app import Database

class TestDatabase(unittest.TestCase):

    def setUp(self):
        data = [
            ['foo', 'bar'],
            ['biz', 'baz'],
            ['spam', 'eggs'],
            ['bar', 'foo'],
            ['bat', 'foo'],
        ]
        f = open('test_db.csv', 'w')
        f.write(
            '\n'.join(f'{key},{value}' for key, value in data)
        )
        f.close()
        self._db = Database('test_db.csv')
        super().setUp()

    def tearDown(self):
        f = open('test_db.csv', 'w')
        f.close()

    def test_get_value(self):
        value = self._db.get_value('foo')
        self.assertEqual('bar', value)

    def test_get_value_null(self):
        value = self._db.get_value('foobar')
        self.assertIsNone(value)

    def test_set_value(self):
        self._db.set_value('1', '2')
        value = self._db.get_value('1')
        self.assertEqual('2', value)

    def test_reset_value(self):
        value = self._db.get_value('foo')
        self.assertEqual('bar', value)

        self._db.set_value('foo', 'biz')
        value = self._db.get_value('foo')
        self.assertEqual('biz', value)

    def test_delete_value(self):
        value = self._db.get_value('foo')
        self.assertEqual('bar', value)

        self._db.delete('foo')
        value = self._db.get_value('foo')
        self.assertIsNone(value)

    def test_count(self):
        count = self._db.count('foo')
        self.assertEqual(2, count)

    def test_count_none(self):
        count = self._db.count('asd')
        self.assertEqual(0, count)

    def test_begin_commit(self):
        self._db.begin()
        self._db.set_value('one', 'two')
        self._db.commit()
        self.assertEqual('two', self._db.get_value('one'))

    def test_begin_rollback(self):
        self._db.begin()
        self._db.set_value('one', 'two')
        self._db.rollback()
        self.assertIsNone(self._db.get_value('one'))

    def test_begin_rollback_old_data_save(self):
        self._db.set_value('one', 'two')
        self._db.begin()
        self._db.set_value('one', 'three')
        self._db.rollback()
        self.assertEqual('two', self._db.get_value('one'))

    def test_save(self):
        self._db.set_value('four', 'five')
        self._db.save()

        new_db = Database('test_db.csv')
        self.assertEqual('five', new_db.get_value('four'))

    def test_save_inside_transaction(self):
        self._db.begin()
        self._db.set_value('four', 'five')
        self._db.save()

        new_db = Database('test_db.csv')
        self.assertIsNone(new_db.get_value('five'))

    def test_save_outside_transaction(self):
        self._db.begin()
        self._db.set_value('four', 'five')
        self._db.commit()

        new_db = Database('test_db.csv')
        self.assertEqual('five', new_db.get_value('four'))

    def test_save_outside_transaction_rollback(self):
        self._db.begin()
        self._db.set_value('four', 'five')
        self._db.rollback()

        new_db = Database('test_db.csv')
        self.assertIsNone(new_db.get_value('five'))

    def test_count_transaction_commit(self):
        count = self._db.count('foo')
        self.assertEqual(2, count)
        self._db.begin()

        self._db.delete('bar')
        count = self._db.count('foo')
        self.assertEqual(1, count)
        self._db.commit()

        count = self._db.count('foo')
        self.assertEqual(1, count)

    def test_count_transaction_rollback(self):
        count = self._db.count('foo')
        self.assertEqual(2, count)
        self._db.begin()

        self._db.set_value('biz', 'foo')
        count = self._db.count('foo')
        self.assertEqual(3, count)
        self._db.rollback()

        count = self._db.count('foo')
        self.assertEqual(2, count)

if __name__ == '__main__':
    unittest.main()
