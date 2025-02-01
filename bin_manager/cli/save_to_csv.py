from bin_manager.db.database import BinDatabase

db = BinDatabase()
db.export_bins_to_csv('bins.csv')
