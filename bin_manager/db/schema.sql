-- Database schema for BIN management system

-- Table for storing bank URLs and their processing status
CREATE TABLE IF NOT EXISTS bank_urls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT UNIQUE NOT NULL,
    processed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table for storing BIN card information
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
);

-- Indexes for improved query performance
CREATE INDEX IF NOT EXISTS idx_bin_number ON bin_cards(bin_number);
CREATE INDEX IF NOT EXISTS idx_pays ON bin_cards(pays);
CREATE INDEX IF NOT EXISTS idx_emetteur ON bin_cards(emetteur);
CREATE INDEX IF NOT EXISTS idx_bank_url_processed ON bank_urls(processed);

-- Views for common queries
CREATE VIEW IF NOT EXISTS bank_stats AS
SELECT 
    emetteur,
    pays,
    COUNT(*) as bin_count,
    GROUP_CONCAT(DISTINCT marque_carte) as card_brands
FROM bin_cards
GROUP BY emetteur, pays;
