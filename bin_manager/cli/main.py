#!/usr/bin/env python3
import argparse
import sqlite3
from typing import List, Dict
import sys
from prettytable import PrettyTable

from bin_manager.cli.check_bin import BinChecker
from bin_manager.cli.collect_urls import collect_bank_urls
from bin_manager.cli.scrap_bins import scrap_bins
from bin_manager.db.database import BinDatabase

class BinCLI:
    def __init__(self, db_path: str = 'bin_database.db'):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row

    def find_bin_info(self, bin_number: str) -> Dict:
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT bin_number, pays, emetteur, marque_carte as marque, 
                   type_carte as type, niveau_carte as niveau
            FROM bin_cards 
            WHERE bin_number LIKE ?
        ''', (f"{bin_number}%",))
        results = cursor.fetchall()
        return [dict(row) for row in results]

    def list_bank_bins(self, bank_name: str) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT bin_number, pays, emetteur, marque_carte as marque, 
                   type_carte as type, niveau_carte as niveau
            FROM bin_cards 
            WHERE emetteur LIKE ?
            ORDER BY bin_number
        ''', (f"%{bank_name}%",))
        results = cursor.fetchall()
        return [dict(row) for row in results]

    def list_country_bank_bins(self, country: str, bank_name: str) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT bin_number, pays, emetteur, marque_carte as marque, 
                   type_carte as type, niveau_carte as niveau
            FROM bin_cards 
            WHERE pays LIKE ? AND emetteur LIKE ?
            ORDER BY bin_number
        ''', (f"%{country}%", f"%{bank_name}%"))
        results = cursor.fetchall()
        return [dict(row) for row in results]

    def list_country_banks(self, country: str) -> List[str]:
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT DISTINCT emetteur
            FROM bin_cards 
            WHERE pays LIKE ?
            ORDER BY emetteur
        ''', (f"%{country}%",))
        return [row[0] for row in cursor.fetchall()]

    def get_statistics(self) -> Dict:
        cursor = self.conn.cursor()
        stats = {}
        
        # Total number of BINs
        cursor.execute('SELECT COUNT(*) FROM bin_cards')
        stats['total_bins'] = cursor.fetchone()[0]
        
        # Number of unique banks
        cursor.execute('SELECT COUNT(DISTINCT emetteur) FROM bin_cards')
        stats['unique_banks'] = cursor.fetchone()[0]
        
        # Number of countries
        cursor.execute('SELECT COUNT(DISTINCT pays) FROM bin_cards')
        stats['countries'] = cursor.fetchone()[0]
        
        # Distribution by card brand
        cursor.execute('''
            SELECT marque_carte, COUNT(*) as count 
            FROM bin_cards 
            GROUP BY marque_carte 
            ORDER BY count DESC
        ''')
        stats['brand_distribution'] = dict(cursor.fetchall())
        
        return stats

    def close(self):
        self.conn.close()

def display_results(results: List[Dict], title: str = "Results"):
    if not results:
        print("No results found.")
        return

    table = PrettyTable()
    table.field_names = results[0].keys()
    for row in results:
        table.add_row(row.values())
    
    print(f"\n{title}")
    print(table)

def display_statistics(stats: Dict):
    print("\nDatabase Statistics:")
    print(f"Total BINs: {stats['total_bins']:,}")
    print(f"Unique Banks: {stats['unique_banks']:,}")
    print(f"Countries: {stats['countries']:,}")
    
    print("\nCard Brand Distribution:")
    for brand, count in stats['brand_distribution'].items():
        print(f"{brand}: {count:,}")

def main():
    parser = argparse.ArgumentParser(description='BIN Database Query Tool')
    parser.add_argument('--bin', help='Find information for a specific BIN')
    parser.add_argument('--bank', help='List all BINs for a specific bank')
    parser.add_argument('--country', help='List all banks in a specific country')
    parser.add_argument('--country-bank', nargs=2, metavar=('COUNTRY', 'BANK'),
                       help='List all BINs for a specific bank in a specific country')
    parser.add_argument('--stats', action='store_true', help='Show database statistics')
    parser.add_argument('--check', help='Check if a bin is correct using bin-ip-checker', nargs=1, metavar=('BIN'))
    parser.add_argument('--collect-urls', action='store_true', help='Collect bank URLs for scraping')
    parser.add_argument('--scrape', action='store_true', help='Scrape BIN data from bank URLs')
    parser.add_argument('--export-to-csv', help='Export BIN data to CSV', nargs=1, metavar=('FILENAME'))
    
    args = parser.parse_args()
    
    if len(sys.argv) == 1:
        parser.print_help()
        return

    cli = BinCLI()

    try:
        if args.bin:
            results = cli.find_bin_info(args.bin)
            display_results(results, f"BIN Information for {args.bin}")
        
        elif args.bank:
            results = cli.list_bank_bins(args.bank)
            display_results(results, f"BINs for bank matching '{args.bank}'")
        
        elif args.country_bank:
            country, bank = args.country_bank
            results = cli.list_country_bank_bins(country, bank)
            display_results(results, f"BINs for '{bank}' in {country}")
        
        elif args.country:
            banks = cli.list_country_banks(args.country)
            if banks:
                print(f"\nBanks in {args.country}:")
                for i, bank in enumerate(banks, 1):
                    print(f"{i}. {bank}")
            else:
                print("No banks found for this country.")
        
        elif args.stats:
            stats = cli.get_statistics()
            display_statistics(stats)
        
        elif args.check:
            BinChecker().check_bin(args.check[0])
        
        elif args.collect_urls:
            collect_bank_urls()
            
        elif args.scrape:
            scrap_bins()
        
        elif args.export_to_csv:
            db = BinDatabase()
            db.export_bins_to_csv(args.export_to_csv[0])

    finally:
        cli.close()

if __name__ == "__main__":
    main()