"""Download IBM's auto insurance customer sample and write the compressed copy the analysis reads.
Only needed if data/ is empty:  python get_data.py"""
import os, pandas as pd

# public GitHub mirror of IBM Watson Analytics' "Marketing Customer Value Analysis" sample dataset
URL = ("https://raw.githubusercontent.com/nanthasnk/Customer-Lifetime-Value-Prediction/"
       "823ff329c99838bfc7da3810fef8b8201e404524/Data/AutoInsurance.csv")

def build(src=URL):
    d = pd.read_csv(src)
    os.makedirs("data", exist_ok=True)
    d.to_csv("data/auto_insurance_customers.csv.gz", index=False, compression="gzip")
    print(f"data/auto_insurance_customers.csv.gz  {len(d):,} rows")

if __name__ == "__main__":
    build()
