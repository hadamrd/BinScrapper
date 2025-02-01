import sqlite3
from typing import List, Dict
import os

class BinDatabase:
    def __init__(self, db_name: str = 'bin_database.db'):
        """Initialize database connection and ensure schema is created."""
        self.conn = sqlite3.connect(db_name)
        self._init_schema()
        
    def _init_schema(self):
        """Initialize the database schema from the SQL file."""
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        
        try:
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
                
            # Execute the schema SQL as a script
            self.conn.executescript(schema_sql)
            self.conn.commit()
        except Exception as e:
            print(f"Error initializing schema: {e}")
            raise
        
    def insert_bank_urls(self, urls: List[str]) -> None:
        """Insert new bank URLs into the database."""
        cursor = self.conn.cursor()
        cursor.executemany(
            'INSERT OR IGNORE INTO bank_urls (url) VALUES (?)',
            [(url,) for url in urls]
        )
        self.conn.commit()
    
    def get_unprocessed_urls(self) -> List[Dict]:
        """Get all unprocessed bank URLs."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT id, url FROM bank_urls WHERE processed = FALSE')
        return [{'id': row[0], 'url': row[1]} for row in cursor.fetchall()]
    
    def mark_url_processed(self, url_id: int) -> None:
        """Mark a bank URL as processed."""
        cursor = self.conn.cursor()
        cursor.execute('UPDATE bank_urls SET processed = TRUE WHERE id = ?', (url_id,))
        self.conn.commit()
        
    def insert_bank_data(self, bank_data: List[Dict], bank_url_id: int):
        """Insert or update bank BIN data."""
        cursor = self.conn.cursor()
        for row in bank_data:
            cursor.execute('''
            INSERT INTO bin_cards (
                bin_number,
                pays,
                emetteur,
                marque_carte,
                type_carte,
                niveau_carte,
                bank_url_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT (bin_number, pays) 
            DO UPDATE SET
                emetteur=excluded.emetteur,
                marque_carte=excluded.marque_carte,
                type_carte=excluded.type_carte,
                niveau_carte=excluded.niveau_carte
            ''', (
                row['Numéro BIN/IIN'],
                row['Pays'],
                row['Nom de l\'émetteur / Banque'],
                row['Marque de carte'],
                row['Type de carte'],
                row['Niveau de carte'],
                bank_url_id
            ))
        self.conn.commit()

    def get_total_urls_count(self) -> int:
        """Get the total count of bank URLs."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM bank_urls')
        return cursor.fetchone()[0]

    def get_processed_urls_count(self) -> int:
        """Get the count of processed bank URLs."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM bank_urls WHERE processed = TRUE')
        return cursor.fetchone()[0]
    
    def export_bins_to_csv(self, csv_path: str) -> None:
        """Export all BIN data to a CSV file."""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT bin_number, pays, emetteur, marque_carte, type_carte, niveau_carte 
            FROM bin_cards
        ''')
        
        import csv
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # Write headers
            writer.writerow(['BIN', 'Pays', 'Emetteur', 'Marque', 'Type', 'Niveau'])
            # Write data
            writer.writerows(cursor.fetchall())
    
    def close(self):
        """Close the database connection."""
        self.conn.close()
