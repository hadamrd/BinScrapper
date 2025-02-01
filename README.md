# BIN Database Tool

A simple and powerful tool to collect, store, and look up Bank Identification Number (BIN) data. Perfect for developers who need to work with BIN information or just want to explore the world of payment card systems.

## What's Inside

The project consists of three main parts that work together:

### 1. Data Collector
Gets BIN data from online sources in two easy steps:
- First, it finds all the bank pages across different countries
- Then, it goes through each bank's page to get their BIN information
Don't worry about timeouts or failures - the tool is built to handle interruptions gracefully.

### 2. Storage
Uses a simple SQLite database to keep everything organized:
- Keeps track of bank webpages and their processing status
- Stores all the BIN details like issuer, brand, type, and level
You can stop and resume the collection process anytime - no data will be lost!

### 3. Search Tool
A friendly command-line tool that lets you:
- Look up any BIN
- Find all BINs for a specific bank
- See which banks operate in a country
- Get insights about your BIN database

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

## Collecting the Data

### Step 1: Get the Bank List
```bash
python scrap_all_banks_urls.py
```
This creates your database and finds all the bank pages we'll need to check.

### Step 2: Get the BIN Data
```bash
python scrap_all_banks_bins.py
```
This gets the actual BIN information from each bank. If something interrupts it, just run it again - it'll pick up where it left off.

## Using the Search Tool

Here's how you can find what you need:

### Look Up a BIN
```bash
python bin_cli.py --bin 123456
```

### Find All BINs for a Bank
```bash
python bin_cli.py --bank "HSBC"
```

### See Banks in a Country
```bash
python bin_cli.py --country "France"
```

### Find a Bank's BINs in a Specific Country
```bash
python bin_cli.py --country-bank "France" "BNP Paribas"
```

### See Your Database Stats
```bash
python bin_cli.py --stats
```

## Files You'll Find
```
.
├── BinScraper.py      # Gets the data from the web
├── BinDatabase.py     # Handles data storage
├── bin_cli.py         # Search tool
├── requirements.txt   # What you need to install
└── logs/              # Keeps track of what's happening
```

## Want to Help?

Feel free to jump in! Whether you've found a bug or have an idea to make it better, we'd love to hear from you.

## License

This project is open source under the MIT License.