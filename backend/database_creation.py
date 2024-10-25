import os
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict
from pathlib import Path

class ChromeHistoryExtractor:
    """Extracts and stores Chrome browsing history."""
    
    CHROME_EPOCH = datetime(1601, 1, 1)
    DEFAULT_CHROME_PATH = "~/.config/google-chrome/Default/History"
    
    def __init__(self, output_db: str = 'local_browsing_history.db'):
        """
        Initialize the ChromeHistoryExtractor.
        
        Args:
            output_db (str): Name of the output SQLite database file
        """
        self.output_db = output_db
        self.chrome_history_path = self._get_chrome_history_path()

    def _get_chrome_history_path(self) -> Path:
        """
        Get the path to Chrome's history database.
        
        Returns:
            Path: Path to Chrome's history database
            
        Raises:
            FileNotFoundError: If Chrome history database doesn't exist
        """
        history_path = Path(os.path.expanduser(self.DEFAULT_CHROME_PATH))
        if not history_path.exists():
            raise FileNotFoundError(
                f"Chrome history database not found at {history_path}"
            )
        return history_path

    @staticmethod
    def _convert_chrome_time(chrome_timestamp: int) -> datetime:
        """
        Convert Chrome's timestamp to datetime.
        
        Args:
            chrome_timestamp (int): Chrome's microsecond timestamp
            
        Returns:
            datetime: Converted datetime object
        """
        return ChromeHistoryExtractor.CHROME_EPOCH + timedelta(microseconds=chrome_timestamp)

    def extract_history(self) -> List[Dict]:
        """
        Extract browsing history from Chrome's database.
        
        Returns:
            List[Dict]: List of browsing history entries
        """
        query = """
            SELECT urls.url, urls.title, visits.visit_time
            FROM urls, visits
            WHERE urls.id = visits.url
            ORDER BY visits.visit_time DESC
        """
        
        with sqlite3.connect(self.chrome_history_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            results = cursor.fetchall()

        return [
            {
                'url': url,
                'title': title,
                'visit_time': self._convert_chrome_time(visit_time)
            }
            for url, title, visit_time in results
        ]

    def store_history(self, history_data: List[Dict]) -> None:
        """
        Store browsing history in a local SQLite database.
        
        Args:
            history_data (List[Dict]): List of history entries to store
        """
        create_table_query = """
            CREATE TABLE IF NOT EXISTS browsing_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                title TEXT,
                visit_time TEXT
            )
        """
        
        insert_query = """
            INSERT INTO browsing_history (url, title, visit_time)
            VALUES (?, ?, ?)
        """
        
        with sqlite3.connect(self.output_db) as conn:
            cursor = conn.cursor()
            cursor.execute(create_table_query)
            
            history_entries = [
                (
                    entry['url'],
                    entry['title'],
                    entry['visit_time'].strftime("%Y-%m-%d %H:%M:%S")
                )
                for entry in history_data
            ]
            
            cursor.executemany(insert_query, history_entries)
            conn.commit()
            
        print(f"Stored {len(history_data)} entries in {self.output_db}")

    def process(self) -> None:
        """Extract and store Chrome history in one operation."""
        try:
            history = self.extract_history()
            self.store_history(history)
        except sqlite3.Error as e:
            print(f"Database error occurred: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")

def main():
    extractor = ChromeHistoryExtractor()
    extractor.process()

if __name__ == "__main__":
    main()