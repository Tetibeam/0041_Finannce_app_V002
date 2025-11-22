import unittest
import os
import io
import sys
import tempfile
import sqlite3
from app import create_app

class TestRoutesData(unittest.TestCase):
    def setUp(self):
        # Create a temporary database
        self.db_fd, self.db_path = tempfile.mkstemp()
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        
        # Initialize tables expected by the app
        self.cursor.execute("CREATE TABLE asset (date TEXT, value INTEGER)")
        self.cursor.execute("CREATE TABLE balance (date TEXT, value INTEGER)")
        self.conn.commit()
        self.conn.close()

        # Configure app to use the temp db
        self.app = create_app()
        self.app.config['DATABASE_PATH'] = os.path.dirname(self.db_path)
        self.app.config['DATABASE'] = {'finance': os.path.basename(self.db_path)}
        self.app.testing = True
        self.client = self.app.test_client()

    def tearDown(self):
        os.close(self.db_fd)
        try:
            os.remove(self.db_path)
        except OSError:
            pass

    def test_upload_update_no_files(self):
        response = self.client.post('/api/data/upload')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"No files provided", response.data)

    def test_upload_update_success(self):
        # Create dummy CSV files
        asset_csv = (io.BytesIO(b"date,value\n2023-01-01,100\n"), 'diff_asset_profit.csv')
        balance_csv = (io.BytesIO(b"date,value\n2023-01-01,200\n"), 'diff_balance.csv')

        data = {
            'file_asset': asset_csv,
            'file_balance': balance_csv
        }

        response = self.client.post(
            '/api/data/upload',
            data=data
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"success", response.data)
        
        # Verify data in DB
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT count(*) FROM asset")
        self.assertEqual(cursor.fetchone()[0], 1)
        cursor.execute("SELECT count(*) FROM balance")
        self.assertEqual(cursor.fetchone()[0], 1)
        conn.close()

if __name__ == '__main__':
    unittest.main()
