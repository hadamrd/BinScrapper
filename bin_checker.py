import os
import requests

class BinChecker:
    def __init__(self):
        self.base_url = "https://bin-ip-checker.p.rapidapi.com"
        self.headers = {
            "x-rapidapi-key": os.getenv("RAPIDAPI_KEY"),
            "x-rapidapi-host": "bin-ip-checker.p.rapidapi.com",
            "Content-Type": "application/json"
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def get_info_by_bin(self, bin_number, ip="2.56.188.79"):
        response = self.session.post(f"{self.base_url}/?bin={bin_number}&ip={ip}")
        return response.json()
