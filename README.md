### Setup env and install dependencies
```
pip -m venv .venv
pip install -r requirements.txt
```

#### 1 - Run first go and fill db with list of all banks bins pages urls

```shell 
python scrap_all_banks_urls.py
```

#### 2 - Run second go and fetch one by one the bins entries for each bank

```shell 
python scrap_all_banks_bins.py
```

!!! info If the second step fails you need to rerun it again and it will resume from where it stopped last time