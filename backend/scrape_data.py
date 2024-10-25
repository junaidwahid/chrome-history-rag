import sqlite3
import requests
from bs4 import BeautifulSoup
import time
from typing import List, Tuple, Optional
from dataclasses import dataclass
from contextlib import contextmanager

@dataclass
class URLMetadata:
    """Data class to store URL metadata."""
    url_id: int
    title: str
    description: str

class MetadataScraper:
    """Scrapes and stores metadata from URLs in browsing history."""
    
    def __init__(self, db_name: str = 'local_browsing_history.db', 
                 request_delay: int = 2, 
                 timeout: int = 5,
                 max_urls: Optional[int] = None):
        """
        Initialize the MetadataScraper.
        
        Args:
            db_name (str): SQLite database filename
            request_delay (int): Delay between requests in seconds
            timeout (int): Request timeout in seconds
            max_urls (Optional[int]): Maximum number of URLs to process
        """
        self.db_name = db_name
        self.request_delay = request_delay
        self.timeout = timeout
        self.max_urls = max_urls
        
    @contextmanager
    def _db_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_name)
        try:
            yield conn
        finally:
            conn.close()

    def _fetch_urls(self) -> List[Tuple[int, str]]:
        """
        Fetch URLs from the database.
        
        Returns:
            List[Tuple[int, str]]: List of (id, url) tuples
        """
        with self._db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, url FROM browsing_history")
            return cursor.fetchall()

    def _extract_metadata(self, url: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Extract metadata from a URL.
        
        Args:
            url (str): URL to scrape
            
        Returns:
            Tuple[Optional[str], Optional[str]]: Title and description
        """
        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract title
            title = soup.title.string if soup.title else None
            
            # Extract description
            meta = soup.find("meta", attrs={"name": "description"})
            description = meta.get("content") if meta else None
            
            return title or "No title found", description or "No description found"
            
        except Exception as e:
            print(f"Error processing {url}: {str(e)}")
            return None, None

    def _update_metadata(self, metadata: List[URLMetadata]) -> None:
        """
        Update database with scraped metadata.
        
        Args:
            metadata (List[URLMetadata]): List of metadata entries to update
        """
        if not metadata:
            return
            
        with self._db_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(
                """
                UPDATE browsing_history
                SET title = ?, description = ?
                WHERE id = ?
                """,
                [(m.title, m.description, m.url_id) for m in metadata]
            )
            conn.commit()

    def _ensure_description_column(self) -> None:
        """Add description column if it doesn't exist."""
        try:
            with self._db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT name FROM pragma_table_info('browsing_history') 
                    WHERE name = 'description'
                    """
                )
                if not cursor.fetchone():
                    cursor.execute(
                        "ALTER TABLE browsing_history ADD COLUMN description TEXT"
                    )
                    conn.commit()
        except sqlite3.OperationalError as e:
            print(f"Error ensuring description column: {e}")

    def process_urls(self) -> None:
        """Main method to process URLs and extract metadata."""
        try:
            self._ensure_description_column()
            urls = self._fetch_urls()
            
            if self.max_urls:
                urls = urls[:self.max_urls]
            
            metadata = []
            for url_id, url in urls:
                print(f"Processing URL: {url}")
                title, description = self._extract_metadata(url)
                
                if title and description:
                    metadata.append(URLMetadata(url_id, title, description))
                    print(f"Extracted - Title: {title[:50]}...")
                
                time.sleep(self.request_delay)
            
            self._update_metadata(metadata)
            print(f"Successfully processed {len(metadata)} URLs")
            
        except Exception as e:
            print(f"Error during processing: {e}")

def main():
    scraper = MetadataScraper(max_urls=5)  # Process first 5 URLs for testing
    scraper.process_urls()

if __name__ == "__main__":
    main()