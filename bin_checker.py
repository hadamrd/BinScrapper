import requests
import json

class BinChecker:
    def __init__(self):
        self.base_url = "https://bin-ip-checker.p.rapidapi.com"
        self.headers = {
            "x-rapidapi-key": "e0c44abb9cmshc3002bae501d16ep1ad210jsn95fc6eb89fce",
            "x-rapidapi-host": "bin-ip-checker.p.rapidapi.com",
            "Content-Type": "application/json"
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def get_info_by_bin(self, bin_number, ip="2.56.188.79"):
        response = self.session.post(f"{self.base_url}/?bin={bin_number}&ip=2.56.188.79")
        return response.json()
