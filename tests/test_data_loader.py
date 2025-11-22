import unittest
import pandas as pd
import os
import sqlite3
import tempfile
from app.utils.data_loader import append_to_table

class TestDataLoader(unittest.TestCase):
    def setUp(self):
        # Create a temporary database
        self.db_fd, self.db_path = tempfile.mkstemp()
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.cursor.execute("CREATE TABLE test_table (col1 INTEGER, col2 TEXT)")
        self.conn.commit()
        self.conn.close()

    def tearDown(self):
        os.close(self.db_fd)
        try:
            os.remove(self.db_path)
        except OSError:
            pass

    def test_append_to_table(self):
        df = pd.DataFrame({'col1': [1, 2], 'col2': ['a', 'b']})
        # This should fail if Path is not imported
        added = append_to_table(self.db_path, df, 'test_table')
        self.assertEqual(added, 2)
        
        # Verify data
        with sqlite3.connect(self.db_path) as conn:
            df_read = pd.read_sql_query("SELECT * FROM test_table", conn)
        self.assertEqual(len(df_read), 2)

if __name__ == '__main__':
    unittest.main()
