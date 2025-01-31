import sqlite3
from typing import List, Dict

class BinDatabase:
    def __init__(self, db_name: str = 'bin_database.db'):
        self.conn = sqlite3.connect(db_name)
        self.create_tables()
        
    def create_tables(self):
        cursor = self.conn.cursor()
        
        # Table for bank URLs
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS bank_urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE NOT NULL,
            processed BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Table for BIN data
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS bin_cards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bin_number TEXT NOT NULL,
            pays TEXT NOT NULL,
            emetteur TEXT NOT NULL,
            marque_carte TEXT NOT NULL,
            type_carte TEXT,
            niveau_carte TEXT,
            bank_url_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (bank_url_id) REFERENCES bank_urls(id),
            UNIQUE(bin_number, pays)
        )
        ''')
        self.conn.commit()
        
    def insert_bank_urls(self, urls: List[str]) -> None:
        cursor = self.conn.cursor()
        cursor.executemany(
            'INSERT OR IGNORE INTO bank_urls (url) VALUES (?)',
            [(url,) for url in urls]
        )
        self.conn.commit()
    
    def get_unprocessed_urls(self) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT id, url FROM bank_urls WHERE processed = FALSE')
        return [{'id': row[0], 'url': row[1]} for row in cursor.fetchall()]
    
    def mark_url_processed(self, url_id: int) -> None:
        cursor = self.conn.cursor()
        cursor.execute('UPDATE bank_urls SET processed = TRUE WHERE id = ?', (url_id,))
        self.conn.commit()
        
    def insert_bank_data(self, bank_data: List[Dict], bank_url_id: int):
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
        cursor = self.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM bank_urls')
        return cursor.fetchone()[0]

    def get_processed_urls_count(self) -> int:
        cursor = self.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM bank_urls WHERE processed = TRUE')
        return cursor.fetchone()[0]
    
    def export_bins_to_csv(self, csv_path: str) -> None:
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
        self.conn.close()
