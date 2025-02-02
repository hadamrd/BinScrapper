# BIN Database Tool

A simple and powerful tool to collect, store, and look up Bank Identification Number (BIN) data. Perfect for developers who need to work with BIN information or just want to explore the world of payment card systems.

## What's Inside

The project consists of three main parts that work together:

### 1. Scrapper that does the following tasks
Gets BIN data from online sources in two easy steps:
- First, it finds all the bank pages across different countries
- Then, go through each bank's page to get their BIN information (resumable)
Don't worry about timeouts or failures - the tool is built to handle interruptions gracefully.

### 2. Storage
Uses a simple SQLite database to keep everything organized:
- Keeps track of bank webpages and their processing status
- Stores all the BIN details like issuer, brand, type, and level
You can stop and resume the collection process anytime - no data will be lost!

### 3. CLI tool that allows to run these and do some other queries
A friendly command-line tool that lets you:
```shell
python -m bin_manager.cli.main -h

usage: main.py [-h] [--bin BIN] [--bank BANK] [--country COUNTRY] [--country-bank COUNTRY BANK] [--stats] [--check BIN] [--collect-urls] [--scrape]

BIN Database Query Tool

options:
  -h, --help                    show this help message and exit
  --bin BIN                     Find information for a specific BIN
  --bank BANK                   List all BINs for a specific bank
  --country COUNTRY             List all banks in a specific country
  --country-bank COUNTRY BANK   List all BINs for a specific bank in a specific country
  --stats                       Show database statistics
  --check BIN                   Check if a bin is correct using bin-ip-checker
  --collect-urls                Collect bank URLs for scraping
  --scrape                      Scrape BIN data from bank URLs
```

## Getting Started

1. Set up your environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows, use: .venv\Scripts\activate
```

2. Install what you need:
```bash
pip install -r requirements.txt
```

2. Run the app
```bash
python -m bin_manager.app.main
```

## If you are more of a cli guy

### Step 1: Get the Bank List
```bash
python -m bin_manager.cli.main --collect-urls
```
This creates your database and finds all the bank pages we'll need to check.

### Step 2: Get the BIN Data
```bash
python -m bin_manager.cli.main --scrape
```
This gets the actual BIN information from each bank. If something interrupts it, just run it again - it'll pick up where it left off.

## Using the Search Tool

Here's how you can find what you need:

### Look Up a BIN
```bash
python -m bin_manager.cli.main --bin 123456
```

### Find All BINs for a Bank
```bash
python -m bin_manager.cli.main --bank "HSBC"
```

### See Banks in a Country
```bash
python -m bin_manager.cli.main --country "France"
```

### Find a Bank's BINs in a Specific Country
```bash
python -m bin_manager.cli.main --country-bank "France" "BNP Paribas"
```

### See Your Database Stats
```bash
python -m bin_manager.cli.main --stats
```


## Want to Help?

Feel free to jump in! Whether you've found a bug or have an idea to make it better, we'd love to hear from you.

## License

This project is open source under the MIT License.

## Current db stats
Database Statistics:
Total BINs: 161,660
Unique Banks: 16,573
Countries: 215

Card Brand Distribution:
VISA: 74,340
MASTERCARD: 44,867
DISCOVER: 12,449
MAESTRO: 6,444
UATP: 4,099
PRIVATE LABEL: 4,071
DINERS CLUB INTERNATIONAL: 3,489
CHINA UNION PAY: 3,216
LOCAL BRAND: 2,676
AMERICAN EXPRESS: 1,828
EBT: 1,046
JCB: 558
ELO: 541
RUPAY: 261
PHH FUEL CARD: 198
CABAL: 192
WEXCARD: 187
CARNET: 181
NSPK MIR: 147
VERVE: 119
CIRRUS: 116
SBERCARD: 98
VISA/DANKORT: 96
TROY: 72
MAESTRO/BANCONTACT: 53
CMI: 38
UZCARD: 27
HUMOCARD: 26
UK FUEL CARD: 24
EFTPOS: 20
JCB/RUPAY: 19
CHJONES FUEL CARD: 15
NEWDAY: 12
DINACARD: 12
CHINA UNION PAY/UZCARD: 12
BELKART: 11
VPAY: 10
DUET: 10
GE CAPITAL: 9
TARJETA NARANJA: 8
RED FUEL CARD: 8
HIPERCARD: 8
PAYPAK: 7
FUEL CARD: 7
PROSTIR: 5
ATM CARD: 4
MEEZA: 3
VISA/BANCONTACT: 2
SODEXO: 2
MASTERCARD/BANCONTACT: 2
LOYALTY CARD: 2
CODENSA: 2
ARGENCARD: 2
TARJETA CENCOSUD: 1
RED LIQUID FUEL CARD: 1
PAYPAL: 1
OUROCARD: 1
JCB/MIR: 1
JCB/LANKAPAY: 1
JCB/CHINA UNION PAY: 1
GLOBAL BC: 1
AURA: 1